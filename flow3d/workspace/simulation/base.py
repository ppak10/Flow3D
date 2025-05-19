import os
import pickle
import shutil

from flow3d import data
from flow3d.simulation import Simulation

from importlib.resources import files

class WorkspaceSimulationBase:
    """
    Workspace class providing methods for initializing simulation folders.
    """

    def simulation_initialize(self, name, **kwargs):
        """
        Create prepin file within simulation folder for a specified workspace
        """

        simulation = Simulation(name=name, **kwargs)

        # Create simulation folder within workspace path 
        simulation_path = os.path.join(self.workspace_path, simulation.name)
        if not os.path.isdir(simulation_path):
            os.makedirs(simulation_path)

        # Copy over default `simulation.yml` file
        config_file = "default.yml"
        if name == "test":
            config_file = "test.yml"

        config_resource_file_path = os.path.join("simulation", "config", config_file)
        config_resource = files(data).joinpath(config_resource_file_path)

        config_file_path = os.path.join(simulation_path, "simulation.yml")
        with config_resource.open("rb") as src, open (config_file_path, "wb") as file:
            shutil.copyfileobj(src, file)

        # Save simulation class object to pickle file
        simulation_pkl_path = os.path.join(simulation_path, f"{simulation.filename}.pkl")
        with open(simulation_pkl_path, "wb") as file:
            pickle.dump(simulation, file)
        
        # # Creates prepin file inside simulation job folder
        # simulation_prepin_filename = f"prepin.{simulation.filename}"
        # simulation_prepin_path = os.path.join(simulation_path, simulation_prepin_filename)

        # # Write prepin file as "prepin.simulation"
        # with open(simulation_prepin_path, "w") as file:
        #     file.write(simulation.prepin_file_content)

        return simulation

    # Alias
    simulation_init = simulation_initialize
