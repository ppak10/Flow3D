import os
import warnings

from datetime import datetime
from flow3d.job import Job
from flow3d.simulation import Simulation

class Flow3D():
    """
    Wrapper for creating and running Flow 3D simulations.
    """

    def __init__(
        self,
        output_dir="out",
        keep_in_memory = False,
        num_proc = 1,
        verbose = False
    ):
        super(Flow3D, self).__init__()
        self.current_dir = os.path.dirname(__file__)
        self.keep_in_memory = keep_in_memory
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

    def create_job(self, job_name = None):
        """
        Creates folder to store data related to Flow3D job.

        @param job_name: New name of job 
        """
        job = Job(job_name)
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
