import os
import subprocess

from flow3d.simulation.utils.decorators import SimulationUtilsDecorators

class SimulationRun():
    """
    Run methods file for simulation class.
    """

    @SimulationUtilsDecorators.change_working_directory
    def runhyd(self, delete_output = True, zip_output = True, **kwargs):
        """
        Open `runhyd` subprocess and zip output

        @param delete_output: Deletes raw output `flsgrf.simulation` file
        @param zip_output: Zips `flsgrf.simulation` file

        @param working_dir: Sets working directory to `simulation.name`.
        """

        if os.path.isfile("runhyd.txt"):
            print(f"`runhyd.txt` file for {self.name} exists, skipping...")
            return self 

        # Open Subprocess
        print(f"Running {self.name}...")
        try:
            with open("runhyd.txt", "w") as f:
                process = subprocess.Popen(
                    ["runhyd", self.filename],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                for line in process.stdout:
                    f.write(line)

                process.stdout.close()
                process.wait()

        except Exception as e:
            print(f"Error running `runhyd` for simulation: {self.name}")
            return None

        # Zip `flsgrf.simulation` File
        if zip_output:
            self.zip_file(f"flsgrf.{self.filename}", "flsgrf.zip")

        # Remove Large File
        if delete_output:
            os.remove(f"flsgrf.{self.filename}")

        return self 
