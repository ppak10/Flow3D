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
        workspace.create_workspace(portfolio_path, **kwargs)

        return workspace
