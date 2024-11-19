from flow3d import Flow3D

output_dir = "/home/flow3d-docker/out"

# Initialize Flow3D wrapper library
f = Flow3D(output_dir=output_dir)

job = f.load_job("test_evaporation_methods")
# job = f.load_job("test_visualize_1_2_with_beam_x_and_higher_accomodation_coefficient")

job.run_post_process(num_proc=16)
