import multiprocessing
import os

from tqdm import tqdm

from flow3d.workspace.utils import WorkspaceUtils

#TODO: There may be a better way to handle the naming convention here
#TODO: Rename file to `post_process` so that it matches the rest of the
# files which are verbs.
class WorkspaceSimulationPost:
    """
    Workspace class providing methods to run post processing methods for
    simulation(s).
    """

    @WorkspaceUtils.with_simulations
    def post_all_run_guipost(self, num_proc = 1, skip_checks = False, **kwargs):
        """
        Method to run guipost for simulations within a job folder.

        @param num_proc: Number of processes to use.
        """

        simulations = kwargs["simulations"]

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(self.workspace_path, simulation.name)
                    pool.apply_async(
                        simulation.guipost,
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
                simulation.guipost(working_dir = s_dir_path, **kwargs)

    @WorkspaceUtils.with_simulations
    def post_all_flslnk_to_chunks(self, num_proc = 1, skip_checks = False, **kwargs):
        """
        Method to run chunk flslnk for simulations within a job folder.

        @param num_proc: Number of processes to use.
        """

        simulations = kwargs["simulations"]

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(self.workspace_path, simulation.name)
                    pool.apply_async(
                        simulation.chunk_flslnk,
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
                simulation.chunk_flslnk(working_dir = s_dir_path, **kwargs)

    @WorkspaceUtils.with_simulations
    def post_all_flslnk_chunks_to_npz(self, num_proc = 1, skip_checks = False, **kwargs):
        """
        Method to convert flslnk chunks into npz for simulations within a job folder.

        @param num_proc: Number of processes to use.
        """

        simulations = kwargs["simulations"]

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(self.workspace_path, simulation.name)
                    pool.apply_async(
                        simulation.flslnk_chunk_to_npz,
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
                simulation.flslnk_chunk_to_npz(working_dir = s_dir_path, **kwargs)