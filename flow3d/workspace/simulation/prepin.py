import os
import pickle

from flow3d.simulation import Simulation

class WorkspaceSimulationPrepin:
    """
    Workspace class providing methods for initializing simulation folders and
    prepin files.
    """

    def simulation_generate_prepin(self, name, config_file="simulation.yml", **kwargs):
        """
        Creates prepin file from simulation.yml
        """

        simulation_path = os.path.join(self.workspace_path, name)
        simulation_pkl_path = os.path.join(simulation_path, f"simulation.pkl")
        with open(simulation_pkl_path, "rb") as file:
            simulation = pickle.load(file)

        simulation.load_config(config_file, working_dir=simulation_path)

        # Creates prepin file inside simulation job folder
        simulation_prepin_filename = f"prepin.{simulation.filename}"
        simulation_prepin_path = os.path.join(simulation_path, simulation_prepin_filename)

        # Write prepin file as "prepin.simulation"
        with open(simulation_prepin_path, "w") as file:
            file.write(simulation.prepin_file_content)

    # def prepin(self, **kwargs):
    #     """
    #     Create prepin file within simulation folder for a specified workspace
    #     """

    #     simulation = Simulation(**kwargs)

    #     # Create simulation folder within workspace path 
    #     simulation_path = os.path.join(self.workspace_path, simulation.name)
    #     if not os.path.isdir(simulation_path):
    #         os.makedirs(simulation_path)

    #     # Save simulation class object to pickle file
    #     simulation_pkl_path = os.path.join(simulation_path, f"{simulation.filename}.pkl")
    #     with open(simulation_pkl_path, "wb") as file:
    #         pickle.dump(simulation, file)
        
    #     # Creates prepin file inside simulation job folder
    #     simulation_prepin_filename = f"prepin.{simulation.filename}"
    #     simulation_prepin_path = os.path.join(simulation_path, simulation_prepin_filename)

    #     # Write prepin file as "prepin.simulation"
    #     with open(simulation_prepin_path, "w") as file:
    #         file.write(simulation.prepin_file_content)

    #     return simulation
    

    def prepin_process_map(
            self,
            power_min = 100,
            power_max = 400,
            power_step = 100,
            powers = None,
            velocity_min = 0.4,
            velocity_max = 2.0,
            velocity_step = 0.4,
            velocities = None,
            temperature_initial = 300,
            temperature_initials = None,
            **kwargs,
        ):
        """
        Creates a process map of simulations bounded by power and velocity.

        @param power_min: (Inclusive) Minimum power in watts
        @param power_max: (Inclusive) Maximum power in watts,
        @param power_step: Step size of power in watts,
        @param velocity_min: (Inclusive) Minimum velocity in m/s,
        @param velocity_max = (Inclusive) Maximum velocity in m/s,
        @param velocity_step = Step size of velocity in m/s,
        """

        print(powers, velocities, temperature_initials)
        #TODO: Add in divibility checks for power and velocity steps.
        if powers == None:
            powers = [x for x in range(power_min, power_max + 1, power_step)]

        if velocities == None:
            # Turns m/s velocity min and max values into integers for `range()`.
            v_min = int(velocity_min * 10)
            v_max = int((velocity_max * 10) + 1)
            v_step = int(velocity_step * 10)
            velocities = [x/10.0 for x in range(v_min, v_max, v_step)]

        if temperature_initials == None:
            temperature_initials = [temperature_initial]

        # Iterate through power and velocity combinations.
        simulations = []
        for power in powers:
            for velocity in velocities:
                for temperature_initial in temperature_initials:
                    s = self.prepin(
                            power = power,
                            velocity = velocity,
                            temperature_initial = temperature_initial,
                            **kwargs
                        )
                    simulations.append(s)

        print(f"Created Process Map with {len(simulations)} simulations")
        return simulations