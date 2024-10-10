class SimulationBase():
    """
    Base file for simulation class.
    """

    def __init__(self, version = 0, verbose = False, **kwargs):
        self.version = version
        self.verbose = verbose
        super().__init__(**kwargs)
