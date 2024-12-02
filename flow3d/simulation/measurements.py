import multiprocessing
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
        │  ├─ temperature/
        │  │  ├─ dimensions.npz
        ...
        ```
        """
        # Initialize visualize folders.
        if not os.path.exists("measurements"):
            os.makedirs("measurements")

        # Column subfolders
        for key in COLUMNS_CONFIG.keys():
            if not os.path.exists(f"measurements/{key}"):
                # Makes folder rather than just file because there may be more
                # measurements other than dimensions. Delete comment when this
                # happens.
                os.makedirs(f"measurements/{key}")

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

                for index, npz_file in tqdm(enumerate(sorted(os.listdir(npz_dir_path)))):
                    index_string = f"{index}".zfill(8)

                    npz_data = np.load(f"{npz_dir_path}/{npz_file}")
                    example = {key: npz_data[key] for key in npz_data.keys()}

                    power, velocity = example["power"][0], example["velocity"][0]

                    flslnk_file = f"flslnk_npz/{index_string}.npz"

                    if os.path.exists(flslnk_file):
                        flslnk_data = np.load(flslnk_file)

                        thresholded_data = np.copy(flslnk_data[key]).squeeze()
                        thresholded_data[thresholded_data <= configs["clim"][0]] = 0
                        thresholded_data[thresholded_data > configs["clim"][0]] = 1
                        thresholded_data_unique = np.unique(thresholded_data)

                        if len(thresholded_data_unique) > 1:
                        
                            data_dict = {
                                "index": index,
                                "power": power,
                                "velocity": velocity,
                                "depth": None,
                                "length": None,
                                "width": None,
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
                                    data_dict["width"] = bbox_height
                                    data_dict["length"] = bbox_width
                                    data_dict["bbox_xy"] = (min_row, min_col, max_row, max_col)
                                    data_dict["labels_all_xy"] = labels_all
                                    data_dict["labels_max_blob_xy"] = labels_max_blob

                                if axis == 1:
                                    data_dict["depth"] = bbox_height
                                    data_dict["bbox_xz"] = (min_row, min_col, max_row, max_col)
                                    data_dict["labels_all_xz"] = labels_all
                                    data_dict["labels_max_blob_xz"] = labels_max_blob

                                # # Create the bounding box
                                # rect = patches.Rectangle(
                                #     (min_col, min_row),  # Bottom-left corner of the rectangle
                                #     bbox_width,               # Width of the rectangle
                                #     bbox_height,              # Height of the rectangle
                                #     linewidth=1,         # Thickness of the rectangle edge
                                #     edgecolor='red',     # Color of the rectangle edge
                                #     facecolor='none'     # No fill color
                                # )

                                # # Plot the labeled max region with the bounding box
                                # plt.figure()
                                # fig, ax = plt.subplots()

                                # ax.imshow(labels_max_blob, cmap=configs["cmap"])
                                # ax.add_patch(rect)  # Add the rectangle to the plot

                                # # Add a colorbar and show the plot
                                # plt.title(f"bbox height: {bbox_height}, bbox width: {bbox_width}")
                                # plt.colorbar(ax.imshow(labels_max_blob, cmap=configs["cmap"]))
                                # plt.show()

                            data_rows.append(data_dict)

            dimensions_df = pd.DataFrame(data_rows)

            # Save dimensions as csv
            dimensions_df.to_pickle(f"measurements/{key}/dimensions.pkl")
