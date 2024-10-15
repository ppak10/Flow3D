from flow3d import Flow3D

version = 0

output_dir = "/home/flow3d-docker/out"

# Initialize Flow3D wrapper library
f = Flow3D(output_dir=output_dir)

job_name = "SS316L_t_reddy_process_map_20_micron"

job = f.load_job(job_name)

dataset_id = f"baratilab/Flow3D-V{version}-{job_name}"

collection_slug = "baratilab/flow3d-6685a342369b09d5648855a2"

job.create_and_upload_huggingface_dataset(
    dataset_id,
    collection_slug,
    # delete_existing = True,
    num_proc = 16,
)
