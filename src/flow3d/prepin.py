import numpy as np
import os
import pandas as pd
import warnings

template_id_types = ["UNS"]

class Prepin():
    """
    Class for creating prepin files given process parameters.
    """

    def __init__(
        self,
        prepin_dir="prepin",
        keep_in_memory = False,
        verbose = True,
    ):
        self.current_dir = os.path.dirname(__file__)
        self.templates_dir_path = os.path.join(self.current_dir, "template")
        self.verbose = verbose
        self.keep_in_memory = keep_in_memory

        # Prepin
        self.prepin_dir_path = prepin_dir
        self.prepin_dir = prepin_dir

    def build_from_template(
        self,
        template_id,
        power,
        velocity,
        mesh_size = 0.002,
        lens_radius = 0.005,
        spot_radius = 0.005,
        template_id_type = "UNS",
        keep_in_memory = False,
    ):
        """
        Creates prepin file for given material template for a single set of
        process parameter configurations.

        @param id: Material Identifier
        @param power: Laser Power (W)
        @param velocity: Scan Velocity (m/s)
        @param mesh_size: Mesh Size (cm) -> defaults to 0.002 cm (20 µm)
        @param lens_radius: Lens Radius (cm) -> defaults to 0.005 cm (50 µm)
        @param spot_radius: Spot Radius (cm) -> defaults to 0.005 cm (50 µm)
        @param id_type: Identifier Type -> defaults to 'UNS'
        @return
        """
        # Check template id type
        if template_id_type not in template_id_types:
            raise Exception(f"""
'{template_id_type}'is not a valid `template_id_type`.
Please select one of `{template_id_types}`.
""")


        # Load Template File
        template_filename = f"{template_id_type}_{template_id}.txt"

        if template_id_type in ["UNS"]:
            # Use the 'material' template folder
            template_file_path = os.path.join(self.templates_dir_path, "material", template_filename)
        else:
            warnings.warn(f"Not yet supported")

        if not os.path.isfile(template_file_path):
            raise Exception(f"Template {template_filename} does not exist.")

        # Create Prepin Output Directory
        if not self.keep_in_memory and not keep_in_memory:
            if hasattr(self, "output_dir"):
                # Method is called from Flow3D class and output directory exists.
                if self.job_dir_path is None:
                    raise Exception("No job created, run `create_job()` first.")
                else:
                    self.prepin_dir_path = os.path.join(self.job_dir_path, "prepin")

                    # Creates prepin folder within job folder if non-existent.
                    if not os.path.isdir(self.prepin_dir_path):
                        os.makedirs(self.prepin_dir_path)
                    else:
                        warnings.warn(f"""
Prepin folder for job `{self.job_name}` already exists.
Following operations will overwrite existing files within folder.
""")
            else:
                # Method is called directly from Prepin class.
                # Creates prepin folder if non-existent.
                if not os.path.isdir(self.prepin_dir_path):
                    os.makedirs(self.prepin_dir_path)
                else:
                    warnings.warn(f"""
Prepin folder already exists.
Following operations will overwrite existing files within folder.
""")
                

        # Print out arguments for build from template
        if self.verbose:
            print(f"""
Creating prepin file...
Template File: {template_filename}
Material ({template_id_type}): {template_id}
Power: {power} W,
Velocity: {velocity} m/s
Mesh Size: {mesh_size} m
Lens Radius: {lens_radius} m
Spot Radius: {spot_radius} m
""")

        # Check Power Arugment
        if isinstance(power, list):
            for p in power:
                if not isinstance(p, int) and not isinstance(p, float):
                    raise Exception(f"`power` input must be either int or float or list of int or float")
            powers = power
        elif isinstance(power, int) or isinstance(power, float):
            powers = [power]
        else:
            raise Exception(f"`power` input must be either int or float or list of int or float")

        # Check Velocity Argument
        if isinstance(velocity, list):
            for v in velocity:
                if not isinstance(v, int) and not isinstance(v, float):
                    raise Exception(f"`velocity` input must be either int or float or list of int or float")
            velocities = velocity 
        elif isinstance(velocity, int) or isinstance(velocity, float):
            velocities = [velocity]
        else:
            raise Exception(f"`velocity` input must be either int or float or list of int or float")

        # Compile `prepin` files.
        for power in powers:
            for velocity in velocities:
                # Update Template File
                power_cgs = power * 1e7
                velocity_cgs = velocity * 100

                power_text = str(power_cgs/1e9) + "e9"
                velocity_text = f"{velocity_cgs:.2f}"

                with open(template_file_path) as file:
                    template = file.read()

                content = template.replace("<POWER>", power_text) 
                content = content.replace("<VELOCITY>", velocity_text) 
                content = content.replace("<LENS_RADIUS>", f"{lens_radius}") 
                content = content.replace("<SPOT_RADIUS>", f"{spot_radius}") 
                content = content.replace("<MESH_SIZE>", str(mesh_size)) 

                # # Save Updated Template File
                # simulation_filename = f"prepin.power_{power}_W_velocity_{velocity}_m_per_s_mesh_size_{mesh_size}_cm"
                # simulation_file_path = os.path.join(self.prepin_dir_path, simulation_filename)
                # with open(simulation_file_path, "w") as file:
                #     file.write(content)
                # if self.verbose: print(f"simulation_file_path: {simulation_file_path}")

        return self.prepin_dir_path
