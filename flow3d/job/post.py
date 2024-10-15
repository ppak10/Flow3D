import copy
import multiprocessing
import numpy as np
import os
import pandas as pd
import shutil
import subprocess
import textwrap
import zipfile

from flow3d import data
from importlib.resources import files
from tqdm import tqdm

from .utils import JobUtils

class JobPost():

    def run_post_process(self, num_proc = 1):
        """
        Runs post processing method with or without multiprocessing.
        """
        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(sorted(self.simulations)):
                    pool.apply_async(
                        self.post_process,
                        args=(simulation, ),
                        error_callback=self.error_callback
                    )
                pool.close()
                pool.join()
                
        else:
            for simulation in tqdm(sorted(self.simulations)):
                self.post_process(simulation)

    def post_process(self, simulation):
        print(f"""\n
################################################################################
Post Process: `{simulation.name}`
################################################################################
""")
        s_dir_path = os.path.join(self.job_dir_path, simulation.name)
        simulation_status = simulation.check_status(s_dir_path)

        if simulation_status["run_simulation_completed"]:
            if not simulation_status["post_process_create_flslnk_completed"]:
                print(f"Creating `flslnk.tmp` file for {simulation.name}...")
                self.create_flslnk(simulation, working_dir=simulation.name)

            if not simulation_status["post_process_create_chunks_completed"]:
                print(f"Processing `flslnk.tmp` into chunks for {simulation.name}...")
                self.create_chunks(simulation, working_dir=simulation.name)

            simulation_status = simulation.check_status(s_dir_path)
            if not simulation_status["post_process_create_npz_completed"]:
                print(f"Creating `.npz` files {simulation.name}...")
                self.create_npz(simulation, zip_output=False)
        else:
            print(f"{simulation.name} not completed, skipping")

    @JobUtils.change_working_directory
    @JobUtils.run_subprocess
    def create_flslnk(
        self,
        simulation,
        delete_output = True,
        zip_output = True,
        **kwargs,
    ):
        """
        Create `flslnk` file.

        @param simulation: Simulation
        @param delete_output: Deletes raw output `flsgrf.simulation` file -> True
        @param zip_output: Zips `flsgrf.simulation` file -> True

        @param working_dir: Sets working directory to `simulation.name`.
        """
        # Create `flsinp.simulation` file for simulation.
        resource_file_path = os.path.join("flsinp", "default.txt")
        resource = files(data).joinpath(resource_file_path)

        with resource.open() as f:
            flsinp = f.read()

            if self.verbose:
                print(textwrap(f"""
                flsinp.simulation file content:
                {flsinp}
                """))

            # TODO: Implement more options for flsinp
            with open("flsinp.simulation", "w") as f:
                # Overwrites existing flsinp with default one
                # Allows for post processing to actually work.
                f.write(flsinp)

        # Unzip flsgrf.zip file to flsgrf.simulation
        print("Unzipping `flsgrf.zip` file...")
        with zipfile.ZipFile("flsgrf.zip") as zip_ref:
            file_name = zip_ref.namelist()[0] # should be `flsgrf.simulation`

            # Open the file inside the zip archive
            with zip_ref.open(file_name) as source_file:
                # Open the destination file in write mode
                with open("flsgrf.simulation", 'wb') as dest_file:
                    # Write the contents of the source file to the destination file
                    dest_file.write(source_file.read())

        # Run subprocess for creating flslnk.tmp file. 
        print("Creating `flslnk.tmp` file...")
        process = subprocess.run(
            ["guipost", "-3", "flsgrf.simulation", "flsinp.simulation"],
            stderr=subprocess.PIPE
        )

        with open("guipost_returncode.txt", "a") as f:
            # Log returncode to txt file
            f.write(f"{process.returncode}")

        # Zip output files
        if zip_output:
            print("Zipping `flslnk.tmp` file")
            flslnk_zip = zipfile.ZipFile("flslnk.zip", "w", zipfile.ZIP_DEFLATED)
            flslnk_zip.write("flslnk.tmp")
            flslnk_zip.close()

        # Remove Large Files
        if delete_output:
            os.remove("flsgrf.simulation")
            os.remove("flslnk.tmp")

        return simulation

    @JobUtils.change_working_directory
    def create_chunks(
        self,
        simulation,
        delete_output = True,
        zip_output = True,
        **kwargs,
    ):
        # Create directory for chunks
        chunk_dir_path = "chunks"
        if not os.path.exists(chunk_dir_path):
            os.makedirs(chunk_dir_path)
        
        chunk = []
        chunk_index = 0

        # Maximum number of zeros padded in front of chunk number
        # i.e. 000000000001.txt
        chunk_zfill = 12

        if not os.path.exists("flslnk.tmp") and os.path.exists("flslnk.zip"):
            # Unzip flsgrf.zip file to flsgrf.simulation
            print("Unzipping `flslnk.zip` file...")
            with zipfile.ZipFile("flslnk.zip") as zip_ref:
                file_name = zip_ref.namelist()[0] # should be `flsgrf.simulation`

                # Open the file inside the zip archive
                with zip_ref.open(file_name) as source_file:
                    # Open the destination file in write mode
                    with open("flslnk.tmp", 'wb') as dest_file:
                        # Write the contents of the source file to the destination file
                        dest_file.write(source_file.read())


        with open("flslnk.tmp", "r") as f:
            for line in tqdm(f):
                # Splits chunks based on empty line
                if line.strip():
                    chunk.append(line)
                else:
                    if len(chunk):
                        # Fills in the remaining values with 0 to sort properly.
                        # Accounts for up to 8 digit values.
                        output_file = f"{chunk_index}.txt".zfill(chunk_zfill)
                        output_path = os.path.join(chunk_dir_path, output_file)
                        with open(output_path, "w") as out_f:
                            out_f.writelines(chunk)
                        chunk_index += 1
                        chunk = []

            # Write the last chunk
            if chunk:
                output_file = f"{chunk_index}.txt".zfill(chunk_zfill)
                output_path = os.path.join(chunk_dir_path, output_file)
                with open(output_path, 'w') as out_f:
                    out_f.writelines(chunk)

        if zip_output:
            print("Zipping `chunks` folder...")
            shutil.make_archive(chunk_dir_path, "zip", chunk_dir_path)

        if delete_output:
            print("Deleting `chunks` folder and `flslnk.tmp`")
            shutil.rmtree(chunk_dir_path)
            os.remove("flslnk.tmp")

        return simulation
    
    def create_npz(
        self,
        simulation,
        delete_output = True,
        zip_output = True,
        **kwargs,
    ):
        chunk_dir_path = os.path.join(self.job_dir_path, simulation.name, "chunks")
        chunk_zip_path = os.path.join(self.job_dir_path, simulation.name, "chunks.zip")

        # Unzip chunks if already zipped
        if not os.path.exists(chunk_dir_path):
            if os.path.exists(chunk_zip_path):
                os.makedirs(chunk_dir_path)
                with zipfile.ZipFile(chunk_zip_path, "r") as zip_ref:
                    zip_ref.extractall(chunk_dir_path)
            else:
                raise FileNotFoundError(f"`chunks.zip` file not found: {chunk_zip_path}")

        # Create folder for npz files
        npz_dir_path = os.path.join(self.job_dir_path, simulation.name, "npz") 
        if not os.path.exists(npz_dir_path):
            os.makedirs(npz_dir_path)

        # Skips 0th chunk with metadata
        chunk_data_listdir = sorted(os.listdir(chunk_dir_path))[1:-1]

        # dataset = None

        # Write chunks to txt file
        for chunk_file in tqdm(chunk_data_listdir):
            # Pulls column headers from the 9th line in each file
            chunk_file_path = os.path.join(chunk_dir_path, chunk_file)

            # Parses header text in values.
            #  printing tn, scl4 and nfs       t=5.52563142E-06  ix=2 to  127   jy=2 to  32  kz=2 to  33 
            # 2        2      5.526E-06      5.526E-06        2      127        2       32        2       33
            metadata_df = pd.read_csv(chunk_file_path, skiprows = 2, nrows=1, sep="\s+", header=None)
            # print(metadata_df)
            t_series = metadata_df.iloc[:, 3]
            t = float(t_series.iloc[0])
            # ix = metadata_df.iloc[:, 4:5]
            # jy = metadata_df.iloc[:, 6:7]
            # kz = metadata_df.iloc[:, 8:9]
            # print(t, ix, jy, kz)

            data_df = pd.read_csv(chunk_file_path, skiprows = 3, sep="\s+", dtype=float)
            data_df["t"] = t
            # data_df["ix"] = ix
            # data_df["jy"] = jy
            # data_df["kz"] = kz
            # print(data_df.columns)

            keys = {
                'p': 'pressure',
                'tn':"temperature",
                'f' : "fraction_of_fluid",
                'rho':"density",
                'scl4':"melt_region",
                'scl5':"temperature_gradient",
                'scl6':'dtdx',
                'scl7':'dtdy',
                'scl8':'dtdz',
                'u':'vx',
                'v':'vy',
                'w':'vz',
                'nfs': 'liquid_label'
            }
            data_renamed_df = data_df.rename(columns=keys)

            numpy_arrays_dict = self.df_to_numpy(data_renamed_df)
            # print(numpy_arrays_dict)

            row_dict = {
                **numpy_arrays_dict,
                "power": [simulation.power],
                "velocity": [float(simulation.velocity)],
                "timestep": [t],
            }

            npz_file_path = os.path.join(npz_dir_path, chunk_file)
            np.savez_compressed(npz_file_path, **row_dict)

        # Generate mesh_x_y_z while here as well
        # TODO: Make this into it's own method
        mesh_x_y_z_path = os.path.join(self.job_dir_path, simulation.name, "mesh_x_y_z.npz") 
        mesh_x_y_z = row_dict["x_y_z"][0]
        mesh_x_y_z_shape = np.array(mesh_x_y_z).shape

        mesh_z_length = mesh_x_y_z_shape[0]
        mesh_y_length = mesh_x_y_z_shape[1]
        mesh_x_length = mesh_x_y_z_shape[2]

        mesh_z = []
        mesh_y = []
        mesh_x = []

        for mesh_z_index in range(mesh_z_length):
            mesh_z.append(mesh_x_y_z[mesh_z_index][0][0][2])

        for mesh_y_index in range(mesh_y_length):
            mesh_y.append(mesh_x_y_z[0][mesh_y_index][0][1])

        for mesh_x_index in range(mesh_x_length):
            mesh_x.append(mesh_x_y_z[0][0][mesh_x_index][0])

        np.savez(mesh_x_y_z_path, x=mesh_x, y=mesh_y, z=mesh_z)

        if zip_output:
            print("Zipping `npz` folder...")
            shutil.make_archive(npz_dir_path, "zip", npz_dir_path)

        if delete_output:
            print("Deleting `chunks` and `npz` folder")
            shutil.rmtree(chunk_dir_path)
            # shutil.rmtree(npz_dir_path)
        
        return simulation

    # TODO: Clean this up
    def df_to_numpy(self, df):
        dtdx_dtdy_dtdz_timestep = []
        dtdx_dtdy_dtdz_z = []
        dtdx_dtdy_dtdz_y = []

        x_y_z_timestep = []
        x_y_z_z = []
        x_y_z_y = []

        vx_vy_vz_timestep = []
        vx_vy_vz_z = []
        vx_vy_vz_y = []

        keys = ["pressure", "temperature", "melt_region", "temperature_gradient", "liquid_label", "fraction_of_fluid"]

        values = {
            "timestep": [],
            "z": [],
            "y": [],
        }

        key_values = {}
        for key in keys:
            key_values[key] = copy.deepcopy(values)

        prev_z = None
        prev_y = None

        for i in range(len(df)):
            row = df.iloc[i]

            z, y = row["z"], row["y"]

            if y != prev_y and prev_y is not None:

                dtdx_dtdy_dtdz_z.append(dtdx_dtdy_dtdz_y)
                dtdx_dtdy_dtdz_y = []

                x_y_z_z.append(x_y_z_y)
                x_y_z_y = []

                vx_vy_vz_z.append(vx_vy_vz_y)
                vx_vy_vz_y = []

                for key in keys:
                    # print(key, key_values[key]["y"])
                    key_values[key]["z"].append(key_values[key]["y"])
                    key_values[key]["y"] = []

            if z != prev_z and prev_z is not None:

                dtdx_dtdy_dtdz_timestep.append(dtdx_dtdy_dtdz_z)
                dtdx_dtdy_dtdz_z = []

                x_y_z_timestep.append(x_y_z_z)
                x_y_z_z = []

                vx_vy_vz_timestep.append(vx_vy_vz_z)
                vx_vy_vz_z = []

                for key in keys:
                    # print(key, len(key_values[key]["z"]))
                    key_values[key]["timestep"].append(key_values[key]["z"])
                    key_values[key]["z"] = []

            dtdx_dtdy_dtdz_y.append([row["dtdx"], row["dtdy"], row["dtdz"]])
            x_y_z_y.append([row["x"], row["y"], row["z"]])
            vx_vy_vz_y.append([row["vx"], row["vy"], row["vz"]])

            for key in keys:
                key_values[key]["y"].append(row[key])

            prev_z = z
            prev_y = y

        # Adds last value
        dtdx_dtdy_dtdz_y.append([row["dtdx"], row["dtdy"], row["dtdz"]])
        x_y_z_y.append([row["x"], row["y"], row["z"]])
        vx_vy_vz_y.append([row["vx"], row["vy"], row["vz"]])
        dtdx_dtdy_dtdz_z.append(dtdx_dtdy_dtdz_y)

        x_y_z_z.append(x_y_z_y)
        vx_vy_vz_z.append(vx_vy_vz_y)

        for key in keys:
            key_values[key]["y"].append(row[key])
            key_values[key]["z"].append(key_values[key]["y"])


        timestep = {} 
        for key in keys:
            timestep[key] = [np.array(key_values[key]["timestep"])]

        other = {
            "dtdx_dtdy_dtdz": [np.array(dtdx_dtdy_dtdz_timestep)],
            "x_y_z": [np.array(x_y_z_timestep)],
            "vx_vy_vz": [np.array(vx_vy_vz_timestep)],
        }

        return {
            **timestep,
            **other,
        }
