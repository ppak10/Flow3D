import imageio
import multiprocessing
import matplotlib.pyplot as plt
import numpy as np
import os
import zipfile

from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap, ScalarMappable
from tqdm import tqdm

from .utils import SimulationUtils

COLUMNS_CONFIG = {
    "pressure": {
        "cmap": "viridis",
        "clim": [0, 10000],
        "title": "Pressure"
    },
    "temperature": {
        "cmap": "plasma",
        # "clim": [1873, 5000], # Ti-6Al-4V
        "clim":[1697, 3000], # SS316L
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

class SimulationVisualization():
    # def __init__(
    #         self,
    #         views = ["isometric", "cross_section_x, cross_section_y"],
    #         **kwargs
    #     ):
    #     self.views = views

    #     super().__init__(**kwargs)

    # def run_visualize(
    #         self,
    #         views = ["isometric", "cross_section_x", "cross_section_y"],
    #         # views = ["cross_section_x"],
    #         regenerate_mesh_x_y_z = False,
    #         num_proc = 1,
    #     ):
    #     """
    #     Runs post processing method with or without multiprocessing.
    #     """

    #     for simulation in tqdm(sorted(self.simulations)):
    #         s_dir_path = os.path.join(self.job_dir_path, simulation.name)
    #         simulation_status = simulation.check_status(s_dir_path)
    #         if simulation_status["post_process_create_npz_completed"]:
    #             print(f"Preparing visualization for {simulation.name}...")
    #             self.prepare_visualize(
    #                 regenerate_mesh_x_y_z = regenerate_mesh_x_y_z,
    #                 working_dir = s_dir_path
    #             )

    #             print(f"Creating visualization files {simulation.name}...")
    #             for view in views:
    #                 self.visualize(
    #                     simulation,
    #                     view,
    #                     num_proc,
    #                     working_dir = s_dir_path
    #                 )

    @SimulationUtils.change_working_directory 
    def prepare_visualization(
        self,
        views = ["isometric", "cross_section_x", "cross_section_y"],
        npz_dir_path = "flslnk_npz",
        regenerate_mesh_x_y_z = False,
        **kwargs
    ):
        """
        Initialize view folders, unzip npz folder, and create mesh_x_y_z file.
        """

        # Initialize visualize folders.
        if not os.path.exists("visualize"):
            os.makedirs("visualize")

        # Create view folder and subfolders.
        for view in views:

            # Create parent visual folder
            view_folder = f"visualize/{view}"
            if not os.path.exists(view_folder):
                os.makedirs(view_folder)

            # Create subfolders
            for subfolder in ["images", "npz"]:
                if not os.path.exists(f"{view_folder}/{subfolder}"):
                    os.makedirs(f"{view_folder}/{subfolder}")

                # Column subfolders
                for key in COLUMNS_CONFIG.keys():
                    if not os.path.exists(f"{view_folder}/{subfolder}/{key}"):
                        os.makedirs(f"{view_folder}/{subfolder}/{key}")

        # Unzip npz files
        if not os.path.exists(npz_dir_path):
            if os.path.exists(f"{npz_dir_path}.zip"):
                os.makedirs(npz_dir_path)
                with zipfile.ZipFile(f"{npz_dir_path}.zip", "r") as zip_ref:
                    zip_ref.extractall(npz_dir_path)
            else:
                raise FileNotFoundError(f"`{npz_dir_path}.zip` file not found")

        # Check if mesh_x_y_z.npz exists and create if not existant
        if not os.path.exists(f"mesh_x_y_z.npz") or regenerate_mesh_x_y_z:
            first_npz_filename = os.listdir(npz_dir_path)[0]
            row_dict = np.load(f"{npz_dir_path}/{first_npz_filename}")
            mesh_x_y_z = row_dict["x_y_z"][0]
            mesh_x_y_z_shape = np.array(mesh_x_y_z).shape

            mesh_z_length = mesh_x_y_z_shape[0]
            mesh_y_length = mesh_x_y_z_shape[1]
            mesh_x_length = mesh_x_y_z_shape[2]

            mesh_z = []
            mesh_y = []
            mesh_x = []

            for mesh_z_index in range(mesh_z_length):
                mesh_z.append(mesh_x_y_z[mesh_z_index][0][0][2])

            for mesh_y_index in range(mesh_y_length):
                mesh_y.append(mesh_x_y_z[0][mesh_y_index][0][1])

            for mesh_x_index in range(mesh_x_length):
                mesh_x.append(mesh_x_y_z[0][0][mesh_x_index][0])

            np.savez("mesh_x_y_z.npz", x=mesh_x, y=mesh_y, z=mesh_z)

    @SimulationUtils.change_working_directory 
    def generate_visualization_view(
        self,
        view,
        npz_dir_path = "flslnk_npz",
        num_proc = 1,
        **kwargs
    ):
        print(f"""\n
################################################################################
Visualize (`{view}`): `{self.name}`
################################################################################
""")
        # View method for visualization.
        view_method = getattr(self, f"generate_{view}")

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
                view_method(example, index, working_dir=self.name)

        print("Compiling images to `.gif`...")

        # visualize_dir_path = os.path.join(self.job_dir_path, self.name, "visualize")
        visualize_dir_path = "visualize"
        view_folder = f"{visualize_dir_path}/{view}"

        # Iterates through column folders within images
        # i.e. "pressure", "temperature", "fraction_of_fluid", etc.
        for column_folder in tqdm(sorted(os.listdir(f"{view_folder}/images"))):
            column_folder_path = f"{view_folder}/images/{column_folder}"

            if os.path.isdir(column_folder_path):
                frames = []
                for image_file in sorted(os.listdir(column_folder_path)):
                    image = imageio.imread(f"{column_folder_path}/{image_file}")
                    frames.append(image)

                # Only compile .gif for folders with images. 
                if len(frames) > 0:
                    imageio.mimsave(f"{view_folder}/images/{column_folder}.gif", frames, fps = 10, loop = 0)

    def generate_cross_section_x(self, example, index):
        """
        Generates the cross_section along the x axis, using y axis midpoint.
        Assumes that the working directory is the changed to the simulation
        """
        mesh_x_y_z = np.load("mesh_x_y_z.npz")
        mesh_y = mesh_x_y_z["y"]
        # print(len(mesh_y))

        power, velocity = example["power"][0], example["velocity"][0]
        midpoint = len(mesh_y) // 2
        # midpoint = 50 

        for key, configs in COLUMNS_CONFIG.items():
            values = np.array(example[key][0])
            # print(f"values.shape: {values.shape}")

            cropped_array = SimulationUtils.crop_3d_array(values,
                crop_y=(midpoint, midpoint + 1)
            )
            # print(f"cropped_array.shape: {cropped_array.shape}")


            index_string = f"{index}".zfill(4)
            rotated_array = cropped_array.squeeze()[::-1, ::-1]

            np.savez_compressed(f"visualize/cross_section_x/npz/{key}/{index_string}.npz", data=rotated_array)

            plt.figure()
            plt.imshow(rotated_array, cmap=configs["cmap"])
            plt.title(f"{configs['title']} ({power} W, {velocity} m/s)")
            plt.colorbar()
            plt.savefig(f"visualize/cross_section_x/images/{key}/{index_string}.png")
            plt.close()
        
    def generate_cross_section_y(self, example, index):
        """
        Generates the cross_section along the y axis, using x axis midpoint.
        Assumes that the working directory is the changed to the simulation
        """
        mesh_x_y_z = np.load("mesh_x_y_z.npz")
        mesh_x = mesh_x_y_z["x"]
        # print(len(mesh_x))

        power, velocity = example["power"][0], example["velocity"][0]
        midpoint = len(mesh_x) // 2

        # mappable = ScalarMappable(norm=norm, cmap=cmap)
        # mappable.set_array([])  # This line is necessary to avoid errors

        # # Add the color bar to the figure
        # cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10)
        # cbar.set_label(key)

        for key, configs in COLUMNS_CONFIG.items():
            values = np.array(example[key][0])
            # print(f"values.shape: {values.shape}")
            cropped_array = SimulationUtils.crop_3d_array(
                np.array(example[key][0]),
                crop_x=(midpoint, midpoint + 1)
            )
            # print(f"cropped_array.shape: {cropped_array.shape}")

            index_string = f"{index}".zfill(4)
            rotated_array = cropped_array.squeeze()[::-1, ::-1]

            np.savez_compressed(f"visualize/cross_section_y/npz/{key}/{index_string}.npz", data=rotated_array)

            plt.figure()
            plt.imshow(rotated_array, cmap=configs["cmap"])
            plt.title(f"{configs['title']} ({power} W, {velocity} m/s)")
            plt.colorbar()
            plt.savefig(f"visualize/cross_section_y/images/{key}/{index_string}.png")
            plt.close()

    def generate_isometric(self, example, index, **kwargs):

        for key, configs in COLUMNS_CONFIG.items():
            if key == "temperature":
                power, velocity = example["power"][0], example["velocity"][0]
                title = f"{configs['title']} ({power} W, {velocity} m/s)"

                # Prepare the grid data for plotting
                values = np.array(example[key][0])
                mesh = np.transpose(values, (2, 1, 0))  # Transpose to match voxel orientation
                threshold = configs["clim"][0]
                voxels = mesh > threshold  # Apply threshold to create a binary voxel structure

                norm = Normalize(vmin=configs["clim"][0], vmax=configs["clim"][1])
                cmap = get_cmap(configs["cmap"])

                normalized_colors = cmap(norm(mesh))
        
                # Plot using Matplotlib's voxels
                fig = plt.figure(figsize=(10, 10))
                ax = fig.add_subplot(projection='3d')
                ax.voxels(
                    voxels,
                    facecolors=normalized_colors,
                    edgecolors=np.clip(2 * normalized_colors - 0.5, 0, 1),
                    linewidth=0.5
                )

                x_dim, y_dim, z_dim = voxels.shape  # Dimensions of the voxel grid

                ax.set_xlim([0, x_dim])
                ax.set_ylim([0, y_dim])
                ax.set_zlim([0, z_dim])

                # Set tick markers every 10 units
                ax.set_xticks(np.arange(0, x_dim + 1, 10))
                ax.set_yticks(np.arange(0, y_dim + 1, 10))
                ax.set_zticks(np.arange(0, z_dim + 1, 10))

                ax.set(xlabel='X', ylabel='Y', zlabel='Z')
                ax.set_title(title)


                # Calculate the maximum extent for equal aspect ratio
                max_extent = max(x_dim, y_dim, z_dim)

                # Center and scale each axis to have equal aspect ratio
                ax.set_box_aspect((x_dim / max_extent, y_dim / max_extent, z_dim / max_extent))
                # ax.set_aspect('auto')

                # Add color bar
                # Create a ScalarMappable to use with the color bar
                mappable = ScalarMappable(norm=norm, cmap=cmap)
                mappable.set_array([])  # This line is necessary to avoid errors

                # Add the color bar to the figure
                cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10)
                cbar.set_label(key)

                index_string = f"{index}".zfill(4)
                # Save or display each plot
                plt.savefig(f"visualize/isometric/images/{key}/{index_string}.png")
                plt.close(fig)

