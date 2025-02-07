import numpy as np
import os
import pandas as pd

from skimage import measure
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

class SimulationMeasurements():
    """
    Methods for obtaining simulation measurements
    """

    @SimulationUtilsDecorators.change_working_directory 
    def prepare_melt_pool_measurements(
        self,
        npz_dir_path = "flslnk_npz",
        regenerate_mesh_x_y_z = False,
        **kwargs,
    ):
        """
        Initialize view folders, unzip npz folder, and create `mesh_x_y_z` file.
        ```
        simulation/
        ├─ measurements/
        │  ├─ melt_pool/
        │  │  ├─ fraction_of_fluid/
        │  │  ├─ liquid_label/
        │  │  ├─ pressure/
        │  │  ├─ temperature/
        │  │  │  ├─ 00000001.npz
        │  │  ├─ temperature.csv
        ...
        ```
        """
        # Initialize visualize folders.
        if not os.path.exists("measurements"):
            os.makedirs("measurements")

        # Column subfolders
        for subfolder in ["melt_pool"]:
            if not os.path.exists(f"measurements/{subfolder}"):
                os.makedirs(f"measurements/{subfolder}")

            for key in COLUMNS_CONFIG.keys():
                if not os.path.exists(f"measurements/{subfolder}/{key}"):
                    os.makedirs(f"measurements/{subfolder}/{key}")

        # Unzip npz files
        self.unzip_folder(f"{npz_dir_path}.zip", npz_dir_path)

        # Check if `mesh_x_y_z.npz exists` and create if not existant
        if not os.path.exists(f"mesh_x_y_z.npz") or regenerate_mesh_x_y_z:
            self.generate_mesh_x_y_z(npz_dir_path = npz_dir_path)

    @SimulationUtilsDecorators.change_working_directory 
    def generate_melt_pool_measurements(
        self,
        npz_dir_path = "flslnk_npz",
        num_proc = 1,
        **kwargs,
    ):
        """
        Provides depth, width, and length measurements of melt pool based on
        output ("pressure", "temperature", "fraction_of_fluid") threshold.
        """
        print(f"""\n
################################################################################
Measurements: `{self.name}`
################################################################################
""")
        # #TODO: Add checks
        # if num_proc > 1:
        #     with multiprocessing.Pool(processes=num_proc) as pool:


        #         for index, npz_file in tqdm(enumerate(sorted(os.listdir(npz_dir_path)))):
        #             npz_data = np.load(f"{npz_dir_path}/{npz_file}")
        #             example = {key: npz_data[key] for key in npz_data.keys()}
        #             pool.apply_async(
        #                 self.generate_melt_pool_dimensions,
        #                 args=(example, index),
        #                 error_callback=self.error_callback,
        #             )
        #         pool.close()
        #         pool.join()

        # else:

        self.generate_melt_pool_dimensions(npz_dir_path = npz_dir_path)

    def generate_melt_pool_dimensions(self, npz_dir_path = "flslnk_npz"):
        """
        Provides depth, width, and length measurements of melt pool based on
        output ("pressure", "temperature", "fraction_of_fluid") threshold.
        """

        for key, configs in COLUMNS_CONFIG.items():

            data_rows = []

            if key == "temperature":

                for npz_file in tqdm(sorted(os.listdir(npz_dir_path))):
                    timestep = npz_file.split(".")[0]

                    npz_data = np.load(f"{npz_dir_path}/{npz_file}")
                    example = {key: npz_data[key] for key in npz_data.keys()}

                    power, velocity = example["power"][0], example["velocity"][0]

                    thresholded_data = np.copy(npz_data[key]).squeeze()
                    thresholded_data[thresholded_data <= configs["clim"][0]] = 0
                    thresholded_data[thresholded_data > configs["clim"][0]] = 1
                    thresholded_data_unique = np.unique(thresholded_data)

                    if len(thresholded_data_unique) > 1:
                        
                        data_dict = {
                            "timestep": timestep,
                            "beam_diameter": self.beam_diameter,
                            "mesh_size": self.mesh_size,

                            # Change to `self.material` when implemented
                            "material": self.template_id,
                            "power": power,
                            "velocity": velocity,
                            "depth_m": None,
                            "depth_px": None,
                            "length_m": None,
                            "length_px": None,
                            "width_m": None,
                            "width_px": None,
                        }

                        skimage_dict = {
                            "bbox_xy": (None, None, None, None),
                            "bbox_xz": (None, None, None, None),
                            "labels_all_xy": None,
                            "labels_all_xz": None,
                            "labels_max_blob_xy": None,
                            "labels_max_blob_xz": None,
                        }

                        # `0` is xy plane `1` is xz plane
                        for axis in [0, 1]:
                        
                            # Sum data along axis and apply threshold and transformations
                            thresholded_data_sum = np.sum(thresholded_data, axis = axis)
                            thresholded_data_sum = np.where(thresholded_data_sum > 0, 1, 0)
                            thresholded_data_sum = np.flip(thresholded_data_sum, axis=(0, 1))

                            # Measure and label blob regions
                            labels_all = measure.label(thresholded_data_sum)
                            regionprops = measure.regionprops(labels_all)

                            # Find the blob with the maximum area
                            blob_max_area = 0
                            for index, blob in enumerate(regionprops):
                                if blob.area > blob_max_area:
                                    blob_max_area_index = index
                                    blob_max_area = blob.area

                            blob_max = regionprops[blob_max_area_index]

                            # Remove other smaller blobs
                            labels_max_blob = np.where(labels_all == blob_max.label, 1, 0)

                            # Get the bounding box of the largest blob
                            min_row, min_col, max_row, max_col = blob_max.bbox
                            bbox_width = max_col - min_col
                            bbox_height = max_row - min_row

                            if axis == 0:
                                data_dict["width_m"] = bbox_height * self.mesh_size
                                data_dict["width_px"] = bbox_height
                                data_dict["length_m"] = bbox_width * self.mesh_size
                                data_dict["length_px"] = bbox_width

                                skimage_dict["bbox_xy"] = (min_row, min_col, max_row, max_col)
                                skimage_dict["labels_all_xy"] = labels_all
                                skimage_dict["labels_max_blob_xy"] = labels_max_blob

                            if axis == 1:
                                data_dict["depth_m"] = bbox_height * self.mesh_size
                                data_dict["depth_px"] = bbox_height

                                skimage_dict["bbox_xz"] = (min_row, min_col, max_row, max_col)
                                skimage_dict["labels_all_xz"] = labels_all
                                skimage_dict["labels_max_blob_xz"] = labels_max_blob

                        data_rows.append(data_dict)
                        np.savez_compressed(
                            f"measurements/melt_pool/{key}/{timestep}.npz",
                            **skimage_dict
                        )

            dimensions_df = pd.DataFrame(data_rows)

            # Save dimensions as csv
            dimensions_df.to_csv(f"measurements/melt_pool/{key}.csv")
