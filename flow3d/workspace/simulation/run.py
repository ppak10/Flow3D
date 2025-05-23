import os
import pickle
import time
import wandb

from pathlib import Path
from tqdm import tqdm

class WorkspaceSimulationRun:
    """
    Workspace class providing methods to run (runhyd) simulation(s).
    """

    def simulation_run(self, name, use_wandb = False, **kwargs):
        """
        Method to run one or a list simulations within a workspace folder.
        """
        simulation_folder = os.path.join(self.workspace_path, name)

        # Initialize WandB
        if use_wandb:
            wandb.login()

            wandb.init(
                project = self.wandb_project,
                config = {
                    "workspace": self.filename,
                    # "simulations": [s.name for s in self.simulations]
                }
            )

        s_dir_path = os.path.join(self.workspace_path, simulation_folder)
        s_pkl_path = os.path.join(s_dir_path, f"simulation.pkl")
        with open(s_pkl_path, "rb") as file:
            s = pickle.load(file)
            
        # Run simulation
        s.runhyd(working_dir = s_dir_path)

        # TODO: Implement better logging here.
        if use_wandb:
            wandb.log({
                "name": s.name,
                "time": time.time()
            })

        if use_wandb:
            wandb.finish()

        pass

    def simulation_run_all(self, name, num_proc=1, use_wandb = False, upload = False, **kwargs):
        """
        Runs the simulation along with queuing the postprocessing and
        visualization code immediately afterwards.
        """

        self.simulation_run(name, use_wandb, **kwargs)
        self.simulation_postprocess(name)
        self.simulation_visualize(name, num_proc=num_proc)
        self.simulation_generate_dataset(name)
        if upload:
            self.simulation_upload_dataset(name)


    def simulations_run_all(self, use_wandb = False, **kwargs):
        """
        Method to run all simulations within a workspace folder.
        """

        # # Define Job path and check that it exists
        # job_dir_path = os.path.join(self.output_dir, job_name)
        # if not os.path.isdir(job_dir_path):
        #     raise Exception(f"Folder `{job_name}` not found at `{job_dir_path}`")

        # Only consider directories and skip over possible files.
        simulation_folders = sorted([s.name for s in Path(self.workspace_path).iterdir() if s.is_dir()])
        print(f"Simulation Folders ({len(simulation_folders)}): {simulation_folders}")

        # Initialize WandB
        if use_wandb:
            wandb.login()

            wandb.init(
                project = self.wandb_project,
                config = {
                    "workspace": self.filename,
                    # "simulations": [s.name for s in self.simulations]
                }
            )

        # Run simulations
        for simulation_folder in tqdm(simulation_folders):
            # Load simulation object 
            s_dir_path = os.path.join(self.workspace_path, simulation_folder)
            s_pkl_path = os.path.join(s_dir_path, f"simulation.pkl")
            # s_pkl_path = os.path.join(s_dir_path, f"{simulation_filename}.pkl")
            with open(s_pkl_path, "rb") as file:
                s = pickle.load(file)
            
            # Run simulation
            s.runhyd(working_dir = s_dir_path)

            # TODO: Implement better logging here.
            if use_wandb:
                wandb.log({
                    "name": s.name,
                    "time": time.time()
                })

        if use_wandb:
            wandb.finish()