from .base import PortfolioBase
from .workspace import PortfolioWorkspace

class Portfolio(
    PortfolioBase,
    PortfolioWorkspace,
):
    def __init__(self, portfolio_path = "out", verbose = False, **kwargs):
        """
        Initializes portfolio variables and creates output directory.

        @param portfolio_path: Path to `portfolio` directory
        @param verbose: Displays verbose outputs.
        """
        super().__init__(
            portfolio_path = portfolio_path,
            verbose = verbose,
            **kwargs,
        )
