import multiprocessing
import numpy as np
import os
import shutil
import time
import zipfile

from datasets import concatenate_datasets, Dataset
from tqdm import tqdm


from flow3d.huggingface import HuggingFace

class JobHuggingface():
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
                    pool.apply_async(
                        self.dataset_create,
                        args=(simulation, dataset_id,),
                        error_callback=self.error_callback
                    )
                
                pool.close()
                pool.join()

        else:
            for simulation in tqdm(self.simulations):
                self.dataset_create(simulation, dataset_id)

    def upload_huggingface_dataset_files(self, dataset_id, num_proc = 1, sleep_time_between_uploads = 30):
        """
        Uploads all local dataset files to huggingface.

        @param dataset_id: Huggingface dataset identifier.
        @param num_proc: Stick with 1 process to prevent rate limiting for now.
        @param sleep_time_between_uploads: 30 seconds for rate limiting.
        """

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(self.simulations):
                    folder_path = os.path.join(self.job_dir_path, simulation.name)
                    path_in_repo = simulation.name
                    upload_url = pool.apply_async(
                        HuggingFace.upload_folder,
                        args=(dataset_id, folder_path, path_in_repo),
                        error_callback=self.error_callback
                    )
                    print(f"Uploaded `{simulation.name}` at {upload_url}")
                
                pool.close()
                pool.join()

        else:
            for simulation in tqdm(self.simulations):
            # for simulation in tqdm(self.simulations[36:]):
                folder_path = os.path.join(self.job_dir_path, simulation.name)
                path_in_repo = simulation.name
                try:
                    upload_url = HuggingFace.upload_folder(dataset_id, folder_path, path_in_repo)
                    print(f"Uploaded `{simulation.name}` at {upload_url}")
                except Exception as e:
                    print(e)
                time.sleep(sleep_time_between_uploads)

    def dataset_create(
        self,
        simulation,
        dataset_id,
        delete_output = True,
    ):
        print(f"""\n
################################################################################
Create Dataset: `{dataset_id}` -> `{simulation.name}`
################################################################################
""")
        s_dir_path = os.path.join(self.job_dir_path, simulation.name)
        simulation_status = simulation.check_status(s_dir_path)

        if simulation_status["post_process_create_npz_completed"]:

            print(f"Creating Dataset {simulation.name}...")

            npz_dir_path = os.path.join(self.job_dir_path, simulation.name, "npz")
            npz_zip_path = os.path.join(self.job_dir_path, simulation.name, "npz.zip")

            if not os.path.exists(npz_dir_path):
                if os.path.exists(npz_zip_path):
                    os.makedirs(npz_dir_path)
                    with zipfile.ZipFile(npz_zip_path, "r") as zip_ref:
                        zip_ref.extractall(npz_dir_path)
                else:
                    raise FileNotFoundError(f"`npz.zip` file not found: {npz_zip_path}")

            npz_data_listdir = sorted(os.listdir(npz_dir_path))

            dataset = None

            for npz_file in tqdm(npz_data_listdir):
                npz_file_path = os.path.join(npz_dir_path, npz_file)

                row_dict = np.load(npz_file_path)

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
                print("Deleting `npz` folder")
                shutil.rmtree(npz_dir_path)

        else:
            print(f"{simulation.name} not completed, skipping")
