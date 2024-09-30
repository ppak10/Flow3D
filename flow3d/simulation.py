import os

from decimal import Decimal
from flow3d.parameters import default_parameters
from flow3d.prepin import Prepin

class Simulation(Prepin):
    """
    Simulation object for Flow3D
    """

    def __lt__(self, other):
        return self.name < other.name

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
        self.status = {
            "completed": False,
        }
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
    
    def check_status(self, simulation_dir_path):
        """
        Provides status object of simulation. 
        """
        # Check if simulation is done by reading `report.simulation`
        # Last lines of `report.simulation` should look something like this.
        # 
        # > restart and spatial data available at t= 9.95003E-04
        # > restart and spatial data available at t= 1.00001E-03
        # > 
        # > end of calculation at   t =    1.00001E-03,     cycle =   44577
        # >  normal completion                                          
        # >
        # >
        # > flsgrf.simulation file size:   29 gb
        # >
        # > elapsed time =    5.67105E+03 seconds, or
        # >                   0 days :  1 hours : 34 minutes : 31 seconds
        # >
        # >     cpu time =    1.79030E+05 seconds

        status = {
            "exists": False,
            "completed": False,
            "run_simulation_completed": False,
            "post_process_create_flslnk_completed": False,
            "post_process_create_chunks_completed": False
        }

        # Check generated report file.
        report_file_path = os.path.join(simulation_dir_path, "report.simulation")

        # if os.path.exists(report_file_path):

        #     with open(report_file_path, "r") as f:
        #         last_line = f.readlines()[-1].strip()

        #     if "cpu time" in last_line.lower():
        #         # Last line should be cpu time if simulation is completed
        #         status["completed"] = True

        # Check execution times files to see if finished zipping flsgrf file.
        # execution_times_file_path = os.path.join(simulation_dir_path, "execution_times.txt")
        chunks_dir_path = os.path.join(simulation_dir_path, "chunks")

        if os.path.exists(simulation_dir_path):

            # with open(execution_times_file_path, "r") as f:
            #     execution_times = f.read()

            # flsgrf_file_path can exist during simulation 
            # flsgrf_file_path = os.path.join(simulation_dir_path, "flsgrf.simulation")
            flsgrf_zip_file_path = os.path.join(simulation_dir_path, "flsgrf.zip")
            if os.path.exists(flsgrf_zip_file_path):
                # Indicates that job method for running simulation is done.
                status["run_simulation_completed"] = True

            # Can't trust execution times.
            # if "post_process_create_flslnk" in execution_times:
            flslnk_tmp_file_path = os.path.join(simulation_dir_path, "flslnk.tmp")
            flslnk_zip_file_path = os.path.join(simulation_dir_path, "flslnk.zip")
            if os.path.exists(flslnk_tmp_file_path) or \
                os.path.exists(flslnk_zip_file_path):
                # Indicates that flslnk file has been created.
                status["post_process_create_flslnk_completed"] = True

            if os.path.isdir(chunks_dir_path) and len(os.listdir(chunks_dir_path)):
                # Indicates that chunks from flslnk file has been created.
                status["post_process_create_chunks_completed"] = True
        
        return status

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
