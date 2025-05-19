import multiprocessing
import numpy as np
import os

from tqdm import tqdm

from flow3d.simulation.utils.decorators import SimulationUtilsDecorators

# TODO: Handle with class (maybe parameters)
COLUMNS_CONFIG = {
    "pressure": {
        "cmap": "viridis",
        "clim": [0, 10000],
        "title": "Pressure"
    },
    "temperature": {
        "cmap": "plasma",
        # "clim": [1873, 5000], # Ti-6Al-4V
        # "clim":[1697, 3000], # SS316L
        "clim":[1000, 3000], # SS316L
        "title": "Temperature"
    },
    "fraction_of_fluid": {
        "cmap": "viridis",
        "clim": [0, 1],
        "title": "Fraction of Fluid"
    },
    "liquid_label": {
        "cmap": "viridis",
        "clim": [0, 100],
        "title": "Liquid Label"
    },
}

class SimulationView():
    """
    Methods to slice and rotate meshes of flsnk `.npz` files for visualization,
    and measurement.
    """
    @SimulationUtilsDecorators.change_working_directory 
    def prepare_views(
        self,
        views = ["isometric", "cross_section_xy", "cross_section_xz", "cross_section_yz"],
        npz_dir_path = "flslnk_npz",
        regenerate_mesh_x_y_z = False,
        **kwargs
    ):
        """
        Initialize view folders, unzip npz folder, and create `mesh_x_y_z` file.
        """

        # Initialize visualize folders.
        if not os.path.exists("views"):
            os.makedirs("views")

        # Create views folder and view subfolders.
        for view in views:

            # Create parent visual folder
            view_folder = f"views/{view}"
            if not os.path.exists(view_folder):
                os.makedirs(view_folder)

            # Column subfolders
            for key in COLUMNS_CONFIG.keys():
                if not os.path.exists(f"{view_folder}/{key}"):
                    os.makedirs(f"{view_folder}/{key}")

        # Unzip npz files
        self.unzip_folder(f"{npz_dir_path}.zip", npz_dir_path)

        # Check if `mesh_x_y_z.npz exists` and create if not existant
        if not os.path.exists(f"mesh_x_y_z.npz") or regenerate_mesh_x_y_z:
            self.generate_mesh_x_y_z(npz_dir_path = npz_dir_path)

    @SimulationUtilsDecorators.change_working_directory 
    def generate_views(
            self,
            views = ["isometric", "cross_section_xy", "cross_section_xz", "cross_section_yz"],
            npz_dir_path = "flslnk_npz",
            num_proc = 1,
            **kwargs
        ):
        """
        Generates the `.npz` files for a specific view (i.e. `cross_section_x`)
        for all simulation timesteps.
        """

        for view in views:

            # View method for visualization.
            view_method = getattr(self, f"view_{view}")

            #TODO: Add checks
            if num_proc > 1:
                with multiprocessing.Pool(processes=num_proc) as pool:

                    for index, npz_file in tqdm(enumerate(sorted(os.listdir(npz_dir_path)))):
                        npz_data = np.load(f"{npz_dir_path}/{npz_file}")
                        example = {key: npz_data[key] for key in npz_data.keys()}
                        pool.apply_async(
                            view_method,
                            args=(example, index),
                            error_callback=self.error_callback,
                        )
                    pool.close()
                    pool.join()
        
            else:
                for index, npz_file in tqdm(enumerate(sorted(os.listdir(npz_dir_path)))):
                    npz_data = np.load(f"{npz_dir_path}/{npz_file}")
                    example = {key: npz_data[key] for key in npz_data.keys()}
                    view_method(example, index)

    def view_cross_section_xz(self, example, index):
        """
        Generates the cross_section along the x axis, cut with xz plane, using y
        axis midpoint. Assumes that the working directory is the changed to the
        simulation
        """
        mesh_x_y_z = np.load("mesh_x_y_z.npz")
        mesh_y = mesh_x_y_z["y"]
        midpoint = len(mesh_y) // 2

        for key, configs in COLUMNS_CONFIG.items():
            values = np.array(example[key][0])

            cropped_array = self.crop_3d_array(values,
                crop_y=(midpoint, midpoint + 1)
            )

            index_string = f"{index}".zfill(4)
            rotated_array = cropped_array.squeeze()[::-1, ::-1]

            np.savez_compressed(
                f"views/cross_section_xz/{key}/{index_string}.npz",
                data=rotated_array
            )
        
    def view_cross_section_yz(self, example, index):
        """
        Generates the cross_section along the y axis, cut with the yz plane,
        using x axis midpoint. Assumes that the working directory is the
        changed to the simulation
        """
        mesh_x_y_z = np.load("mesh_x_y_z.npz")
        mesh_x = mesh_x_y_z["x"]

        midpoint = len(mesh_x) // 2

        for key, configs in COLUMNS_CONFIG.items():
            cropped_array = self.crop_3d_array(
                np.array(example[key][0]),
                crop_x=(midpoint, midpoint + 1)
            )

            index_string = f"{index}".zfill(4)
            rotated_array = cropped_array.squeeze()[::-1, ::-1]

            np.savez_compressed(
                f"views/cross_section_yz/{key}/{index_string}.npz",
                data=rotated_array
            )

    def view_cross_section_xy(self, example, index):
        """
        Generates the cross_section along the x axis, cut with the xy plane,
        from `fluid_region_z_end`.
        Assumes that the working directory is the changed to the simulation
        """
        top_of_fluid = int(self.fluid_region_z_end // self.mesh_size) - 1

        for key, configs in COLUMNS_CONFIG.items():
            values = np.array(example[key][0])
            # print(f"values.shape: {values.shape}")
            cropped_array = self.crop_3d_array(
                values,
                crop_z=(top_of_fluid, top_of_fluid + 1)
            )
            # print(f"cropped_array.shape: {cropped_array.shape}")

            index_string = f"{index}".zfill(4)
            rotated_array = cropped_array.squeeze()[::-1, ::-1]

            np.savez_compressed(
                f"views/cross_section_xy/{key}/{index_string}.npz",
                data=rotated_array
            )

    def view_isometric(self, example, index, **kwargs):

        for key, configs in COLUMNS_CONFIG.items():
            if key == "temperature":

                values = np.array(example[key][0])
                mesh = np.transpose(values, (2, 1, 0))  # Transpose to match voxel orientation

                index_string = f"{index}".zfill(4)

                np.savez_compressed(
                    f"views/isometric/{key}/{index_string}.npz",
                    data=mesh
                )