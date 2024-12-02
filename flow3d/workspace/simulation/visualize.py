import multiprocessing
import os

from tqdm import tqdm

from flow3d.workspace.utils import WorkspaceUtils

#TODO: There may be a better way to handle the naming convention here
class WorkspaceSimulationVisualize:
    """
    Workspace class providing methods to visualize simulations. 
    """

    @WorkspaceUtils.with_simulations
    def visualize_all_prepare_view_visualizations(self, num_proc = 1, skip_checks = False, **kwargs):
        """
        Method to convert prepare visualization folders and unzip flslnk npz files.

        @param num_proc: Number of processes to use.
        """

        simulations = kwargs["simulations"]

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(self.workspace_path, simulation.name)
                    pool.apply_async(
                        simulation.prepare_view_visualizations,
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
                simulation.prepare_view_visualizations(working_dir = s_dir_path, **kwargs)

    @WorkspaceUtils.with_simulations
    def visualize_all_generate_views_visualizations(
            self,
            num_proc = 1,
            skip_checks = False,
            views = ["isometric", "cross_section_xy", "cross_section_xz", "cross_section_yz"],
            **kwargs
        ):
        """
        Method to convert flslnk chunks into npz for simulations within a job folder.

        @param job_name: Name of existing Job
        @param num_proc: Number of processes to use.
        """

        simulations = kwargs["simulations"]

        for simulation in tqdm(simulations):
            s_dir_path = os.path.join(self.workspace_path, simulation.name)
            simulation.generate_views_visualizations(
                views = views,
                num_proc = num_proc,
                working_dir = s_dir_path,
                **kwargs
            )