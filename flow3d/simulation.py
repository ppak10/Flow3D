import math

from decimal import Decimal
from flow3d.parameters import default_parameters
from flow3d.prepin import Prepin

class Simulation(Prepin):
    """
    Simulation object for Flow3D
    """

    @staticmethod
    def update_name(func):
        """
        Decorator for updating simulation name for when process parameters have
        changed.

        @param func: Method where process parameters have changed within class.
        """
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)

            # Generate Name using specific version.
            self.name = getattr(self, f"generate_name_v{self.version}")()

            return result

        return wrapper

    @staticmethod
    def update_prepin_file_content(func):
        """
        Decorator for updating prepin file content when process parameters have
        changed.

        @param func: Method where process parameters have changed within class.
        """
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)

            # Update self.prepin_file_content
            if self.use_template:
                self.build_from_template()

            return result

        return wrapper

    @update_name
    @update_prepin_file_content
    def __init__(
        self,
        version = 0,
        verbose = False,
        use_template = True,
        **kwargs
    ):
        super(Simulation, self).__init__()
        self.use_template = use_template
        self.version = version
        self.verbose = verbose

        # Sets default parameters
        for key, value in default_parameters.items():
            setattr(self, key, value)

        # Sets override values to that provided in kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    @update_name
    @update_prepin_file_content
    def set_process_parameters(self, **kwargs):
        """
        Set process parameters for a given simulation

        @param power: Laser Power (W)
        @param velocity: Scan Velocity (m/s)
        @param beam_diameter: Beam Diameter (m) -> defaults to 1E-4 (100 µm)
        @param lens_radius: Lens Radius (m) -> defaults to 5E-5 (50 µm)
        @param spot_radius: Spot Radius (m) -> defaults to 5E-5 (50 µm)
        @param gauss_beam: Gaussian Beam (m) -> defaults to 5E-5/√2 (50/√2 µm)
        @param mesh_size: Mesh Size (m) -> defaults to 2E-5 (20 µm)
        @param mesh_x_start: Mesh X Start (m) -> defaults to 5E-4 m (500 µm)
        @param mesh_x_end: Mesh X End (m) -> defaults to 3E-3 m (3000 µm)
        @param mesh_y_start: Mesh Y Start (m) -> defaults to 0 m (0 µm)
        @param mesh_y_end: Mesh Y End (m) -> defaults to 6E-4 m (600 µm)
        @param mesh_z_start: Mesh Z Start (m) -> defaults to 0 m (0 µm)
        @param mesh_z_end: Mesh Z End (m) -> defaults to 6E-4 m (600 µm)
        @param fluid_region_x_start: Fluid back boundary (default 0 µm)
        @param fluid_region_x_end: Fluid front boundary (default 2800 µm)
        @param fluid_region_y_start: Fluid left boundary (default 0 µm)
        @param fluid_region_y_end: Fluid right boundary (default 600 µm)
        @param fluid_region_z_start: Fluid bottom boundary (default 0 µm)
        @param fluid_region_z_end: Fluid top boundary (default 400 µm)
        @return
        """

        # TODO: Add min / max checks.
        # TODO: Handle auto-generation of gauss_beam parameter
        for key, value in kwargs.items():
            if key in default_parameters.keys():
                # Integer values
                if key in ["power"]:
                    setattr(self, key, int(value))

                # converts everything else to float.
                else:
                    setattr(self, key, float(value))

    def generate_name_v0(
        self,
        power = None,
        velocity = None,
        beam_diameter = None,
        mesh_size = None
    ):
        if power is not None:
            p = f"{int(power)}".zfill(4)
        else:
            p = f"{self.power}".zfill(4)

        if velocity is not None:
            v = f"{float(velocity)}".zfill(4)
        else:
            v = f"{self.velocity}".zfill(4)

        if beam_diameter is not None:
            b_d = f"{Decimal(beam_diameter):.1E}".zfill(5)
        else:
            b_d = f"{Decimal(self.beam_diameter):.1E}".zfill(5)

        if mesh_size is not None:
            m_s = f"{Decimal(mesh_size):.1E}".zfill(5)
        else:
            m_s = f"{Decimal(self.mesh_size):.1E}".zfill(5)

        return f"0_{p}_{v}_{b_d}_{m_s}"
   
