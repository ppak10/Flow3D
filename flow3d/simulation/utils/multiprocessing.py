import logging
import traceback

class SimulationUtilsMultiprocessing():
    """
    Multiprocessing methods used within simulation class.
    """

    @staticmethod
    def error_callback(e):
        """
        Log the error and stack trace error
        """
        logging.error(e)
        logging.error(traceback.format_exc())
