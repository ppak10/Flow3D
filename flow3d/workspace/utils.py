import os
import pickle

from pathlib import Path

class WorkspaceUtils():
    
    def with_simulations(func):
        """
        Decorator for sorting and retrieving simulations within workspace.
        """

        def wrapper(self, *args, **kwargs):

            # Only consider directories and skip over possible files.
            simulation_folders = sorted([
                s.name for s in Path(self.workspace_path).iterdir() if s.is_dir()
            ])

            if self.verbose:
                print(f"Simulation Folders ({len(simulation_folders)}): {simulation_folders}")

            # Load simulations
            simulations = []
            for simulation_folder in simulation_folders:

                # Load simulation object 
                s_dir_path = os.path.join(self.workspace_path, simulation_folder)
                s_pkl_path = os.path.join(s_dir_path, f"simulation.pkl")
                with open(s_pkl_path, "rb") as file:
                    simulation = pickle.load(file)
                    simulations.append(simulation)

            kwargs = {
                "simulations": simulations,
                **kwargs,
            }

            # Run method 
            output = func(self, *args, **kwargs)

            return output

        return wrapper