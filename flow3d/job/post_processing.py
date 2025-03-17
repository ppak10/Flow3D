# import multiprocessing
# import os
# from tqdm import tqdm


# class JobPostProcessing():

#     def run_post_process(self, num_proc = 1):
#         """
#         Runs post processing method with or without multiprocessing.
#         """
#         if num_proc > 1:
#             with multiprocessing.Pool(processes=num_proc) as pool:
#                 for simulation in tqdm(sorted(self.simulations)):
#                     pool.apply_async(
#                         self.post_process,
#                         args=(simulation, ),
#                         error_callback=self.error_callback
#                     )
#                 pool.close()
#                 pool.join()
                
#         else:
#             for simulation in tqdm(sorted(self.simulations)):
#                 self.post_process(simulation)

#     def post_process(self, simulation):
#         print(f"""\n
# ################################################################################
# Post Process: `{simulation.name}`
# ################################################################################
# """)
#         s_dir_path = os.path.join(self.job_dir_path, simulation.name)
#         simulation_status = simulation.check_status(s_dir_path)

#         if simulation_status["post_process_create_npz_completed"]:
#             print(f"{simulation.name} already post processed, skipping")

#         elif simulation_status["run_simulation_completed"]:
#             if not simulation_status["post_process_create_flslnk_completed"]:
#                 print(f"Creating `flslnk.tmp` file for {simulation.name}...")
#                 self.create_flslnk(simulation, working_dir=simulation.name)

#             if not simulation_status["post_process_create_chunks_completed"]:
#                 print(f"Processing `flslnk.tmp` into chunks for {simulation.name}...")
#                 self.create_chunks(simulation, working_dir=simulation.name)

#             simulation_status = simulation.check_status(s_dir_path)
#             if not simulation_status["post_process_create_npz_completed"]:
#                 print(f"Creating `.npz` files {simulation.name}...")
#                 self.create_npz(simulation)
#         else:
#             print(f"{simulation.name} not completed, skipping")
