# Run from project root.
# `python example/create_and_run_job.py`
from flow3d import Flow3D

f = Flow3D()

# Create Job
job = f.create_job("SS316L")
print(job.dir_path)

# Create Simulations
power = [x for x in range(0, 500, 20)]
velocity = [x/10.0 for x in range(0, 30, 1)]

simulation = f.create_simulation(mesh_size = 100)
print(simulation.verbose)
print(simulation.mesh_size)
print(simulation.name)

# simulations = f.build_from_template(
#     "S31603",
#     power,
#     velocity,
#     mesh_z_end=1.2E-3,
#     fluid_region_z_end=1E-3,
# )
# 
# print(simulations)
