import bisect
import logging
import traceback
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

    @staticmethod
    def error_callback(e):
        """Log the error and stack trace error"""
        logging.error(e)
        logging.error(traceback.format_exc())

    @staticmethod
    def x_distance(timestep, velocity = 0.5, laser_start_x = 0.06):
        # Coverts from m/s to cm/s
        velocity_cm_per_s = velocity * 100
        x_distance_cm = velocity_cm_per_s * timestep
        return laser_start_x + x_distance_cm

    @staticmethod
    def find_index(x_distance_cm, mesh):
        # Find the insertion point in the sorted list where the value would go
        idx = bisect.bisect_left(mesh, x_distance_cm)

        # print(idx)

        # If the value is exactly at idx, return idx - 1 to indicate the lower bound
        if idx == 0:
            # return None  # The value is smaller than all elements in the list
            return 0
        elif idx == len(mesh):
            # return None  # The value is larger than all elements in the list
            return len(mesh) - 1 
        else:
            return idx - 1  # The value lies between idx-1 and idx

    @staticmethod
    def crop_3d_array(array, crop_x, crop_y = None):
        # Assuming the crop values specify how much to cut from the edges
        # z_len, y_len, x_len = array.shape

        # Create slices for x, y, and z based on the crop distances
        x_slice = slice(crop_x[0], crop_x[1])
        if crop_y is None:
            cropped_array = array[:, :, x_slice]
        else:
            y_slice = slice(crop_y[0], crop_y[1])
            cropped_array = array[:, y_slice, x_slice]
        # z_slice = slice(crop_z[0], z_len - crop_z[1])

        # Crop the array using the slices
        # cropped_array = array[z_slice, y_slice, x_slice]
        return cropped_array

    