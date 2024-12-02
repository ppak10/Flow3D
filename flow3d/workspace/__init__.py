from .base import WorkspaceBase
from .simulation.huggingface import WorkspaceSimulationHuggingFace
from .simulation.measure import WorkspaceSimulationMeasure
from .simulation.post import WorkspaceSimulationPost
from .simulation.prepin import WorkspaceSimulationPrepin
from .simulation.simulate import WorkspaceSimulationSimulate
from .simulation.view import WorkspaceSimulationView
from .simulation.visualize import WorkspaceSimulationVisualize
from .utils import WorkspaceUtils

class Workspace(
    WorkspaceBase,
    WorkspaceSimulationHuggingFace,
    WorkspaceSimulationMeasure,
    WorkspaceSimulationPost,
    WorkspaceSimulationPrepin,
    WorkspaceSimulationSimulate,
    WorkspaceSimulationView,
    WorkspaceSimulationVisualize,
    WorkspaceUtils,
):
    def __init__(
            self,
            name: str = None,
            filename: str = None,
            workspace_path: str = None,
            verbose = False,
            **kwargs,
        ):
        super().__init__(
            name = name,
            filename = filename,
            verbose = verbose,
            workspace_path = workspace_path,
            **kwargs,
        )
