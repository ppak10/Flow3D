import os

class SimulationStatus():
    """
    Static methods for determining simulation status
    """

    def check_status(self, simulation_dir_path):
        """
        Provides status object of simulation. 
        """
        # Check if simulation is done by reading `report.simulation`
        # Last lines of `report.simulation` should look something like this.
        # 
        # > restart and spatial data available at t= 9.95003E-04
        # > restart and spatial data available at t= 1.00001E-03
        # > 
        # > end of calculation at   t =    1.00001E-03,     cycle =   44577
        # >  normal completion                                          
        # >
        # >
        # > flsgrf.simulation file size:   29 gb
        # >
        # > elapsed time =    5.67105E+03 seconds, or
        # >                   0 days :  1 hours : 34 minutes : 31 seconds
        # >
        # >     cpu time =    1.79030E+05 seconds

        status = {
            "exists": False,
            "completed": False,
            "run_simulation_completed": False,
            "post_process_create_flslnk_completed": False,
            "post_process_create_chunks_completed": False,
            "post_process_create_npz_completed": False,
        }

        # Check generated report file.
        report_file_path = os.path.join(simulation_dir_path, "report.simulation")

        # if os.path.exists(report_file_path):

        #     with open(report_file_path, "r") as f:
        #         last_line = f.readlines()[-1].strip()

        #     if "cpu time" in last_line.lower():
        #         # Last line should be cpu time if simulation is completed
        #         status["completed"] = True

        # Check execution times files to see if finished zipping flsgrf file.
        # execution_times_file_path = os.path.join(simulation_dir_path, "execution_times.txt")
        chunks_dir_path = os.path.join(simulation_dir_path, "chunks")
        chunks_zip_path = os.path.join(simulation_dir_path, "chunks.zip")

        npz_dir_path = os.path.join(simulation_dir_path, "npz")
        npz_zip_path = os.path.join(simulation_dir_path, "npz.zip")

        if os.path.exists(simulation_dir_path):

            # with open(execution_times_file_path, "r") as f:
            #     execution_times = f.read()

            # flsgrf_file_path can exist during simulation 
            # flsgrf_file_path = os.path.join(simulation_dir_path, "flsgrf.simulation")
            flsgrf_zip_file_path = os.path.join(simulation_dir_path, "flsgrf.zip")
            if os.path.exists(flsgrf_zip_file_path):
                # Indicates that job method for running simulation is done.
                status["run_simulation_completed"] = True

            # Can't trust execution times.
            # if "post_process_create_flslnk" in execution_times:
            flslnk_tmp_file_path = os.path.join(simulation_dir_path, "flslnk.tmp")
            flslnk_zip_file_path = os.path.join(simulation_dir_path, "flslnk.zip")
            if os.path.exists(flslnk_tmp_file_path) or \
                os.path.exists(flslnk_zip_file_path):
                # Indicates that flslnk file has been created.
                status["post_process_create_flslnk_completed"] = True

            if (os.path.isdir(chunks_dir_path) and len(os.listdir(chunks_dir_path))) or os.path.exists(chunks_zip_path):
                # Indicates that chunks from flslnk file has been created.
                status["post_process_create_chunks_completed"] = True

            if (os.path.isdir(npz_dir_path) and len(os.listdir(npz_dir_path))) or os.path.exists(npz_zip_path):
                # Indicates that npz from chuncks has been created.
                status["post_process_create_npz_completed"] = True
        
        return status
