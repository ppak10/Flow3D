import os
import textwrap

from flow3d.workspace import Workspace

class PortfolioWorkspace:
    """
    Portfolio class for Workspace methods
    """

    def create_workspace(self, name = None, portfolio_path = None, **kwargs):
        """
        Creates folder to store data related to Flow3D workspace.

        @param name: Name of workspace
        @param portfolio_path: Override of portfolio path
        """

        # Sets `portfolio_path`` to value in self if override not provided.
        if portfolio_path is None:
            portfolio_path = self.portfolio_path
            
        workspace = Workspace(name=name)
        workspace_path = workspace.create_workspace(portfolio_path, **kwargs)

        # Print `create_workspace` success message.
        print(textwrap.dedent(f"""
        Workspace folder `{name}` at `{workspace_path}`.
        Manage workspace with `manage.py` at `{workspace_path}`

        ```
        python {os.path.join(workspace_path, "manage.py")}
        ```
        """))

        return workspace
