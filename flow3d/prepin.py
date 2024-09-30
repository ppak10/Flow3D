# import math
import os
# import warnings
# 
# from flow3d.simulation import Simulation
from decimal import Decimal
from importlib.resources import files
from flow3d import data
from flow3d.parameters import default_parameters

template_id_types = ["UNS"]
template_ids = [
    "A03590",
    "A97075",
    "N06002",
    "N07718",
    "R56400",
    "S30400",
    "S31603",
]

default_template_id = "S31603"
default_template_id_type = "UNS"

class Prepin():
    """
    Base class for creating prepin files given process parameters.
    """

    def __init__(
        self,
        template_id = default_template_id,
        template_id_type = default_template_id_type,
        verbose = True,
    ):
        self.verbose = verbose
        self.prepin_file_content = None

        # Check template id
        if template_id not in template_ids:
            raise Exception(f"""
'{template_id}'is not a valid `template_id`.
Please select one of `{template_ids}`.
""")
        self.template_id = template_id

        # Check template id type
        if template_id_type not in template_id_types:
            raise Exception(f"""
'{template_id_type}'is not a valid `template_id_type`.
Please select one of `{template_id_types}`.
""")
        self.template_id_type = template_id_type


    def cgs(self, parameter: str):
        """
        Converts metric process parameter to centimeter-gram-second units.
        """
        if parameter == "power":
            # 1 erg = 1 cm^2 * g * s^-2
            # 1 J = 10^7 ergs -> 1 W = 10^7 ergs/s
            return getattr(self, parameter) * 1E7
        elif parameter == "velocity":
            # Handled separately from `else` case just in case if mm/s input
            # is implement in the future.
            # 1 m/s = 100 cm/s
            return getattr(self, parameter) * 100
        elif parameter == "gauss_beam":
            # Gauss beam should utilize a more precise value.
            return getattr(self, parameter) * 1E2
        else:
            # Converting to decimal handles case where 2.799 != 2.8
            parameter_decimal = Decimal(getattr(self, parameter) * 1E2)
            return float(round(parameter_decimal, 3))

    def build_from_template(self):
        """
        Create prepin file text content given template configurations.

        @param template_id: Material Identifier -> defaults to 'S31603'
        @param template_id_type: Material Identifier Type -> defaults to 'UNS'
        @return
        """

        # Load Template File
        template_filename = f"{self.template_id_type}_{self.template_id}.txt"

        if self.template_id_type in ["UNS"]:
            # Use the 'material' template folder
            template_file_path = os.path.join("template", "material", template_filename)
            template_resource = files(data).joinpath(template_file_path)
        else:
            warnings.warn(f"Not yet supported")

        if not template_resource.is_file():
            raise Exception(f"Template {template_filename} does not exist.")

        with template_resource.open() as file:
            t = file.read()

        # Replaces values in template file with cgs parameter values.
        for key in default_parameters.keys():
            if self.verbose:
                print(f"Replacing <{key.upper()}> with {str(self.cgs(key))}")

            t = t.replace(f"<{key.upper()}>", str(self.cgs(key)))
        
        self.prepin_file_content = t
        return self.prepin_file_content

