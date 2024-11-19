import os
import textwrap

from datetime import datetime

class WorkspaceBase:
    """
    Workspace methods that do not rely on other classes.
    """
    def __init__(
            self,
            name: str = None,
            filename: str = None,
            verbose = False,
            **kwargs,
        ):
        self.set_name(name, filename)
        self.workspace_path = None
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
        Creates folder to store data related to Flow3D job.
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

        return self.workspace_path
