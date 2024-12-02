import copy
import numpy as np
import os
import pandas as pd
import shutil
import subprocess
import textwrap

from flow3d import data
from importlib.resources import files
from tqdm import tqdm

from flow3d.simulation.utils.decorators import SimulationUtilsDecorators

class SimulationPostProcessing():
    """
    Run methods file for simulation class.
    """

    @SimulationUtilsDecorators.change_working_directory
    def guipost(
        self,
        delete_output = True,
        delete_source = True,
        zip_output = True,
        **kwargs
    ):
        """
        Creates and zips `flslnk.tmp` file.

        @param simulation: Simulation
        @param delete_output: Deletes raw output `flsgrf.simulation` file -> True
        @param zip_output: Zips `flsgrf.simulation` file -> True

        @param working_dir: Sets working directory to `simulation.name`.
        """

        # Create `flsinp.simulation` file for simulation.
        resource_file_path = os.path.join("simulation", "flsinp", "default.txt")
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
        if not os.path.exists("flsgrf.simulation"):
            self.unzip_file("flsgrf.zip", "flsgrf.simulation")

        # Run subprocess for creating flslnk.tmp file. 
        print("Creating `flslnk.tmp` file...")
        process = subprocess.run(
            ["guipost", "-3", "flsgrf.simulation", "flsinp.simulation"],
            stderr=subprocess.PIPE
        )

        # Log returncode to txt file
        with open("guipost_returncode.txt", "a") as f:
            f.write(f"{process.returncode}")

        # Zip output files
        if zip_output:
            self.zip_file("flslnk.tmp", "flslnk.zip")

        # Remove output file
        if delete_output:
            print("Deleting `flslnk.tmp` output...")
            os.remove("flslnk.tmp")

        # Remove source file
        if delete_source:
            print("Deleting `flsgrf.simulation` source...")
            os.remove("flsgrf.simulation")

        return self

    # TODO: Does not necessary need to change working directory.
    @SimulationUtilsDecorators.change_working_directory
    def chunk_flslnk(
        self,
        chunk_dir_path = "flslnk_chunks",
        delete_output = True,
        delete_source = True,
        zip_output = True,
        **kwargs,
    ):
        # Create directory for chunks
        if not os.path.exists(chunk_dir_path):
            os.makedirs(chunk_dir_path)
        
        chunk = []
        chunk_index = 0

        # Maximum number of zeros padded in front of chunk number
        # i.e. 000000000001.txt
        chunk_zfill = 12

        # Unzip flslnk.zip file to flslnk.tmp if not already done.
        if not os.path.exists("flslnk.tmp") and os.path.exists("flslnk.zip"):
            self.unzip_file("flslnk.zip", "flslnk.tmp")

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
            print(f"Zipping `{chunk_dir_path}` folder...")
            shutil.make_archive(chunk_dir_path, "zip", chunk_dir_path)

        if delete_output:
            print(f"Deleting `{chunk_dir_path}` folder output...")
            shutil.rmtree(chunk_dir_path)

        if delete_source:
            print("Deleting `flslnk.tmp` source...")
            os.remove("flslnk.tmp")

        return self
    
    # TODO: Does not necessary need to change working directory.
    # TODO: Make method that does this multiprocessing per chunk rather than by
    # simulation
    @SimulationUtilsDecorators.change_working_directory
    def flslnk_chunk_to_npz(
        self,
        chunk_dir_path = "flslnk_chunks",
        npz_dir_path = "flslnk_npz",
        delete_output = True,
        delete_source = True,
        zip_output = True,
        **kwargs,
    ):
        # Unzip chunks
        self.unzip_folder(f"{chunk_dir_path}.zip", chunk_dir_path)

        # Create folder for npz files
        # npz_dir_path = os.path.join(self.job_dir_path, simulation.name, "npz") 
        if not os.path.exists(npz_dir_path):
            os.makedirs(npz_dir_path)

        # Skips 0th chunk with metadata
        chunk_data_listdir = sorted(os.listdir(chunk_dir_path))[1:-1]

        # Write chunks to txt file
        for chunk_file in tqdm(chunk_data_listdir):
            # Pulls column headers from the 9th line in each file
            chunk_file_path = os.path.join(chunk_dir_path, chunk_file)

            # Parses header text in values.
            #  printing tn, scl4 and nfs       t=5.52563142E-06  ix=2 to  127   jy=2 to  32  kz=2 to  33 
            # 2        2      5.526E-06      5.526E-06        2      127        2       32        2       33
            metadata_df = pd.read_csv(chunk_file_path, skiprows = 2, nrows=1, sep="\s+", header=None)

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
                "power": [self.power],
                "velocity": [float(self.velocity)],
                "timestep": [t],
            }

            # Removes the `.txt` from chunk file name before saving as `.npz`.
            chunk_file_name = chunk_file.split(".")[0]

            npz_file_path = os.path.join(npz_dir_path, chunk_file_name)
            np.savez_compressed(npz_file_path, **row_dict)

        if zip_output:
            print(f"Zipping `{npz_dir_path}` folder...")
            shutil.make_archive(npz_dir_path, "zip", npz_dir_path)

        if delete_source:
            print(f"Deleting `{chunk_dir_path}` source folder")
            shutil.rmtree(chunk_dir_path)

        if delete_output:
            print(f"Deleting `{npz_dir_path}` output folder")
            shutil.rmtree(npz_dir_path)
        
        return self

    # TODO: Clean this up
    # @staticmethod
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
