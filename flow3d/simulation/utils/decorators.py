import functools
import os

#TODO: Rename to singular `SimulationUtilsDecorator` instead of plural
class SimulationUtilsDecorators():
    """
    Decorators used within simulation class.
    """

    @staticmethod
    def change_working_directory(func):
        """
        Decorator for changing and reverting working directory just for method.
        """

        # Uses `functools.wraps` decorator to preserve metadadta during
        # multiprocessing.
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):

            # Set working directory from kwargs
            if "working_dir" not in kwargs:
                raise Exception(f"No working directory provided")
            else:
                working_dir = kwargs["working_dir"]

            # Change working directory
            previous_dir = os.getcwd()
            os.chdir(working_dir)

            # Run method 
            output = func(self, *args, **kwargs)

            # Change working directory back to previous folder
            os.chdir(previous_dir)

            return output

        return wrapper