import datetime
import multiprocessing
import numpy as np
import os
import copy
import pandas as pd
import pickle
import subprocess
import time
import warnings
import zipfile

from datasets import Dataset, concatenate_datasets
from flow3d import data
from flow3d.huggingface import HuggingFace
from importlib.resources import files
from tqdm import tqdm

class Job():
    """
    Class for running and managing Flow3D simulation outputs.
    """

    @staticmethod
    def save_simulation(func):
        """
        Decorator for saving simulation instance to pickle file.
        """

        def wrapper(self, *args, **kwargs):
            simulation = func(self, *args, **kwargs)

            s_dir_path = os.path.join(self.dir_path, simulation.name)
            s_pkl_file_path = os.path.join(s_dir_path, "simulation.pkl")
            with open(s_pkl_file_path, "wb") as file:
                pickle.dump(simulation, file)
            
            return simulation

        return wrapper
    
    @staticmethod
    def run_simulation_subprocess(func):
        """
        Decorator for running simulation subprocess.
        """

        def wrapper(self, *args, **kwargs):
            simulation = args[0]

            # Change working directory to simulation folder
            previous_dir_path = os.getcwd()
            s_dir_path = os.path.join(self.dir_path, simulation.name)
            os.chdir(s_dir_path)

            # Run and time simulation
            start_time = time.time()

            # Run subprocess
            try:
                simulation = func(self, *args, **kwargs)
            except Exception as e:
                print(e)

            end_time = time.time()

            # Write duration to file.
            duration = end_time - start_time
            duration_str = str(datetime.timedelta(seconds=duration))
            with open(f"execution_times.txt", "a") as f:
                f.write(f"{func.__name__}: {duration_str}")

            # Return back to previous directory path
            os.chdir(previous_dir_path)

            # Save job.
            self.save()

            return simulation

        return wrapper


    def __init__(self, name = None, output_dir = "out"):
        self.output_dir = output_dir
        self.dir_path = None
        self.simulations = []

        if name is None:
            # Sets `job_name` to approximate timestamp.
            self.name = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.name = name

    def create_dir(self):
        """
        Creates folder to store data related to Flow3D job.

        @param output_dir: Output directory for storing jobs
        """
        self.dir_path = os.path.join(self.output_dir, self.name)

        # Creates job folder directory in output directory.
        if not os.path.isdir(self.dir_path):
            os.makedirs(self.dir_path)
        else:
            warnings.warn(f"""
Folder for job `{self.name}` already exists.
Following operations will overwrite existing files within folder.
""")

        return self.dir_path
    
    def save(self):
        """
        Saves job instance to pickle file.
        """
        job_pkl_path = os.path.join(self.dir_path, "job.pkl")
        with open(job_pkl_path, "wb") as file:
            pickle.dump(self, file)

    
    def load(self, simulation = None):
        """
        Loads simulation(s) into job folder.
        """
        # TODO: Add type checking for instance of simulation
        if isinstance(simulation, list):
            for s in simulation:
                self.load_simulation(s)
        else:
            self.load_simulation(simulation)

    @save_simulation 
    def load_simulation(self, simulation):
        """
        Creates folder in job and writes simulation prepin file.
        """
        self.simulations.append(simulation)

        # Create simulation job folder
        s_dir_path = os.path.join(self.dir_path, simulation.name)
        if not os.path.isdir(s_dir_path):
            os.makedirs(s_dir_path)

        # Creates prepin file inside simulation job folder
        s_prepin_filename = "prepin.simulation"
        s_prepin_file_path = os.path.join(s_dir_path, s_prepin_filename)

        # Write prepin file as "prepin.simulation"
        with open(s_prepin_file_path, "w") as file:
            file.write(simulation.prepin_file_content)

        self.save()
        return simulation
    
    def run(self):
        """
        Run job with parameters
        """
        for simulation in tqdm(self.simulations):
            self.run_simulation(simulation)

    @save_simulation
    @run_simulation_subprocess
    def run_simulation(
        self,
        simulation,
        delete_output = True,
        zip_output = True
    ):
        """
        Run simulation and Zip
        @param simulation: Simulation
        @param delete_output: Deletes raw output `flsgrf.simulation` file -> True
        @param zip_output: Zips `flsgrf.simulation` file -> True
        """

        if os.path.isfile("runhyd.txt"):
            print("`runhyd.txt` file exists, skipping...")
            return simulation

        print(f"Running {simulation.name}...")
        with open("runhyd.txt", "w") as f:
            process = subprocess.Popen(
                ["runhyd", "simulation"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in process.stdout:
                f.write(line)
                # if self.verbose:
                #     print(line, end="")

            process.stdout.close()
            process.wait()

        # Zip Large Files
        if zip_output:
            print("Zipping `flsgrf.simulation` file...")
            flsgrf_zip = zipfile.ZipFile("flsgrf.zip", "w", zipfile.ZIP_DEFLATED)
            flsgrf_zip.write("flsgrf.simulation")
            flsgrf_zip.close()

        # Remove Large File
        if delete_output:
            os.remove("flsgrf.simulation")

        return simulation
    
    def post_process(self):
        for simulation in tqdm(sorted(self.simulations)):
            print(f"""\n
################################################################################
Post Process: `{simulation.name}`
################################################################################
""")
            s_dir_path = os.path.join(self.dir_path, simulation.name)
            simulation_status = simulation.check_status(s_dir_path)

            # if simulation_status["completed"] \
            #     and simulation_status["run_simulation_completed"]:
            if simulation_status["run_simulation_completed"]:
                if not simulation_status["post_process_create_flslnk_completed"]:
                    print(f"Creating `flslnk.tmp` file for {simulation.name}...")
                    self.post_process_create_flslnk(simulation)

                if not simulation_status["post_process_create_chunks_completed"]:
                    print(f"Processing `flslnk.tmp` into chunks for {simulation.name}...")
                    self.post_process_create_chunks(simulation)
                # self.post_process_format_chunks(simulation)
            else:
                print(f"{simulation.name} not completed, skipping")

    @run_simulation_subprocess
    def post_process_create_flslnk(
        self,
        simulation,
        delete_unzipped = True,
        verbose = False,
    ):

        # Create `flsinp.simulation` file for simulation.
        resource_file_path = os.path.join("flsinp", "default.txt")
        resource = files(data).joinpath(resource_file_path)

        with resource.open() as f:
            flsinp = f.read()

            if verbose:
                print(f"""
flsinp.simulation file content:
{flsinp}
""")

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
        print("Zipping `flslnk.tmp` file")
        flslnk_zip = zipfile.ZipFile("flslnk.zip", "w", zipfile.ZIP_DEFLATED)
        flslnk_zip.write("flslnk.tmp")
        flslnk_zip.close()

        # Remove Large Files
        if delete_unzipped:
            os.remove("flsgrf.simulation")
            os.remove("flslnk.tmp")

        return simulation

    @run_simulation_subprocess
    def post_process_create_chunks(
        self,
        simulation,
        delete_output = True,
        zip_output = True,
    ):
        # TODO: Update to:
        # Remove raw `flslnk.tmp` file
        # Remove unzipped chunks
        # Zip Chunks

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

        return simulation
    
    def create_and_upload_huggingface_dataset(
            self,
            dataset_id,
            collection_slug,
            delete_existing = False,
            initialize_dataset = True,
            num_proc = 1,
        ):

        # Initialize Dataset on HuggingFace
        if initialize_dataset:
            h = HuggingFace()
            repo_url = h.create_repo_and_add_collection_item(
                dataset_id,
                collection_slug,
                delete_existing=delete_existing,
            )

            print(repo_url)

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(self.simulations):
                    print(f"""\n
################################################################################
Create Dataset: `{dataset_id}` -> `{simulation.name}`
################################################################################
""")
                    s_dir_path = os.path.join(self.dir_path, simulation.name)
                    simulation_status = simulation.check_status(s_dir_path)

                    # if simulation_status["completed"] and \
                    if simulation_status["run_simulation_completed"] and \
                        simulation_status["post_process_create_flslnk_completed"] and \
                        simulation_status["post_process_create_chunks_completed"]:
                        print(f"Creating Dataset {simulation.name}...")
                        pool.apply_async(self.dataset_format_and_upload, args=(simulation, dataset_id,))
                    else:
                        print(f"{simulation.name} not completed, skipping")
                
                pool.close()
                pool.join()
                print("finished")

        else:

            for simulation in tqdm(self.simulations):
                print(f"""\n
################################################################################
Create Dataset: `{dataset_id}` -> `{simulation.name}`
################################################################################
""")
                s_dir_path = os.path.join(self.dir_path, simulation.name)
                simulation_status = simulation.check_status(s_dir_path)

                if simulation_status["completed"] and \
                    simulation_status["run_simulation_completed"] and \
                    simulation_status["post_process_create_flslnk_completed"] and \
                    simulation_status["post_process_create_chunks_completed"]:
                    print(f"Creating Dataset {simulation.name}...")
                    self.dataset_format_and_upload(simulation, dataset_id)
                else:
                    print(f"{simulation.name} not completed, skipping")

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

    def dataset_format_and_upload(
        self,
        simulation,
        dataset_id,
    ):
        chunk_dir_path = os.path.join(self.dir_path, simulation.name, "chunks")

        # Skips 0th chunk with metadata
        chunk_data_listdir = sorted(os.listdir(chunk_dir_path))[1:-1]

        dataset = None

        # Write chunks to txt file
        # for chunk_file in chunk_data_listdir:
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

            time_step_dataset = Dataset.from_dict(row_dict)

            if dataset is None:
                dataset = time_step_dataset
            else:
                dataset = concatenate_datasets([dataset, time_step_dataset])

        dataset.push_to_hub(
            dataset_id,
            config_name = simulation.name,
            commit_message = simulation.name,
            split = "simulation",
        )

    # def huggingface_dataset_upload_raw(self):

