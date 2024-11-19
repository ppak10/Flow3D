from .base import WorkspaceBase

class Workspace(
    WorkspaceBase,
):
    def __init__(
            self,
            name: str = None,
            filename: str = None,
            verbose = False,
            **kwargs,
        ):
        super().__init__(
            name = name,
            filename = filename,
            verbose = verbose,
            **kwargs,
        )
