# from .base import JobBase
# from .huggingface import JobHuggingface
# from .utils import JobUtils
# from .wandb import JobWandb

# class Job(
#     JobBase,
#     JobHuggingface,
#     JobUtils,
#     JobWandb,
# ):
#     def __init__(
#             self,
#             name = None,
#             filename: str = "job",
#             output_dir = "out",
#             use_wandb = False,
#             verbose = False,
#             wandb_project = "Flow3D",
#             **kwargs,
#         ):
#         super().__init__(
#             name = name,
#             filename = filename,
#             output_dir = output_dir,
#             use_wandb = use_wandb,
#             verbose = verbose,
#             wandb_project = wandb_project,
#             **kwargs,
#         )
    
#     # def run():
