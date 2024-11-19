import bisect
import copy
import functools
import logging
import traceback
import numpy as np
import os
import zipfile

from tqdm import tqdm

class SimulationUtils():
    
    @staticmethod
    def change_working_directory(func):
        """
        Decorator for changing and reverting working directory just for method.
        """

        # Uses `functools.wraps` decorator to preserve metadadta during
        # multiprocessing.
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):

            # Set working directory from kwargs
            if "working_dir" not in kwargs:
                raise Exception(f"No working directory provided")
            else:
                working_dir = kwargs["working_dir"]

            # Change working directory
            previous_dir = os.getcwd()
            os.chdir(working_dir)

            # Run method 
            output = func(self, *args, **kwargs)

            # Change working directory back to previous folder
            os.chdir(previous_dir)

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
    def crop_3d_array(array, crop_x=None, crop_y=None, crop_z=None):
        # Define slices for x, y, and z based on the crop distances
        # If a crop value is None, use the full range for that dimension
        x_slice = slice(crop_x[0], crop_x[1]) if crop_x is not None else slice(None)
        y_slice = slice(crop_y[0], crop_y[1]) if crop_y is not None else slice(None)
        z_slice = slice(crop_z[0], crop_z[1]) if crop_z is not None else slice(None)
    
        # Crop the array using the slices
        cropped_array = array[z_slice, y_slice, x_slice]
        return cropped_array

    @staticmethod
    def unzip_file(source, destination, chunk_size=1024**3):
        """
        Method for unzipping multiple files with the same name into one combined file.
        @param source: Path to the zip file, e.g., "flslnk.zip"
        @param destination: Path to the output file, e.g., "flsgrf.simulation"
        @param chunk_size: Size of each chunk to read (defaults to 10 MB)
        """
        print(f"Unzipping `{source}` to `{destination}`...")

        with zipfile.ZipFile(source) as zip_ref:
            file_names = zip_ref.namelist()

            # Filter to include only files named "flsgrf.simulation"
            # matching_files = [name for name in file_names if name == "flsgrf.simulation"]

            # Open the destination file once and append each matching file's contents to it
            with open(destination, 'wb') as dest_file:
                for file_name in tqdm(file_names):
                    # Get the uncompressed file size for progress tracking
                    uncompressed_size = zip_ref.getinfo(file_name).file_size
                    print(f"Extracting `{file_name}` ({uncompressed_size} bytes)")

                    # Open each file inside the zip archive
                    with zip_ref.open(file_name) as source_file:
                        # Initialize tqdm progress bar
                        # with tqdm(total=uncompressed_size, unit="B", unit_scale=True, desc=f"Extracting {file_name}", position=0, leave=True) as pbar:
                        while True:
                            # Read a chunk of data from the source file
                            chunk = source_file.read(chunk_size)
                            if not chunk:
                                break  # Stop when no more data is read

                            # Append the chunk to the destination file
                            dest_file.write(chunk)

                            # Update the progress bar
                            # pbar.update(len(chunk))

        print(f"All matching files have been combined into `{destination}`.")

    @staticmethod
    def zip_file(source, destination):
        print(f"Zipping `{source}` file to `{destination}`...")
        zip = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
        zip.write(source)
        zip.close()

    # TODO: Clean this up
    @staticmethod
    def df_to_numpy(df):
        dtdx_dtdy_dtdz_timestep = []
        dtdx_dtdy_dtdz_z = []
        dtdx_dtdy_dtdz_y = []

        x_y_z_timestep = []
        x_y_z_z = []
        x_y_z_y = []

        vx_vy_vz_timestep = []
        vx_vy_vz_z = []
        vx_vy_vz_y = []

        keys = ["pressure", "temperature", "melt_region", "temperature_gradient", "liquid_label", "fraction_of_fluid"]

        values = {
            "timestep": [],
            "z": [],
            "y": [],
        }

        key_values = {}
        for key in keys:
            key_values[key] = copy.deepcopy(values)

        prev_z = None
        prev_y = None

        for i in range(len(df)):
            row = df.iloc[i]

            z, y = row["z"], row["y"]

            if y != prev_y and prev_y is not None:

                dtdx_dtdy_dtdz_z.append(dtdx_dtdy_dtdz_y)
                dtdx_dtdy_dtdz_y = []

                x_y_z_z.append(x_y_z_y)
                x_y_z_y = []

                vx_vy_vz_z.append(vx_vy_vz_y)
                vx_vy_vz_y = []

                for key in keys:
                    # print(key, key_values[key]["y"])
                    key_values[key]["z"].append(key_values[key]["y"])
                    key_values[key]["y"] = []

            if z != prev_z and prev_z is not None:

                dtdx_dtdy_dtdz_timestep.append(dtdx_dtdy_dtdz_z)
                dtdx_dtdy_dtdz_z = []

                x_y_z_timestep.append(x_y_z_z)
                x_y_z_z = []

                vx_vy_vz_timestep.append(vx_vy_vz_z)
                vx_vy_vz_z = []

                for key in keys:
                    # print(key, len(key_values[key]["z"]))
                    key_values[key]["timestep"].append(key_values[key]["z"])
                    key_values[key]["z"] = []

            dtdx_dtdy_dtdz_y.append([row["dtdx"], row["dtdy"], row["dtdz"]])
            x_y_z_y.append([row["x"], row["y"], row["z"]])
            vx_vy_vz_y.append([row["vx"], row["vy"], row["vz"]])

            for key in keys:
                key_values[key]["y"].append(row[key])

            prev_z = z
            prev_y = y

        # Adds last value
        dtdx_dtdy_dtdz_y.append([row["dtdx"], row["dtdy"], row["dtdz"]])
        x_y_z_y.append([row["x"], row["y"], row["z"]])
        vx_vy_vz_y.append([row["vx"], row["vy"], row["vz"]])
        dtdx_dtdy_dtdz_z.append(dtdx_dtdy_dtdz_y)

        x_y_z_z.append(x_y_z_y)
        vx_vy_vz_z.append(vx_vy_vz_y)

        for key in keys:
            key_values[key]["y"].append(row[key])
            key_values[key]["z"].append(key_values[key]["y"])


        timestep = {} 
        for key in keys:
            timestep[key] = [np.array(key_values[key]["timestep"])]

        other = {
            "dtdx_dtdy_dtdz": [np.array(dtdx_dtdy_dtdz_timestep)],
            "x_y_z": [np.array(x_y_z_timestep)],
            "vx_vy_vz": [np.array(vx_vy_vz_timestep)],
        }

        return {
            **timestep,
            **other,
        }

