import imageio
import multiprocessing
import matplotlib.pyplot as plt
import numpy as np
import os
import zipfile

from tqdm import tqdm

from .utils import JobUtils

COLUMNS_CONFIG = {
    "pressure": {
        "cmap": "viridis",
        "title": "Pressure"
    },
    "temperature": {
        "cmap": "plasma",
        "title": "Temperature"
    },
    "fraction_of_fluid": {
        "cmap": "viridis",
        "title": "Fraction of Fluid"
    },
    "liquid_label": {
        "cmap": "viridis",
        "title": "Liquid Label"
    },
}

class JobVisualize():

    def run_visualize(self, num_proc = 1):
        """
        Runs post processing method with or without multiprocessing.
        """

        for simulation in tqdm(sorted(self.simulations)):
            s_dir_path = os.path.join(self.job_dir_path, simulation.name)
            simulation_status = simulation.check_status(s_dir_path)
            if simulation_status["post_process_create_npz_completed"]:
                print(f"Creating visualization files {simulation.name}...")
                self.visualize(simulation, num_proc)

    def visualize(self, simulation, num_proc = 1):
        print(f"""\n
################################################################################
Visualize: `{simulation.name}`
################################################################################
""")
        # Initialize visualize folders.
        visualize_dir_path = os.path.join(self.job_dir_path, simulation.name, "visualize")
        if not os.path.exists(visualize_dir_path):
            os.makedirs(visualize_dir_path)

        if not os.path.exists(f"{visualize_dir_path}/images"):
            os.makedirs(f"{visualize_dir_path}/images")

        if not os.path.exists(f"{visualize_dir_path}/npz"):
            os.makedirs(f"{visualize_dir_path}/npz")

        for key in COLUMNS_CONFIG.keys():
            if not os.path.exists(f"{visualize_dir_path}/images/{key}"):
                os.makedirs(f"{visualize_dir_path}/images/{key}")
            if not os.path.exists(f"{visualize_dir_path}/npz/{key}"):
                os.makedirs(f"{visualize_dir_path}/npz/{key}")

        # Unzip npz files
        npz_dir_path = os.path.join(self.job_dir_path, simulation.name, "npz")
        npz_zip_path = os.path.join(self.job_dir_path, simulation.name, "npz.zip")

        if not os.path.exists(npz_dir_path):
            if os.path.exists(npz_zip_path):
                os.makedirs(npz_dir_path)
                with zipfile.ZipFile(npz_zip_path, "r") as zip_ref:
                    zip_ref.extractall(npz_dir_path)
            else:
                raise FileNotFoundError(f"`npz.zip` file not found: {npz_zip_path}")
            
        # Check if mesh_x_y_z.npz exists and create if not existant
        if not os.path.exists(f"{self.job_dir_path}/{simulation.name}/mesh_x_y_z.npz"):
            first_npz_filename = os.listdir(npz_dir_path)[0]
            row_dict = np.load(f"{npz_dir_path}/{first_npz_filename}")
            mesh_x_y_z_path = os.path.join(self.job_dir_path, simulation.name, "mesh_x_y_z.npz") 
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

            np.savez(mesh_x_y_z_path, x=mesh_x, y=mesh_y, z=mesh_z)


        #TODO: Add checks
        if num_proc > 1:
            with multiprocessing.Pool(processes=num_proc) as pool:
                # for simulation in tqdm(sorted(self.simulations)):
                for index, npz_file in tqdm(enumerate(sorted(os.listdir(npz_dir_path)))):
                    example = np.load(f"{npz_dir_path}/{npz_file}")
                    extracted_data = {key: example[key] for key in example.keys()}
                    pool.apply_async(
                        self.generate_cross_section,
                        args=(extracted_data, index),
                        error_callback=self.error_callback,
                        kwds={
                            "working_dir": simulation.name
                        },
                    )
                pool.close()
                pool.join()
                
        else:
            for index, npz_file in tqdm(enumerate(sorted(os.listdir(npz_dir_path)))):
                example = np.load(f"{npz_dir_path}/{npz_file}")
                self.generate_cross_section(example, index, working_dir=simulation.name)

        print("Compiling images to `.gif`")
        for folder in tqdm(sorted(os.listdir(f"{visualize_dir_path}/images"))):
            folder_path = f"{visualize_dir_path}/images/{folder}"
            if os.path.isdir(folder_path):
                frames = []
                for image_file in sorted(os.listdir(folder_path)):
                    image = imageio.imread(f"{folder_path}/{image_file}")
                    frames.append(image)

                imageio.mimsave(f"{visualize_dir_path}/images/{folder}.gif", frames, fps = 10)

    def generate_cross_section(self, example, index, **kwargs):
        # print(example)
        # index = kwargs["index"]
        working_dir = kwargs["working_dir"]
        visualize_dir_path = os.path.join(self.job_dir_path, working_dir, "visualize")
        mesh = np.load(f"{self.job_dir_path}/{working_dir}/mesh_x_y_z.npz")
        mesh_x, mesh_y = mesh["x"], mesh["y"]
        # print(mesh_x, mesh_y)
        mesh_x_length, mesh_y_length = len(mesh_x), len(mesh_y)

        power, velocity, timestep = example["power"][0], example["velocity"][0], example["timestep"][0]
        x_distance_cm = JobUtils.x_distance(timestep, velocity)
        # print(x_distance_cm)
        mesh_index = JobUtils.find_index(x_distance_cm, mesh_x)
        # print(mesh_index)

        for key, configs in COLUMNS_CONFIG.items():
            cropped_array = JobUtils.crop_3d_array(
                np.array(example[key][0]),
                crop_x=(max(0, mesh_index - 50), min(mesh_index + 25, mesh_x_length)),
                crop_y=(mesh_y_length // 2, mesh_y_length // 2 + 1)
            )
            index_string = f"{index}".zfill(4)
            rotated_array = cropped_array.squeeze()[::-1, ::-1]

            np.savez_compressed(f"{visualize_dir_path}/npz/{key}/{index_string}.npz", data=rotated_array)

            plt.figure()
            plt.imshow(rotated_array, cmap=configs["cmap"])
            plt.title(f"{configs['title']} ({power} W, {velocity} m/s)")
            plt.colorbar()
            plt.savefig(f"{visualize_dir_path}/images/{key}/{index_string}.png")
            plt.close()
        
