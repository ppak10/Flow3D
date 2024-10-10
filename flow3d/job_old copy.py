import multiprocessing
import numpy as np
import os
import copy
import pandas as pd
import subprocess
import shutil
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


    def dataset_format_and_upload(
        self,
        simulation,
        dataset_id,
        delete_output = True,
    ):
        chunk_dir_path = os.path.join(self.dir_path, simulation.name, "chunks")
        chunk_zip_path = os.path.join(self.dir_path, simulation.name, "chunks.zip")

        if not os.path.exists(chunk_dir_path):
            if os.path.exists(chunk_zip_path):
                os.makedirs(chunk_dir_path)
                with zipfile.ZipFile(chunk_zip_path, "r") as zip_ref:
                    zip_ref.extractall(chunk_dir_path)
            else:
                raise FileNotFoundError(f"`chunks.zip` file not found: {chunk_zip_path}")

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

        if delete_output:
            print("Deleting `chunks` folder")
            shutil.rmtree(chunk_dir_path)

    # def huggingface_dataset_upload_raw(self):

