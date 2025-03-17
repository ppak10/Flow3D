# import os
# import pickle
# import textwrap
# import warnings

# from datetime import datetime

# class JobBase:
#     """
#     Main job methods that do not rely on other classes.
#     """
#     def __init__(
#             self,
#             name = None,
#             filename: str = "job",
#             output_dir = "out",
#             verbose = False,
#             **kwargs,
#         ):
#         self.filename = filename
#         self.output_dir = output_dir
#         self.job_dir_path = None
#         self.verbose = verbose

#         self.simulations = []

#         if name is None:
#             # Sets `job_name` to approximate timestamp.
#             self.name = datetime.now().strftime("%Y%m%d_%H%M%S")
#         else:
#             self.name = name

#         super().__init__(**kwargs)

#     def create_dir(self):
#         """
#         Creates folder to store data related to Flow3D job.
#         """
#         self.job_dir_path = os.path.join(self.output_dir, self.name)

#         # Creates job folder directory in output directory.
#         if not os.path.isdir(self.job_dir_path):
#             os.makedirs(self.job_dir_path)
#         else:
#             warnings.warn(textwrap.dedent(f"""
#             Folder for job `{self.name}` already exists.
#             Following operations will overwrite existing files within folder.
#             """))

#         return self.job_dir_path

#     def save(self):
#         """
#         Saves job instance to pickle file.
#         """
#         job_pkl_path = os.path.join(self.job_dir_path, f"{self.filename}.pkl")
#         with open(job_pkl_path, "wb") as file:
#             pickle.dump(self, file)
