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
        self.mesh_size = None

        # Process Parameters (centimeter-gram-second)
        self.power_cgs = None
        self.velocity_cgs = None
        self.lens_radius_cgs = None
        self.spot_radius_cgs = None
        self.beam_diameter_cgs = None
        self.mesh_size_cgs = None

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
            # self.name = self[f"generate_name_v{self.version}"]()

            return result

        return wrapper

    @update_name
    def set_process_parameters(
        self,
        power,
        velocity,
        mesh_size = 2E-5,
        lens_radius = 5E-5,
        spot_radius = 5E-5,
    ):
        """
        Set process parameters for a given simulation

        @param power: Laser Power (W)
        @param velocity: Scan Velocity (m/s)
        @param mesh_size: Mesh Size (m) -> defaults to 2E-5 (20 µm)
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
        self.mesh_size = mesh_size

        # Conversion to centimeter-gram-second

        # 1 erg = 1 cm^2 * g * s^-2
        # 1 J = 10^7 ergs -> 1 W = 10^7 ergs/s
        self.power_cgs = self.power * 1E7

        # 1 m/s = 100 cm/s
        self.velocity_cgs = self.velocity * 100

        # 5E-5 m = 5E-3 cm
        self.lens_radius_cgs = self.lens_radius * 1E2
        self.spot_radius_cgs = self.spot_radius * 1E2
        self.mesh_size_cgs = self.mesh_size * 1E2
        self.beam_diameter_cgs = self.beam_diameter * 1E2

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
    
