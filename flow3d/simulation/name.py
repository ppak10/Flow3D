from decimal import Decimal

class SimulationName():
    """
    Class for handling simulation name
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

    def __init__(self, name = None, filename = "simulation", **kwargs):
        self.name = name
        self.filename = filename

        if type(name) == str:
            self.name = name
        else:
            # Generate `self.name` using specific `self.version`.
            self.name = getattr(self, f"generate_name_v{self.version}")()
        
        super().__init__(**kwargs)

    def generate_name_v0(
        self,
        power = None,
        velocity = None,
        temperature_initial = None,
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

        if temperature_initial is not None:
            t_i = f"{float(temperature_initial)}".zfill(6)
        else:
            t_i = f"{self.temperature_initial}".zfill(6)

        if beam_diameter is not None:
            b_d = f"{Decimal(beam_diameter):.1E}".zfill(5)
        else:
            b_d = f"{Decimal(self.beam_diameter):.1E}".zfill(5)

        if mesh_size is not None:
            m_s = f"{Decimal(mesh_size):.1E}".zfill(5)
        else:
            m_s = f"{Decimal(self.mesh_size):.1E}".zfill(5)

        return f"0_{p}_{v}_{t_i}_{b_d}_{m_s}"
    
    # TODO: Add class to turn name to parameters
