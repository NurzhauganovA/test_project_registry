import logging
import os
from logging import Logger


class LoggerService:
    def __init__(
        self,
        name: str,
        log_file_name: str = "registry-module",
        log_dir: str = "logs",
        log_format: str = "%(levelname)s:    %(asctime)s - %(name)s: %(message)s",
        date_format: str = "%Y-%m-%d %H:%M:%S",
        file_level: int = logging.ERROR,
        base_level: int = logging.DEBUG,
    ) -> None:
        """
        Creates a customized logger that outputs logs to both the console and a file.

        - name - Logger name.
        - log_file_name - File name, where logs will be written.
        - log_dir - Log files directory.
        - log_format - Message format.
        - date_format - Date format.
        - file_level - File logging level.
        - base_level - Base logging level.
        """
        self.logger: Logger = logging.getLogger(name)
        self.logger.setLevel(base_level)
        # If handlers have already been added, there's no need to recreate them
        if not self.logger.handlers:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            formatter = logging.Formatter(log_format, datefmt=date_format)

            # Console handler setting up
            console_handler = logging.StreamHandler()
            console_handler.setLevel(base_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # File handler setting up
            file_path = os.path.join(log_dir, f"{log_file_name}.log")
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(file_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)
