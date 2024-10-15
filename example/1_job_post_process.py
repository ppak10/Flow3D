from flow3d import Flow3D

output_dir = "/home/flow3d-docker/out"

# Initialize Flow3D wrapper library
f = Flow3D(output_dir=output_dir)

job = f.load_job("Ti-6Al-4V_t_reddy_process_map_5_micron")

job.run_post_process(num_proc=64)
