import multiprocessing
import os

from tqdm import tqdm

from flow3d.workspace.utils import WorkspaceUtils

class WorkspaceSimulationMeasure:
    """
    Workspace class providing methods to measure simulation results. 
    """

    @WorkspaceUtils.with_simulations
    def measure_all_prepare_melt_pool_measurements(self, num_proc = 1, skip_checks = False, **kwargs):
        """
        Method to convert prepare measurement folders and unzip flslnk npz files.

        @param num_proc: Number of processes to use.
        """

        simulations = kwargs["simulations"]

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(self.workspace_path, simulation.name)
                    pool.apply_async(
                        simulation.prepare_melt_pool_measurements,
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
                simulation.prepare_melt_pool_measurements(working_dir = s_dir_path, **kwargs)

    @WorkspaceUtils.with_simulations
    def measure_all_generate_melt_pool_measurements(
            self,
            num_proc = 1,
            skip_checks = False,
            **kwargs
        ):
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
                        simulation.generate_melt_pool_measurements,
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
                simulation.generate_melt_pool_measurements(working_dir = s_dir_path, **kwargs)