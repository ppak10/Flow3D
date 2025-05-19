import imageio
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import os

from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap, ScalarMappable
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

class SimulationVisualizations():

    # TODO: Make into decorator
    @SimulationUtilsDecorators.change_working_directory 
    def prepare_view_visualizations(
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
        if not os.path.exists("visualizations"):
            os.makedirs("visualizations")

        # Create view folder and subfolders.
        for view in views:

            # Create parent visual folder
            view_folder = f"visualizations/{view}"
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

    # TODO: Consider renaming this to `generate_view_visualizations`.
    @SimulationUtilsDecorators.change_working_directory 
    def generate_views_visualizations(
        self,
        views = ["isometric", "cross_section_xy", "cross_section_xz", "cross_section_yz"],
        npz_dir_path = "flslnk_npz",
        num_proc = 1,
        **kwargs
    ):
        print(f"""\n
################################################################################
Visualize Views: `{self.name}`
################################################################################
""")
        for view in views:

            # View method for visualization.
            if view in ["cross_section_xy", "cross_section_xz", "cross_section_yz"]:
                view_method = getattr(self, f"view_visualization_cross_section")
            else:
                view_method = getattr(self, f"view_visualization_isometric")

            #TODO: Add checks
            if num_proc > 1:
                with multiprocessing.Pool(processes=num_proc) as pool:


                    for index, npz_file in tqdm(enumerate(sorted(os.listdir(npz_dir_path)))):
                        npz_data = np.load(f"{npz_dir_path}/{npz_file}")
                        example = {key: npz_data[key] for key in npz_data.keys()}
                        pool.apply_async(
                            view_method,
                            args=(view, example, index),
                            error_callback=self.error_callback,
                        )
                    pool.close()
                    pool.join()

            else:
                for index, npz_file in tqdm(enumerate(sorted(os.listdir(npz_dir_path)))):
                    npz_data = np.load(f"{npz_dir_path}/{npz_file}")
                    example = {key: npz_data[key] for key in npz_data.keys()}
                    view_method(view, example, index)

            print("Compiling images to `.gif`...")

            view_folder = f"visualizations/{view}"
            column_folders = sorted(os.listdir(f"{view_folder}"))

            # Iterates through column folders within images
            # i.e. "pressure", "temperature", "fraction_of_fluid", etc.
            for column_folder in tqdm(column_folders):
                column_folder_path = f"{view_folder}/{column_folder}"

                if os.path.isdir(column_folder_path):
                    frames = []
                    for image_file in sorted(os.listdir(column_folder_path)):
                        image = imageio.imread(f"{column_folder_path}/{image_file}")
                        frames.append(image)

                    # Only compile .gif for folders with images. 
                    if len(frames) > 0:
                        imageio.mimsave(f"{view_folder}/{column_folder}.gif", frames, fps = 10, loop = 0)

    # TODO: Include more information in visualization
    # TODO: Make colorbar consistent throughout frames.
    def view_visualization_cross_section(self, view, example, index):
        """
        Generates visualization of 2D cross section view.
        """
        power, velocity = example["power"][0], example["velocity"][0]

        for key, configs in COLUMNS_CONFIG.items():
            index_string = f"{index}".zfill(4)

            view_file = f"views/{view}/{key}/{index_string}.npz"
            if os.path.exists(view_file):
                view_data = np.load(view_file)

                plt.figure()
                plt.imshow(view_data["data"], cmap=configs["cmap"])
                plt.title(f"{configs['title']} ({power} W, {velocity} m/s)")
                plt.colorbar()
                plt.savefig(f"visualizations/{view}/{key}/{index_string}.png")
                plt.close()

    def view_visualization_isometric(self, view, example, index, **kwargs):
        for key, configs in COLUMNS_CONFIG.items():
            if key == "temperature":
                power, velocity = example["power"][0], example["velocity"][0]
                title = f"{configs['title']} ({power} W, {velocity} m/s)"

                # Prepare the grid data for plotting
                values = np.array(example[key][0])
                mesh = np.transpose(values, (2, 1, 0))  # Transpose to match voxel orientation

                index_string = f"{index}".zfill(4)

                view_file = f"views/{view}/{key}/{index_string}.npz"
                if os.path.exists(view_file):
                    view_data = np.load(view_file)
                    data = view_data["data"]

                    threshold = configs["clim"][0]
                    voxels = data > threshold  # Apply threshold to create a binary voxel structure


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

                    # Save or display each plot
                    plt.savefig(f"visualizations/isometric/{key}/{index_string}.png")
                    plt.close(fig)