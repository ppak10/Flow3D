# import bisect
# import logging
# import traceback
# import os
# import time
# import zipfile

# from datetime import timedelta
# from tqdm import tqdm

# class JobUtils():

#     @staticmethod
#     def run_subprocess(func):
#         """
#         Decorator for running simulation subprocess.
#         """

#         def wrapper(self, *args, **kwargs):

#             # Use passed argument for custom output path
#             output_path = "execution_times.txt"
#             if "output_path" in kwargs:
#                 output_path = kwargs["output_path"]

#             # Run and time simulation
#             start_time = time.time()

#             # Run subprocess
#             try:
#                 output = func(self, *args, **kwargs)
#             except Exception as e:
#                 print(e)
#                 return None

#             # Write end time
#             end_time = time.time()

#             # Write duration to file.
#             duration = end_time - start_time
#             duration_str = str(timedelta(seconds=duration))
#             with open(output_path, "a") as f:
#                 f.write(f"{func.__name__}: {duration_str}")

#             return output 

#         return wrapper

    
#     @staticmethod
#     def change_working_directory(func):
#         """
#         Decorator for changing and reverting working directory just for method.
#         """

#         def wrapper(self, *args, **kwargs):

#             # Set working directory from kwargs
#             if "working_dir" not in kwargs:
#                 raise Exception(f"No working directory provided")
#             else:
#                 working_dir = kwargs["working_dir"]

#             # Change working directory
#             previous_dir_path = os.getcwd()
#             working_dir_path = os.path.join(self.job_dir_path, working_dir)
#             os.chdir(working_dir_path)

#             # Run method 
#             output = func(self, *args, **kwargs)

#             # Change working directory back to previous folder
#             os.chdir(previous_dir_path)

#             return output

#         return wrapper

#     @staticmethod
#     def error_callback(e):
#         """Log the error and stack trace error"""
#         logging.error(e)
#         logging.error(traceback.format_exc())

#     @staticmethod
#     def x_distance(timestep, velocity = 0.5, laser_start_x = 0.06):
#         # Coverts from m/s to cm/s
#         velocity_cm_per_s = velocity * 100
#         x_distance_cm = velocity_cm_per_s * timestep
#         return laser_start_x + x_distance_cm

#     @staticmethod
#     def find_index(x_distance_cm, mesh):
#         # Find the insertion point in the sorted list where the value would go
#         idx = bisect.bisect_left(mesh, x_distance_cm)

#         # print(idx)

#         # If the value is exactly at idx, return idx - 1 to indicate the lower bound
#         if idx == 0:
#             # return None  # The value is smaller than all elements in the list
#             return 0
#         elif idx == len(mesh):
#             # return None  # The value is larger than all elements in the list
#             return len(mesh) - 1 
#         else:
#             return idx - 1  # The value lies between idx-1 and idx

#     @staticmethod
#     def crop_3d_array(array, crop_x=None, crop_y=None, crop_z=None):
#         # Define slices for x, y, and z based on the crop distances
#         # If a crop value is None, use the full range for that dimension
#         x_slice = slice(crop_x[0], crop_x[1]) if crop_x is not None else slice(None)
#         y_slice = slice(crop_y[0], crop_y[1]) if crop_y is not None else slice(None)
#         z_slice = slice(crop_z[0], crop_z[1]) if crop_z is not None else slice(None)
    
#         # Crop the array using the slices
#         cropped_array = array[z_slice, y_slice, x_slice]
#         return cropped_array

#     # def crop_3d_array(array, crop_x, crop_y = None):
#     #     # Assuming the crop values specify how much to cut from the edges
#     #     # z_len, y_len, x_len = array.shape

#     #     # Create slices for x, y, and z based on the crop distances
#     #     x_slice = slice(crop_x[0], crop_x[1])
#     #     if crop_y is None:
#     #         cropped_array = array[:, :, x_slice]
#     #     else:
#     #         y_slice = slice(crop_y[0], crop_y[1])
#     #         cropped_array = array[:, y_slice, x_slice]
#     #     # z_slice = slice(crop_z[0], z_len - crop_z[1])

#     #     # Crop the array using the slices
#     #     # cropped_array = array[z_slice, y_slice, x_slice]
#     #     return cropped_array

#     @staticmethod
#     def unzip_file(source, destination, chunk_size=1024**3):
#         """
#         Method for unzipping multiple files with the same name into one combined file.
#         @param source: Path to the zip file, e.g., "flslnk.zip"
#         @param destination: Path to the output file, e.g., "flsgrf.simulation"
#         @param chunk_size: Size of each chunk to read (defaults to 10 MB)
#         """
#         print(f"Unzipping `{source}` to `{destination}`...")

#         with zipfile.ZipFile(source) as zip_ref:
#             file_names = zip_ref.namelist()

#             # Filter to include only files named "flsgrf.simulation"
#             # matching_files = [name for name in file_names if name == "flsgrf.simulation"]

#             # Open the destination file once and append each matching file's contents to it
#             with open(destination, 'wb') as dest_file:
#                 for file_name in tqdm(file_names):
#                     # Get the uncompressed file size for progress tracking
#                     uncompressed_size = zip_ref.getinfo(file_name).file_size
#                     print(f"Extracting `{file_name}` ({uncompressed_size} bytes)")

#                     # Open each file inside the zip archive
#                     with zip_ref.open(file_name) as source_file:
#                         # Initialize tqdm progress bar
#                         # with tqdm(total=uncompressed_size, unit="B", unit_scale=True, desc=f"Extracting {file_name}", position=0, leave=True) as pbar:
#                         while True:
#                             # Read a chunk of data from the source file
#                             chunk = source_file.read(chunk_size)
#                             if not chunk:
#                                 break  # Stop when no more data is read

#                             # Append the chunk to the destination file
#                             dest_file.write(chunk)

#                             # Update the progress bar
#                             # pbar.update(len(chunk))

#         print(f"All matching files have been combined into `{destination}`.")

#     @staticmethod
#     def zip_file(source, destination, chunk_size=1024**3):
#         print(f"Zipping `{source}` file to `{destination}`...")
#         zip = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
#         zip.write(source)
#         zip.close()
#         # with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
#         #     with open(source, 'rb') as f_in:
#         #         while True:
#         #             data = f_in.read(chunk_size)
#         #             if not data:
#         #                 break
#         #             # Convert `source` to string before passing to writestr
#         #             zipf.writestr(str(source), data, compress_type=zipfile.ZIP_DEFLATED)
