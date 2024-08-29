# Run from project root.
# `python example/create_and_run_job.py`
from flow3d import Flow3D

f = Flow3D()

# Create Job
job = f.create_job("Ti-6Al-4V")
print(job.dir_path)

# Set process parameter range for simulations 
powers = [x for x in range(0, 500, 20)]
velocities = [x/10.0 for x in range(0, 30, 1)]

# Create simulations
simulations = []

for power in powers:
    for velocity in velocities:
        s = f.create_simulation(
            power = power,
            velocity = velocity,
            mesh_size = 100,
            template_id = "R56400",
        )
        simulations.append(s)

# Load simulations to job
job.load(simulations)

# Run simulations
job.run()

