import multiprocessing
import os
import time

from huggingface_hub import upload_folder
from tqdm import tqdm

from flow3d.workspace.utils import WorkspaceUtils

#TODO: There may be a better way to handle the naming convention here
class WorkspaceSimulationHuggingFace:
    """
    Workspace class providing methods to visualize simulations. 
    """

    @WorkspaceUtils.with_simulations
    def huggingface_all_create_flslnk_dataset(
        self,
        num_proc = 1,
        skip_checks = False,
        **kwargs,
    ):
        simulations = kwargs["simulations"]

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(self.workspace_path, simulation.name)
                    pool.apply_async(
                        simulation.create_flslnk_dataset,
                        kwds = {
                            **kwargs,
                            "working_dir": s_dir_path,
                        }
                        # TODO: Move error callback to flow3d class
                        # error_callback=self.error_callback
                    )
                pool.close()
                pool.join()
                
        else:
            for simulation in tqdm(simulations):
                s_dir_path = os.path.join(self.workspace_path, simulation.name)
                simulation.create_flslnk_dataset(working_dir = s_dir_path, **kwargs)
    
    @WorkspaceUtils.with_simulations
    def huggingface_all_upload_flslnk_dataset(
        self,
        dataset_id = None,
        num_proc = 1,
        skip_checks = False,
        **kwargs,
    ):
        simulations = kwargs["simulations"]

        if dataset_id == None:
            dataset_id = f"FLOW-3D/{self.filename}"

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(self.workspace_path, simulation.name)
                    pool.apply_async(
                        simulation.upload_flslnk_dataset,
                        args = [dataset_id],
                        kwds = {
                            **kwargs,
                            "working_dir": s_dir_path,
                        }
                        # TODO: Move error callback to flow3d class
                        # error_callback=self.error_callback
                    )
                pool.close()
                pool.join()
                
        else:
            for simulation in tqdm(simulations):
                s_dir_path = os.path.join(self.workspace_path, simulation.name)
                simulation.upload_flslnk_dataset(
                    dataset_id,
                    working_dir = s_dir_path,
                    **kwargs
                )

    # TODO: Make method to upload just the FLOW-3D metadata for cases when
    # folders such as `visualize` is updated. Thus, you don't have to upload
    # everything agian. We still want to keep this method though, just want
    # the more granular methods as well.
    @WorkspaceUtils.with_simulations
    def huggingface_all_upload_folder(
        self,
        dataset_id = None,
        sleep_time_between_uploads = 30,
        **kwargs,
    ):
        """
        Uploads all local dataset files to huggingface
        (Single process to prevent rate liminting).

        @param dataset_id: Huggingface dataset identifier.
        @param sleep_time_between_uploads: 30 seconds for rate limiting.
        """
        simulations = kwargs["simulations"]

        if dataset_id == None:
            dataset_id = f"FLOW-3D/{self.filename}"

        for simulation in tqdm(simulations):

            s_dir_path = os.path.join(self.workspace_path, simulation.name)
            try:
                upload_url = upload_folder(
                    repo_id = dataset_id,
                    folder_path = s_dir_path,
                    path_in_repo = simulation.name,
                    repo_type = "dataset"
                )
                print(f"Uploaded `{simulation.name}` at {upload_url}")
            except Exception as e:
                print(e)

            time.sleep(sleep_time_between_uploads)
