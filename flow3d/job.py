import os
import warnings

from datetime import datetime

class Job():
    """
    Class for running and managing Flow3D simulation outputs.
    """

    def __init__(self, name = None):
        if name is None:
            # Sets `job_name` to approximate timestamp.
            self.name = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.name = name

    def create_dir(self, output_dir = "out"):
        """
        Creates folder to store data related to Flow3D job.

        @param output_dir: Output directory for storing jobs
        """
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

