import os

from flow3d.job import Job
from flow3d.simulation import Simulation

class Flow3D():
    """
    Wrapper for creating and running Flow 3D simulations.
    """

    def __init__(self, output_dir="out", num_proc = 1, verbose = False):
        super(Flow3D, self).__init__()
        self.current_dir = os.path.dirname(__file__)
        self.num_proc = num_proc
        self.verbose = verbose

        # Output Directory
        self.output_dir = output_dir
        if not os.path.isdir(self.output_dir):
            # Creates output directory to store Flow3D simulation data.
            os.makedirs(self.output_dir)

        # Job
        self.job_name = None 
        self.job_dir_path = None

    def create_job(self, **kwargs):
        """
        Creates folder to store data related to Flow3D job.

        @param job_name: New name of job 
        """

        # Sets output_dir to value in self if override not provided.
        if "output_dir" not in kwargs:
            kwargs["output_dir"] = self.output_dir
            
        job = Job(**kwargs)
        job.create_dir()

        return job

    def create_simulation(self, **kwargs):
        """
        Creates folder to store simulation metadata such as prepin files.

        @param simulation_name: New name of simulation
        """
        simulation = Simulation(**kwargs)
        # simulation.create_dir()

        return simulation

    # Aliases
    # prepin_build_from_template = Prepin.build_from_template
