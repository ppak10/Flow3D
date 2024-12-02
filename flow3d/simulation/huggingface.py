import numpy as np
import os
import shutil
import zipfile

from datasets import concatenate_datasets, Dataset, load_from_disk
from huggingface_hub import HfApi
from tqdm import tqdm

from flow3d.simulation.utils.decorators import SimulationUtilsDecorators

hf_api = HfApi()

class SimulationHuggingFace():
    """
    Runs methods for huggingface related calls
    """

    @SimulationUtilsDecorators.change_working_directory 
    def create_flslnk_dataset(
        self,
        npz_dir_path = "flslnk_npz",
        dataset_path = "flslnk_dataset",
        delete_output = True,
        delete_source = True,
        zip_output = True,
        **kwargs
    ):
        # Unzip npz files
        if not os.path.exists(npz_dir_path):
            if os.path.exists(f"{npz_dir_path}.zip"):
                os.makedirs(npz_dir_path)
                with zipfile.ZipFile(f"{npz_dir_path}.zip", "r") as zip_ref:
                    zip_ref.extractall(npz_dir_path)
            else:
                raise FileNotFoundError(f"`{npz_dir_path}.zip` file not found")

        # Generate and concatenate datasets.
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

        dataset.save_to_disk(dataset_path)

        if zip_output:
            print(f"Zipping `{dataset_path}` folder...")
            shutil.make_archive(dataset_path, "zip", dataset_path)

        if delete_source:
            print(f"Deleting `{npz_dir_path}` source folder")
            shutil.rmtree(npz_dir_path)

        if delete_output:
            print(f"Deleting `{dataset_path}` output folder")
            shutil.rmtree(dataset_path)

        return dataset
    
    @SimulationUtilsDecorators.change_working_directory 
    def upload_flslnk_dataset(
        self,

        # `dataset.push_to_hub`
        dataset_id,
        config_name = None,
        split = None,

        # `load_from_disk`
        dataset_path = "flslnk_dataset",
        keep_in_memory = None,

        delete_source = True,
        **kwargs
    ):

        # Unzip dataset files
        if not os.path.exists(dataset_path):
            if os.path.exists(f"{dataset_path}.zip"):
                os.makedirs(dataset_path)
                with zipfile.ZipFile(f"{dataset_path}.zip", "r") as zip_ref:
                    zip_ref.extractall(dataset_path)
            else:
                raise FileNotFoundError(f"`{dataset_path}.zip` file not found")

        # Load dataset from disk
        dataset = load_from_disk(dataset_path, keep_in_memory=keep_in_memory)

        # Create Huggingface Dataset (if non-existant)
        repo_exists = hf_api.repo_exists(repo_id = dataset_id, repo_type="dataset")

        if repo_exists:
            # TODO: Figure out if `delete_existing` should be implemented here.
            # if delete_existing:
            #     # Delete existing repo on HuggingFace
            #     try:
            #         hf_api.delete_repo(repo_id, repo_type=repo_type)
            #     except Exception as e:
            #         # It is possible that this error occurs when repo is renamed.
            #         print(e)
            # else:
            #     return "repo exists"
            pass
        
        else:
            repo_url = hf_api.create_repo(
                repo_id = dataset_id,
                repo_type = "dataset",
                # private=private
            )
            print(f"Created new dataset at: {repo_url}")

        if config_name is None:
            config_name = self.name

        if split is None:
            split = self.filename

        dataset.push_to_hub(
            dataset_id,
            config_name = config_name,
            split = split,
        )

        if delete_source:
            print(f"Deleting `{dataset_path}` source folder")
            shutil.rmtree(dataset_path)

    @SimulationUtilsDecorators.change_working_directory 
    def upload_flslnk_dataset(
        self,

        # `dataset.push_to_hub`
        dataset_id,
        config_name = None,
        split = None,

        # `load_from_disk`
        dataset_path = "flslnk_dataset",
        keep_in_memory = None,

        delete_source = True,
        **kwargs
    ):

        # Unzip dataset files
        if not os.path.exists(dataset_path):
            if os.path.exists(f"{dataset_path}.zip"):
                os.makedirs(dataset_path)
                with zipfile.ZipFile(f"{dataset_path}.zip", "r") as zip_ref:
                    zip_ref.extractall(dataset_path)
            else:
                raise FileNotFoundError(f"`{dataset_path}.zip` file not found")

        # Load dataset from disk
        dataset = load_from_disk(dataset_path, keep_in_memory=keep_in_memory)

        # Create Huggingface Dataset (if non-existant)
        repo_exists = hf_api.repo_exists(repo_id = dataset_id, repo_type="dataset")

        if repo_exists:
            # TODO: Figure out if `delete_existing` should be implemented here.
            # if delete_existing:
            #     # Delete existing repo on HuggingFace
            #     try:
            #         hf_api.delete_repo(repo_id, repo_type=repo_type)
            #     except Exception as e:
            #         # It is possible that this error occurs when repo is renamed.
            #         print(e)
            # else:
            #     return "repo exists"
            pass
        
        else:
            repo_url = hf_api.create_repo(
                repo_id = dataset_id,
                repo_type = "dataset",
                # private=private
            )
            print(f"Created new dataset at: {repo_url}")

        if config_name is None:
            config_name = self.name

        if split is None:
            split = self.filename

        dataset.push_to_hub(
            dataset_id,
            config_name = config_name,
            split = split,
        )

        if delete_source:
            print(f"Deleting `{dataset_path}` source folder")
            shutil.rmtree(dataset_path)
