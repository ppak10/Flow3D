import os
import shutil
import textwrap

from datetime import datetime
from importlib.resources import files

from flow3d import data

class WorkspaceBase:
    """
    Workspace methods that do not rely on other classes.
    """
    def __init__(
            self,
            name: str = None,
            filename: str = None,
            workspace_path = None,
            verbose = False,
            **kwargs,
        ):
        self.set_name(name, filename)

        self.workspace_path = workspace_path
        self.verbose = verbose

        super().__init__(**kwargs)
    
    def set_name(self, name = None, filename = None):
        """
        Sets the `name` and `filename` values of the class.

        @param name: Name of workspace
        @param filename: `filename` override of workspace (no spaces)
        """
        # Sets `name` to approximate timestamp.
        if name is None:
            self.name = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.name = name

        # Autogenerates `filename` from `name` if not provided.
        if filename == None:
            self.filename = self.name.replace(" ", "_")
        else:
            self.filename = filename

    def create_workspace(self, portfolio_path):
        """
        Called by Portfolio `manage.py`
        Creates folder to store data related to Flow3D workspace.

        @param portfolio_dir: Portfolio directory
        """
            
        self.workspace_path = os.path.join(portfolio_path, self.filename)

        # Creates workspace folder directory in portfolio directory.
        if not os.path.isdir(self.workspace_path):
            os.makedirs(self.workspace_path)
        else:
            warning = textwrap.dedent(f"""
            Folder for job `{self.filename}` already exists.
            Following operations may overwrite existing files within folder.
            """)
            print(warning)

        # Copy over `manage.py` file to created workspace.
        resource_path = os.path.join("workspace", "manage.py")
        manage_py_resource_path = files(data).joinpath(resource_path)
        manage_py_workspace_path = os.path.join(self.workspace_path, "manage.py")
        shutil.copy(manage_py_resource_path, manage_py_workspace_path)

        # TODO: Generate workspace .xml

        return self.workspace_path
