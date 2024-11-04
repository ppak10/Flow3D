import os
import pickle
import subprocess
import time
import wandb

from tqdm import tqdm
from .utils import JobUtils
from .wandb import JobWandb

class JobSimulation():
    """
    Class for running and managing Flow3D simulations.
    """

    @staticmethod
    def save_simulation(func):
        """
        Decorator for saving simulation instance to pickle file after method.
        """

        def wrapper(self, *args, **kwargs):
            simulation = func(self, *args, **kwargs)

            # Skips saving if error occured during
            if simulation is None:
                print("Simulation not saved")
                return simulation

            s_dir_path = os.path.join(self.job_dir_path, simulation.name)
            s_pkl_file_path = os.path.join(s_dir_path, f"{simulation.filename}.pkl")
            with open(s_pkl_file_path, "wb") as file:
                pickle.dump(simulation, file)
            
            return simulation
        return wrapper

    def load_simulations(self, simulation = None):
        """
        Loads simulation(s) into job folder.
        """
        # TODO: Add type checking for instance of simulation
        if isinstance(simulation, list):
            for s in simulation:
                self.load_simulation(s)
        else:
            self.load_simulation(simulation)

    def load_simulation(self, simulation):
        """
        Creates folder in job and writes simulation prepin file.
        """
        self.simulations.append(simulation)

        # Create simulation job folder
        s_dir_path = os.path.join(self.job_dir_path, simulation.name)
        if not os.path.isdir(s_dir_path):
            os.makedirs(s_dir_path)

        # Creates prepin file inside simulation job folder
        s_prepin_filename = f"prepin.{simulation.filename}"
        s_prepin_file_path = os.path.join(s_dir_path, s_prepin_filename)

        # Write prepin file as "prepin.simulation"
        with open(s_prepin_file_path, "w") as file:
            file.write(simulation.prepin_file_content)

        # Saves list of simulations to job
        self.save()
        return simulation

    @JobWandb.wandb_run
    def run_simulations(self):
        """
        Run simulations loaded in job
        """
        for simulation in tqdm(self.simulations):
            self.run_simulation(simulation, working_dir = simulation.name)

            # TODO: Implement better logging here.
            if self.use_wandb:
                wandb.log({
                    "name": simulation.name,
                    "time": time.time()
                })

    @save_simulation
    @JobUtils.change_working_directory
    @JobUtils.run_subprocess
    def run_simulation(
        self,
        simulation,
        delete_output = True,
        zip_output = True,
        **kwargs,
    ):
        """
        Run simulation and Zip
        @param simulation: Simulation
        @param delete_output: Deletes raw output `flsgrf.simulation` file -> True
        @param zip_output: Zips `flsgrf.simulation` file -> True

        @param working_dir: Sets working directory to `simulation.name`.
        """

        if os.path.isfile("runhyd.txt"):
            print(f"`runhyd.txt` file for {simulation.name} exists, skipping...")
            return simulation

        print(f"Running {simulation.name}...")
        with open("runhyd.txt", "w") as f:
            process = subprocess.Popen(
                ["runhyd", simulation.filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in process.stdout:
                f.write(line)
                # if self.verbose:
                #     print(line, end="")

            process.stdout.close()
            process.wait()

        # Zip `flsgrf.simulation` File
        if zip_output:
            JobUtils.zip_file(f"flsgrf.{simulation.filename}", "flsgrf.zip")

        # Remove Large File
        if delete_output:
            os.remove(f"flsgrf.{simulation.filename}")

        return simulation