from .base import JobBase
from .huggingface import JobHuggingface
from .post import JobPost
from .simulation import JobSimulation
from .utils import JobUtils
from .visualize import JobVisualize
from .wandb import JobWandb

class Job(
    JobBase,
    JobHuggingface,
    JobPost,
    JobSimulation,
    JobUtils,
    JobVisualize,
    JobWandb,
):
    def __init__(
            self,
            name = None,
            filename: str = "job",
            output_dir = "out",
            use_wandb = False,
            verbose = False,
            wandb_project = "Flow3D",
            **kwargs,
        ):
        super().__init__(
            name = name,
            filename = filename,
            output_dir = output_dir,
            use_wandb = use_wandb,
            verbose = verbose,
            wandb_project = wandb_project,
            **kwargs,
        )
    
    # def run():
