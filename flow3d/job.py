import os
import warnings

from datetime import datetime

class Job():
    """
    Class for running and managing Flow3D simulation outputs.
    """

    def __init__(self, name = None, output_dir = "out"):
        self.output_dir = output_dir
        self.dir_path = None
        if name is None:
            # Sets `job_name` to approximate timestamp.
            self.name = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.name = name

    def create_dir(self):
        """
        Creates folder to store data related to Flow3D job.

        @param output_dir: Output directory for storing jobs
        """
        self.dir_path = os.path.join(self.output_dir, self.name)

        # Creates job folder directory in output directory.
        if not os.path.isdir(self.dir_path):
            os.makedirs(self.dir_path)
        else:
            warnings.warn(f"""
Folder for job `{self.name}` already exists.
Following operations will overwrite existing files within folder.
""")

        return self.dir_path
    
    def load_simulation(self, simulations):
        for simulation in simulations:
            print(simulation.prepin)
    
    def run_simulation(self, simulations):
        for simulation in simulations:
            print(simulation.prepin)
    
    def post_process(self):
        print("postprocess")

