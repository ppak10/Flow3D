import os
import warnings

from datetime import datetime
from flow3d.prepin import Prepin

class Flow3D(Prepin):
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
        if job_name is None:
            # Sets `job_name` to approximate timestamp.
            job_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.job_name = job_name
        self.job_dir_path = os.path.join(self.output_dir, self.job_name)

        # Creates job folder directory in output directory.
        if not os.path.isdir(self.job_dir_path):
            os.makedirs(self.job_dir_path)
        else:
            warnings.warn(f"""
Folder for job `{self.job_name}` already exists.
Following operations will overwrite existing files within folder.
""")

        return job_name

    # Aliases
    prepin_build_from_template = Prepin.build_from_template
