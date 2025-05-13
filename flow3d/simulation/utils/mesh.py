import numpy as np
import os

class SimulationUtilsMesh():
    """
    Utility functions related to simulation mesh parameters
    """

    # TODO: Consider if it better to move this to a new class file specific to
    # `flslnk` related methods.
    def generate_mesh_x_y_z(self, npz_dir_path = "flslnk_npz"):
        """
        Generates a `.npz` file with `x`, `y`, and `z` keys and values
        indicating the equivalent distance of each voxel (tick) in cm.
        """

        # Unzip npz files if not already unzipped
        self.unzip_folder(f"{npz_dir_path}.zip", npz_dir_path)

        npz_files = os.listdir(npz_dir_path)

        if len(npz_files):
            first_npz_filename = npz_files[0]

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
        else:
            print("Could not generate mesh_x_y_z.npz")
