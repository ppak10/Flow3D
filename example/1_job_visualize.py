from flow3d import Flow3D

output_dir = "/home/flow3d-docker/out"

# Initialize Flow3D wrapper library
f = Flow3D(output_dir=output_dir)

# job = f.load_job("SS316L_t_reddy_process_map_10_micron")
job = f.load_job("SS316L_5_micron_test")

job.run_visualize(num_proc=48)
