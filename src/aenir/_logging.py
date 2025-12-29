"""
Declares loggers and logging configurations.
"""

import logging
import logging.config

logger = logging.getLogger("aenir")
time_logger = logging.getLogger("timer")

def configure_logging() -> None:
    """
    Instructs interpreter to log in accordance with configuration below.
    """
    main_logging_file = ".aenir.log"
    html_logging_file = ".html_aenir.log"
    main_datefmt = "%B %d, %Y @ %I:%M:%S %p"
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "timed": {
                    "datefmt": main_datefmt,
                    "format": "\n** %(asctime)s **\n" + "=" * 32,
                },
                "simple": {
                    "format":
                    "%(levelname)s:%(name)s.%(module)s.%(funcName)s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": main_logging_file,
                    "formatter": "simple",
                },
                "timekeeping": {
                    "class": "logging.FileHandler",
                    "filename": main_logging_file,
                    "formatter": "timed",
                },
            },
            "loggers": {
                "aenir": {
                    "level": "DEBUG",
                    "handlers": [
                        "file",
                        #"console",
                        #"email",# Not in use yet.
                    ],
                },
                "timer": {
                    # To capture all testing runs.
                    "level": "DEBUG",
                    "handlers": [
                        "timekeeping",
                    ],
                },
            },
        }
    )
