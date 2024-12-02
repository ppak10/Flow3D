import os
import textwrap
import warnings

from flow3d import data
from importlib.resources import files

# TODO: Move these constants to a better place
TEMPLATE_ID_TYPES = ["UNS"]
TEMPLATE_IDS = [
    "A03590",
    "A97075",
    "N06002",
    "N07718",
    "R56400",
    "S30400",
    "S31603",
]

DEFAULT_TEMPLATE_ID = "S31603"
DEFAULT_TEMPLATE_ID_TYPE = "UNS"

class SimulationPrepin():
    """
    Base class for creating prepin files given process parameters.
    """

    @staticmethod
    def update_prepin_file_content(func):
        """
        Decorator for updating prepin file content when process parameters have
        changed.

        @param func: Method where process parameters have changed within class.
        """
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)

            # Update self.prepin_file_content
            if self.use_template:
                self.build_from_template()

            return result

        return wrapper

    def __init__(
        self,
        template_id = DEFAULT_TEMPLATE_ID,
        template_id_type = DEFAULT_TEMPLATE_ID_TYPE,
        use_template = True,    # Placeholder for future functionality.
        **kwargs,
    ):
        # Check template id
        if template_id not in TEMPLATE_IDS:
            raise Exception(textwrap.dedent(f"""
                '{template_id}'is not a valid `template_id`.
                Please select one of `{TEMPLATE_IDS}`.
                """))
        self.template_id = template_id

        # Check template id type
        if template_id_type not in TEMPLATE_ID_TYPES:
            raise Exception(textwrap.dedent(f"""
                '{template_id_type}'is not a valid `template_id_type`.
                Please select one of `{TEMPLATE_ID_TYPES}`.
                """))

        self.template_id_type = template_id_type
        self.use_template = use_template

        self.prepin_file_content = self.build_from_template()

    def build_from_template(self):
        """
        Create prepin file text content given template configurations.
        """

        # Load Template File
        template_filename = f"{self.template_id_type}_{self.template_id}.txt"

        if self.template_id_type in ["UNS"]:
            # Use the 'material' template folder
            template_file_path = os.path.join("simulation", "prepin", "material", template_filename)
            template_resource = files(data).joinpath(template_file_path)
        else:
            warnings.warn(f"Not yet supported")

        if not template_resource.is_file():
            raise Exception(f"Template {template_filename} does not exist.")

        with template_resource.open() as file:
            t = file.read()

        # Replaces values in template file with cgs parameter values.
        for key in self.default_parameters.keys():
            if self.verbose:
                print(f"Replacing <{key.upper()}> with {str(self.cgs(key))}")

            t = t.replace(f"<{key.upper()}>", str(self.cgs(key)))
        
        return t 

