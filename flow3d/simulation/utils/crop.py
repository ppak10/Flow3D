import bisect

class SimulationUtilsCrop():

    @staticmethod
    def x_distance(timestep, velocity = 0.5, laser_start_x = 0.06):
        # Coverts from m/s to cm/s
        velocity_cm_per_s = velocity * 100
        x_distance_cm = velocity_cm_per_s * timestep
        return laser_start_x + x_distance_cm

    @staticmethod
    def find_index(x_distance_cm, mesh):
        # Find the insertion point in the sorted list where the value would go
        idx = bisect.bisect_left(mesh, x_distance_cm)

        # print(idx)

        # If the value is exactly at idx, return idx - 1 to indicate the lower bound
        if idx == 0:
            # return None  # The value is smaller than all elements in the list
            return 0
        elif idx == len(mesh):
            # return None  # The value is larger than all elements in the list
            return len(mesh) - 1 
        else:
            return idx - 1  # The value lies between idx-1 and idx

    @staticmethod
    def crop_3d_array(array, crop_x=None, crop_y=None, crop_z=None):
        # Define slices for x, y, and z based on the crop distances
        # If a crop value is None, use the full range for that dimension
        x_slice = slice(crop_x[0], crop_x[1]) if crop_x is not None else slice(None)
        y_slice = slice(crop_y[0], crop_y[1]) if crop_y is not None else slice(None)
        z_slice = slice(crop_z[0], crop_z[1]) if crop_z is not None else slice(None)
    
        # Crop the array using the slices
        cropped_array = array[z_slice, y_slice, x_slice]
        return cropped_array

