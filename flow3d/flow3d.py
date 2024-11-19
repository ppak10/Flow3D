import multiprocessing
import os
import pickle
import time
import wandb

from flow3d.job import Job
from flow3d.simulation import Simulation
from pathlib import Path
from tqdm import tqdm

# TODO: Rename this to portfolio to match Flow3D jargon.
class Flow3D():
    """
    Wrapper for creating and running Flow 3D simulations.
    @param output_dir: Directory for managing job outputs.
    """

    def __init__(self, output_dir="out"):
        super(Flow3D, self).__init__()
        self.current_dir = os.path.dirname(__file__)

        # Output Directory
        self.output_dir = output_dir
        if not os.path.isdir(self.output_dir):
            # Creates output directory to store Flow3D simulation data.
            os.makedirs(self.output_dir)

    # TODO: Rename `Job` to `Workspace`
    def create_job(self, name, **kwargs):
        """
        Creates folder to store data related to Flow3D job.

        @param job_name: New name of job 
        """

        # Sets output_dir to value in self if override not provided.
        if "output_dir" not in kwargs:
            kwargs["output_dir"] = self.output_dir
            
        job = Job(name=name, **kwargs)
        job.create_dir()

        return job
    
# TODO: Move rest to Job class.
    
    def create_job_simulation(self, job_name, **kwargs):
        """
        Create simulation folder and prepin given a specified job name

        @param job_name: Name of existing Job 
        """

        # Define Job path and check that it exists
        job_dir_path = os.path.join(self.output_dir, job_name)
        if not os.path.isdir(job_dir_path):
            raise Exception(f"Folder `{job_name}` not found at `{job_dir_path}`")

        s = Simulation(**kwargs)

        # Create simulation job folder
        s_dir_path = os.path.join(job_dir_path, s.name)
        if not os.path.isdir(s_dir_path):
            os.makedirs(s_dir_path)

        # Save simulation class object to pickle file
        s_pkl_path = os.path.join(s_dir_path, f"{s.filename}.pkl")
        with open(s_pkl_path, "wb") as file:
            pickle.dump(s, file)
        
        # Creates prepin file inside simulation job folder
        s_prepin_filename = f"prepin.{s.filename}"
        s_prepin_file_path = os.path.join(s_dir_path, s_prepin_filename)

        # Write prepin file as "prepin.simulation"
        with open(s_prepin_file_path, "w") as file:
            file.write(s.prepin_file_content)

        return s

    def create_job_simulation_process_map(
            self,
            job_name,
            power_min = 100,
            power_max = 400,
            power_step = 100,
            powers = None,
            velocity_min = 0.4,
            velocity_max = 2.0,
            velocity_step = 0.4,
            velocities = None,
            **kwargs,
        ):
        """
        Creates a process map of simulations bounded by power and velocity.

        @param power_min: (Inclusive) Minimum power in watts
        @param power_max: (Inclusive) Maximum power in watts,
        @param power_step: Step size of power in watts,
        @param velocity_min: (Inclusive) Minimum velocity in m/s,
        @param velocity_max = (Inclusive) Maximum velocity in m/s,
        @param velocity_step = Step size of velocity in m/s,
        """

        #TODO: Add in divibility checks for power and velocity steps.
        if powers == None:
            powers = [x for x in range(power_min, power_max + 1, power_step)]

        if velocities == None:
            # Turns m/s velocity min and max values into integers for `range()`.
            v_min = int(velocity_min * 10)
            v_max = int((velocity_max * 10) + 1)
            v_step = int(velocity_step * 10)
            velocities = [x/10.0 for x in range(v_min, v_max, v_step)]

        # Iterate through power and velocity combinations.
        simulations = []
        for power in powers:
            for velocity in velocities:
                s = self.create_job_simulation(
                    job_name=job_name,
                    power = power,
                    velocity = velocity,
                    **kwargs
                )
                simulations.append(s)

        print(f"Created {len(simulations)} simulations")
        return simulations

    def run_job_simulations(
            self,
            job_name,
            simulation_filename = "simulation",
            use_wandb = False,
            **kwargs
        ):
        """
        Method to run simulations within a job folder.

        @param job_name: Name of existing Job
        """

        # Initialize WandB
        if use_wandb:
            wandb.login()

            wandb.init(
                project = self.wandb_project,
                config = {
                    "job_name": self.name,
                    "simulations": [s.name for s in self.simulations]
                }
            )

        # Define Job path and check that it exists
        job_dir_path = os.path.join(self.output_dir, job_name)
        if not os.path.isdir(job_dir_path):
            raise Exception(f"Folder `{job_name}` not found at `{job_dir_path}`")

        # Only consider directories and skip over possible files.
        simulation_folders = sorted([d.name for d in Path(job_dir_path).iterdir() if d.is_dir()])
        print(f"Simulation Folders ({len(simulation_folders)}): {simulation_folders}")

        # Run simulations
        for simulation_folder in tqdm(simulation_folders):

            # Load simulation object 
            s_dir_path = os.path.join(job_dir_path, simulation_folder)
            s_pkl_path = os.path.join(s_dir_path, f"{simulation_filename}.pkl")
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

###################
# Post Processing #   
###################

    def run_job_simulations_guipost(
            self,
            job_name,
            num_proc = 1,
            skip_checks = False,
            simulation_filename = "simulation",
            **kwargs
        ):
        """
        Method to run guipost for simulations within a job folder.

        @param job_name: Name of existing Job
        @param num_proc: Number of processes to use.
        """

        # Define Job path and check that it exists
        job_dir_path = os.path.join(self.output_dir, job_name)
        if not os.path.isdir(job_dir_path):
            raise Exception(f"Folder `{job_name}` not found at `{job_dir_path}`")

        # Only consider directories and skip over possible files.
        simulation_folders = sorted([d.name for d in Path(job_dir_path).iterdir() if d.is_dir()])
        print(f"Simulation Folders ({len(simulation_folders)}): {simulation_folders}")

        # Load simulations
        simulations = []
        for simulation_folder in tqdm(simulation_folders):

            # Load simulation object 
            s_dir_path = os.path.join(job_dir_path, simulation_folder)
            s_pkl_path = os.path.join(s_dir_path, f"{simulation_filename}.pkl")
            with open(s_pkl_path, "rb") as file:
                s = pickle.load(file)
                simulations.append(s)

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(job_dir_path, simulation.name)
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
                s_dir_path = os.path.join(job_dir_path, simulation.name)
                simulation.guipost(working_dir = s_dir_path, **kwargs)
    
    def run_job_simulations_chunk_flslnk(
            self,
            job_name,
            num_proc = 1,
            skip_checks = False,
            simulation_filename = "simulation",
            **kwargs
        ):
        """
        Method to run chunk flslnk for simulations within a job folder.

        @param job_name: Name of existing Job
        @param num_proc: Number of processes to use.
        """

        # Define Job path and check that it exists
        job_dir_path = os.path.join(self.output_dir, job_name)
        if not os.path.isdir(job_dir_path):
            raise Exception(f"Folder `{job_name}` not found at `{job_dir_path}`")

        # Only consider directories and skip over possible files.
        simulation_folders = sorted([d.name for d in Path(job_dir_path).iterdir() if d.is_dir()])
        print(f"Simulation Folders ({len(simulation_folders)}): {simulation_folders}")

        # Load simulations
        simulations = []
        for simulation_folder in tqdm(simulation_folders):

            # Load simulation object 
            s_dir_path = os.path.join(job_dir_path, simulation_folder)
            s_pkl_path = os.path.join(s_dir_path, f"{simulation_filename}.pkl")
            with open(s_pkl_path, "rb") as file:
                s = pickle.load(file)
                simulations.append(s)

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(job_dir_path, simulation.name)
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
                s_dir_path = os.path.join(job_dir_path, simulation.name)
                simulation.chunk_flslnk(working_dir = s_dir_path, **kwargs)
    
    def run_job_simulations_flslnk_chunk_to_npz(
            self,
            job_name,
            num_proc = 1,
            skip_checks = False,
            simulation_filename = "simulation",
            **kwargs
        ):
        """
        Method to convert flslnk chunks into npz for simulations within a job folder.

        @param job_name: Name of existing Job
        @param num_proc: Number of processes to use.
        """

        # Define Job path and check that it exists
        job_dir_path = os.path.join(self.output_dir, job_name)
        if not os.path.isdir(job_dir_path):
            raise Exception(f"Folder `{job_name}` not found at `{job_dir_path}`")

        # Only consider directories and skip over possible files.
        simulation_folders = sorted([d.name for d in Path(job_dir_path).iterdir() if d.is_dir()])
        print(f"Simulation Folders ({len(simulation_folders)}): {simulation_folders}")

        # Load simulations
        simulations = []
        for simulation_folder in tqdm(simulation_folders):

            # Load simulation object 
            s_dir_path = os.path.join(job_dir_path, simulation_folder)
            s_pkl_path = os.path.join(s_dir_path, f"{simulation_filename}.pkl")
            with open(s_pkl_path, "rb") as file:
                s = pickle.load(file)
                simulations.append(s)

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(job_dir_path, simulation.name)
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
                s_dir_path = os.path.join(job_dir_path, simulation.name)
                simulation.flslnk_chunk_to_npz(working_dir = s_dir_path, **kwargs)
    
#################
# Visualization # 
#################

    def run_job_simulations_prepare_visualization(
            self,
            job_name,
            num_proc = 1,
            skip_checks = False,
            simulation_filename = "simulation",
            **kwargs
        ):
        """
        Method to convert flslnk chunks into npz for simulations within a job folder.

        @param job_name: Name of existing Job
        @param num_proc: Number of processes to use.
        """

        # Define Job path and check that it exists
        job_dir_path = os.path.join(self.output_dir, job_name)
        if not os.path.isdir(job_dir_path):
            raise Exception(f"Folder `{job_name}` not found at `{job_dir_path}`")

        # Only consider directories and skip over possible files.
        simulation_folders = sorted([d.name for d in Path(job_dir_path).iterdir() if d.is_dir()])
        print(f"Simulation Folders ({len(simulation_folders)}): {simulation_folders}")

        # Load simulations
        simulations = []
        for simulation_folder in tqdm(simulation_folders):

            # Load simulation object 
            s_dir_path = os.path.join(job_dir_path, simulation_folder)
            s_pkl_path = os.path.join(s_dir_path, f"{simulation_filename}.pkl")
            with open(s_pkl_path, "rb") as file:
                s = pickle.load(file)
                simulations.append(s)

        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                for simulation in tqdm(simulations):
                    s_dir_path = os.path.join(job_dir_path, simulation.name)
                    pool.apply_async(
                        simulation.prepare_visualization,
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
                s_dir_path = os.path.join(job_dir_path, simulation.name)
                simulation.prepare_visualization(working_dir = s_dir_path, **kwargs)

    def run_job_simulations_generate_visualization_views(
            self,
            job_name,
            num_proc = 1,
            skip_checks = False,
            simulation_filename = "simulation",
            views = ["isometric", "cross_section_x", "cross_section_y"],
            **kwargs
        ):
        """
        Method to convert flslnk chunks into npz for simulations within a job folder.

        @param job_name: Name of existing Job
        @param num_proc: Number of processes to use.
        """

        # Define Job path and check that it exists
        job_dir_path = os.path.join(self.output_dir, job_name)
        if not os.path.isdir(job_dir_path):
            raise Exception(f"Folder `{job_name}` not found at `{job_dir_path}`")

        # Only consider directories and skip over possible files.
        simulation_folders = sorted([d.name for d in Path(job_dir_path).iterdir() if d.is_dir()])
        print(f"Simulation Folders ({len(simulation_folders)}): {simulation_folders}")

        # Load simulations
        simulations = []
        for simulation_folder in tqdm(simulation_folders):

            # Load simulation object 
            s_dir_path = os.path.join(job_dir_path, simulation_folder)
            s_pkl_path = os.path.join(s_dir_path, f"{simulation_filename}.pkl")
            with open(s_pkl_path, "rb") as file:
                s = pickle.load(file)
                simulations.append(s)

        for simulation in tqdm(simulations):
            s_dir_path = os.path.join(job_dir_path, simulation.name)
            for view in views:
                simulation.generate_visualization_view(
                    view = view,
                    num_proc = num_proc,
                    working_dir = s_dir_path,
                    **kwargs
                )