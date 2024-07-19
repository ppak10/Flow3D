from decimal import Decimal

class Simulation():
    """
    Simulation object for Flow3D
    """

    def __init__(self, name = None, version = 0):
        self.version = version
        self.name = name

        # Process Parameters (meter-gram-second)
        self.power = None
        self.velocity = None
        self.lens_radius = None
        self.spot_radius = None
        self.beam_diameter = None

        # Mesh
        self.mesh_size = None
        self.mesh_x_start = None
        self.mesh_x_end = None
        self.mesh_y_start = None
        self.mesh_y_end = None
        self.mesh_z_start = None
        self.mesh_z_end = None

        # Fluid Region
        self.fluid_region_x_start = None
        self.fluid_region_x_end = None
        self.fluid_region_y_start = None
        self.fluid_region_y_end = None
        self.fluid_region_z_start = None
        self.fluid_region_z_end = None

        # Prepin
        self.prepin = None
    
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

    @update_name
    def set_process_parameters(
        self,
        power,
        velocity,
        mesh_size = 2E-5,
        mesh_x_start = 5E-4,
        mesh_x_end = 3E-3,
        mesh_y_start = 0,
        mesh_y_end = 6E-4,
        mesh_z_start = 0,
        mesh_z_end = 6E-4,
        fluid_region_x_start = 0,
        fluid_region_x_end = 2.8E-3,
        fluid_region_y_start = 0,
        fluid_region_y_end = 6E-4, 
        fluid_region_z_start = 0,
        fluid_region_z_end = 4E-4, 
        lens_radius = 5E-5,
        spot_radius = 5E-5,
    ):
        """
        Set process parameters for a given simulation

        @param power: Laser Power (W)
        @param velocity: Scan Velocity (m/s)
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
        @param lens_radius: Lens Radius (m) -> defaults to 5E-5 (50 µm)
        @param spot_radius: Spot Radius (m) -> defaults to 5E-5 (50 µm)
        @return
        """

        # TODO: Add min / max checks.
        self.power = int(power)
        self.velocity = float(velocity)
        self.lens_radius = float(lens_radius)
        self.spot_radius = float(spot_radius)
        self.beam_diameter = spot_radius * 2
        self.mesh_size = float(mesh_size)
        self.mesh_x_start = float(mesh_x_start)
        self.mesh_x_end = float(mesh_x_end)
        self.mesh_y_start = float(mesh_y_start)
        self.mesh_y_end = float(mesh_y_end)
        self.mesh_z_start = float(mesh_z_start)
        self.mesh_z_end = float(mesh_z_end)
        self.fluid_region_x_start = fluid_region_x_start
        self.fluid_region_x_end = fluid_region_x_end
        self.fluid_region_y_start = fluid_region_y_start
        self.fluid_region_y_end = fluid_region_y_end
        self.fluid_region_z_start = fluid_region_z_start
        self.fluid_region_z_end = fluid_region_z_end

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
        else:
            # Converting to decimal handles case where 2.799 != 2.8
            parameter_decimal = Decimal(getattr(self, parameter) * 1E2)
            return float(round(parameter_decimal, 3))

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
    
