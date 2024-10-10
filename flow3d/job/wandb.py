import wandb

class JobWandb():
    def __init__(self, wandb_project = "Flow3D", use_wandb = False, **kwargs):
        self.use_wandb = use_wandb
        self.wandb_project = wandb_project

        if use_wandb:
            wandb.login()

            self.run = wandb.init(
                project = wandb_project,
                config = {
                    "job_name": self.name,
                    "simulations": [s.name for s in self.simulations]
                }
            )

        super().__init__(**kwargs)
