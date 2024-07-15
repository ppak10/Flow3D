
class Simulation():
    """
    Simulation object for Flow3D
    """

    def __init__(self, name = None, version = 0):
        self.version = version
        self.name = name

        # Process Parameters
        self.power = None
        self.velocity = None
        self.lens_radius = None
        self.spot_radius = None
        self.beam_diameter = None
        self.mesh_size = None
    
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
        mesh_size = 0.002,
        lens_radius = 0.005,
        spot_radius = 0.005,
    ):
        """
        Set process parameters for a given simulation

        @param power: Laser Power (W)
        @param velocity: Scan Velocity (m/s)
        @param mesh_size: Mesh Size (cm) -> defaults to 0.002 cm (20 µm)
        @param lens_radius: Lens Radius (cm) -> defaults to 0.005 (50 µm)
        @param spot_radius: Spot Radius (cm) -> defaults to 0.005 (50 µm)
        @return
        """

        # TODO: Add min / max checks.
        self.power = int(power)
        self.velocity = float(velocity)
        self.lens_radius = float(lens_radius)
        self.spot_radius = float(spot_radius)
        self.beam_diameter = spot_radius * 2

        self.mesh_size = mesh_size

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
            b_d = f"{float(beam_diameter) * 1E3}E-5".zfill(5)
        else:
            b_d = f"{self.beam_diameter * 1E3}E-5".zfill(5)

        if mesh_size is not None:
            m_s = f"{float(mesh_size) * 1E3}E-5".zfill(5)
        else:
            m_s = f"{self.mesh_size * 1E3}E-5".zfill(5)

        return f"0_{p}_{v}_{b_d}_{m_s}"
    
