# import wandb

# class JobWandb():
#     def __init__(self, wandb_project = "Flow3D", use_wandb = False, **kwargs):
#         # Note: Saving wandb run variable to self causes issues in multiprocessing.
#         self.use_wandb = use_wandb
#         self.wandb_project = wandb_project

#         super().__init__(**kwargs)

#     @staticmethod
#     def wandb_run(func):
#         """
#         Decorator for initializing wandb
#         """

#         def wrapper(self, *args, **kwargs):
#             if self.use_wandb:
#                 wandb.login()

#                 wandb.init(
#                     project = self.wandb_project,
#                     config = {
#                         "job_name": self.name,
#                         "simulations": [s.name for s in self.simulations]
#                     }
#                 )
            
#             output = func(self, *args, **kwargs)

#             if self.use_wandb:
#                 wandb.finish()

#             return output
            
#         return wrapper
