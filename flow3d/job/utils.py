import os
import time

from datetime import timedelta

class JobUtils():

    @staticmethod
    def run_subprocess(func):
        """
        Decorator for running simulation subprocess.
        """

        def wrapper(self, *args, **kwargs):

            # Use passed argument for custom output path
            output_path = "execution_times.txt"
            if "output_path" in kwargs:
                output_path = kwargs["output_path"]

            # Run and time simulation
            start_time = time.time()

            # Run subprocess
            try:
                output = func(self, *args, **kwargs)
            except Exception as e:
                print(e)
                return None

            # Write end time
            end_time = time.time()

            # Write duration to file.
            duration = end_time - start_time
            duration_str = str(timedelta(seconds=duration))
            with open(output_path, "a") as f:
                f.write(f"{func.__name__}: {duration_str}")

            return output 

        return wrapper

    
    @staticmethod
    def change_working_directory(func):
        """
        Decorator for changing and reverting working directory just for method.
        """

        def wrapper(self, *args, **kwargs):

            # Set working directory from kwargs
            if "working_dir" not in kwargs:
                raise Exception(f"No working directory provided")
            else:
                working_dir = kwargs["working_dir"]

            # Change working directory
            previous_dir_path = os.getcwd()
            working_dir_path = os.path.join(self.job_dir_path, working_dir)
            os.chdir(working_dir_path)

            # Run method 
            output = func(self, *args, **kwargs)

            # Change working directory back to previous folder
            os.chdir(previous_dir_path)

            return output

        return wrapper
    