import math

from decimal import Decimal

class SimulationParameters():
    """
    Class for defining simulation parameters.
    """

    def __init__(self, **kwargs):
        # Valid parameters to pass to class as **kwargs (meter-gram-second).
        self.default_parameters = {
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

        # Sets default parameters
        for key, value in self.default_parameters.items():
            setattr(self, key, value)

        # Sets override values to that provided in kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        super().__init__(**kwargs)

    def cgs(self, parameter: str):
        """
        Converts metric process parameter to centimeter-gram-second units.
        """
        if parameter == "power":
            # 1 erg = 1 cm^2 * g * s^-2
            # 1 J = 10^7 ergs -> 1 W = 10^7 ergs/s
            return getattr(self, parameter) * 1E7
        elif parameter == "velocity":
            # Handled separately from `else` case just in case if mm/s input
            # is implement in the future.
            # 1 m/s = 100 cm/s
            return getattr(self, parameter) * 100
        elif parameter == "gauss_beam":
            # Gauss beam should utilize a more precise value.
            return getattr(self, parameter) * 1E2
        else:
            # Converting to decimal handles case where 2.799 != 2.8
            parameter_decimal = Decimal(getattr(self, parameter) * 1E2)
            return float(round(parameter_decimal, 3))

    # TODO: Figure whether or not to implement, in practice it seems unlikely
    # that one would want to change simulation parameters after initializing
    # rather than just create a new one.
    # @update_name
    # @update_prepin_file_content
    # def set_process_parameters(self, **kwargs):
    #     """
    #     Set process parameters for a given simulation

    #     @param power: Laser Power (W)
    #     @param velocity: Scan Velocity (m/s)
    #     @param beam_diameter: Beam Diameter (m) -> defaults to 1E-4 (100 µm)
    #     @param lens_radius: Lens Radius (m) -> defaults to 5E-5 (50 µm)
    #     @param spot_radius: Spot Radius (m) -> defaults to 5E-5 (50 µm)
    #     @param gauss_beam: Gaussian Beam (m) -> defaults to 5E-5/√2 (50/√2 µm)
    #     @param mesh_size: Mesh Size (m) -> defaults to 2E-5 (20 µm)
    #     @param mesh_x_start: Mesh X Start (m) -> defaults to 5E-4 m (500 µm)
    #     @param mesh_x_end: Mesh X End (m) -> defaults to 3E-3 m (3000 µm)
    #     @param mesh_y_start: Mesh Y Start (m) -> defaults to 0 m (0 µm)
    #     @param mesh_y_end: Mesh Y End (m) -> defaults to 6E-4 m (600 µm)
    #     @param mesh_z_start: Mesh Z Start (m) -> defaults to 0 m (0 µm)
    #     @param mesh_z_end: Mesh Z End (m) -> defaults to 6E-4 m (600 µm)
    #     @param fluid_region_x_start: Fluid back boundary (default 0 µm)
    #     @param fluid_region_x_end: Fluid front boundary (default 2800 µm)
    #     @param fluid_region_y_start: Fluid left boundary (default 0 µm)
    #     @param fluid_region_y_end: Fluid right boundary (default 600 µm)
    #     @param fluid_region_z_start: Fluid bottom boundary (default 0 µm)
    #     @param fluid_region_z_end: Fluid top boundary (default 400 µm)
    #     @return
    #     """

    #     # TODO: Add min / max checks.
    #     # TODO: Handle auto-generation of gauss_beam parameter
    #     for key, value in kwargs.items():
    #         if key in self.default_parameters.keys():
    #             # Integer values
    #             if key in ["power"]:
    #                 setattr(self, key, int(value))

    #             # converts everything else to float.
    #             else:
    #                 setattr(self, key, float(value))

