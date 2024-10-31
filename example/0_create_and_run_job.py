from flow3d import Flow3D

output_dir = "/home/flow3d-docker/out"

# Initialize Flow3D wrapper library
f = Flow3D(output_dir=output_dir)

# Create Job
# job = f.create_job(name = "Ti-6Al-4V_fast_test", use_wandb = True)
job = f.create_job(name = "SS316L_5_micron_test_1", use_wandb = True)

# Create simulation
s = f.create_simulation(
    power = 300,            # 100 Watts
    velocity = 1.0,         # 1.0 m/s
    # template_id = "R56400",  # Ti-6Al-4V Material Template
    template_id = "S31603",  # Stainless Steel 316L Material Template
    # mesh_size = 1E-5        # 10 micron
    mesh_size = 5E-6        # 0.000005 m (5 µm)
)

# Create multiple simulations
# s = []

# # Power
# power_min = 100     # Minimum power of 100 Watts
# power_max = 400     # Maximum power of 400 Watts (inclusive)
# power_step = 50     # Step size of 100 Watts
# powers = [x for x in range(power_min, power_max + 1, power_step)]
# print(powers)

# # Velocities
# velocity_min = 4    # Minimum velocity of 0.4 m/s
# velocity_max = 20   # Maximum velocity of 2.0 m/s (inclusive)
# velocity_step = 2   # Step size of 0.2 m/s
# velocities = [x/10.0 for x in range(velocity_min, velocity_max + 1, velocity_step)]
# print(velocities)

# for power in powers:
#     for velocity in velocities:
#         s.append(f.create_simulation(
#             power = power,            
#             velocity = velocity,         
#             # template_id = "R56400",  # Ti-6Al-4V Material Template
#             template_id = "S31603",  # Stainless Steel 316L Material Template
#             # mesh_size = 1E-2        # 0.01 m (10,000 µm)
#             mesh_size = 5E-6        # 0.000005 m (5 µm)
#             # mesh_size = 1E-5        # 0.00001 m (10 µm)
#             # mesh_size = 2E-5        # 0.00002 m (20 µm)
#         ))

# Load simulation to job
job.load_simulations(s)

# Run simulations
# job.run_simulations()
