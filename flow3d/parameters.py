import math

# Valid parameters to pass to class as **kwargs (meter-gram-second).
default_parameters = {
    # Process
    "power": 100,                       # 100 Watts
    "velocity": 1.0,                    # 1 m/s
    "beam_diameter": 1E-4,              # 100 µm (not explicity in prepin file)
    "lens_radius": 5E-5,                # 50 µm
    "spot_radius": 5E-5,                # 50 µm
    "gauss_beam": 5E-5 / math.sqrt(2),  # 50 / √2 µm 

    # Mesh
    "mesh_size": 2E-5,                  # 20 µm
    "mesh_x_start": 5E-4,               # 500 µm
    "mesh_x_end": 3E-3,                 # 3000 µm
    "mesh_y_start": 0,                  # 0 µm
    "mesh_y_end": 6E-4,                 # 600 µm
    "mesh_z_start": 0,                  # 0 µm
    "mesh_z_end": 6E-4,                 # 600 µm

    # Fluid Region
    "fluid_region_x_start": 0,          # 0 µm
    "fluid_region_x_end": 2.8E-3,       # 2800 µm
    "fluid_region_y_start": 0,          # 0 µm
    "fluid_region_y_end": 6E-4,         # 600 µm
    "fluid_region_z_start": 0,          # 0 µm
    "fluid_region_z_end": 4E-4,         # 400 µm
}

