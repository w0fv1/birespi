import logging
import datetime
import os


class BLogger:
    log: logging.Logger = None

    def __init__(self):
        self.log = logging.getLogger("BLogger")
        self.log.setLevel(logging.DEBUG)

        # Create file handler which logs even debug messages
        filename = f'log/birespi-log-{datetime.datetime.now().strftime("%Y-%m-%d")}.txt'
        if not os.path.exists("log"):
            os.makedirs("log")

        file_handler = logging.FileHandler(filename, mode="a")
        file_handler.setLevel(logging.DEBUG)

        # Create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)

    def log_message(self, message: str):
        self.log.info(message)

    def log_info(self, message):
        self.log.info(message)

    def log_error(self, message):
        self.log.error(message)

    def log_warning(self, message):
        self.log.warning(message)

    def log_debug(self, message):
        self.log.debug(message)

    def log_critical(self, message):
        self.log.critical(message)
