import datetime
import os
import subprocess
import time
import warnings
import zipfile

class Job():
    """
    Class for running and managing Flow3D simulation outputs.
    """

    def __init__(self, name = None, output_dir = "out"):
        self.output_dir = output_dir
        self.dir_path = None
        self.simulations = []

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
    
    def load(self, simulation):
        """
        Loads simulation(s) into job folder.
        """
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
        s_dir_path = os.path.join(self.dir_path, simulation.name)
        if not os.path.isdir(s_dir_path):
            os.makedirs(s_dir_path)

        # Creates prepin file inside simulation job folder
        s_prepin_filename = "prepin.simulation"
        s_prepin_file_path = os.path.join(s_dir_path, s_prepin_filename)

        # Write prepin file as "prepin.simulation"
        with open(s_prepin_file_path, "w") as file:
            file.write(simulation.prepin_file_content)
    
    def run(self):
        """
        Run job with parameters
        """
        for simulation in self.simulations:
            self.run_simulation(simulation)

    def run_simulation(self, simulation):
        """
        Run simulation and Zip
        """

        # Change working directory to simulation folder
        previous_dir_path = os.getcwd()
        s_dir_path = os.path.join(self.dir_path, simulation.name)
        os.chdir(s_dir_path)

        # Run and time simulation
        start_time = time.time()

        try:
            with open("runhyd.txt", "w") as f:
                process = subprocess.Popen(
                    ["runhyd", "simulation"],
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

            # Zip Large Files
            flsgrf_zip = zipfile.ZipFile("flsgrf.zip", "w", zipfile.ZIP_DEFLATED)
            flsgrf_zip.write("flsgrf.simulation")
            flsgrf_zip.close()

            # Remove Large File
            os.remove("flsgrf.simulation")
        except Exception as e:
            print(e)

        end_time = time.time()

        # Write duration to file.
        duration = end_time - start_time
        duration_str = str(datetime.timedelta(seconds=duration))
        with open(f"simulation_execution_time.txt", "a") as f:
            f.write(duration_str)

        # Return back to previous directory path
        os.chdir(previous_dir_path)
    
    def post_process(self):
        print("postprocess")
