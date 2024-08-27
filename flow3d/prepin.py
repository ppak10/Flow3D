# import math
import os
# import warnings
# 
# from flow3d.simulation import Simulation
# from flow3d import data
# from importlib.resources import files
# 
# template_id_types = ["UNS"]

class Prepin():
    """
    Base class for creating prepin files given process parameters.
    """

    def __init__(self, verbose = True):
        self.current_dir = os.path.dirname(__file__)
        self.verbose = verbose
        # self.keep_in_memory = keep_in_memory

        # self.data_path = os.path.join(__package__, "data")
        # Prepin
        # self.prepin_dir_path = prepin_dir
        # self.prepin_dir = prepin_dir

