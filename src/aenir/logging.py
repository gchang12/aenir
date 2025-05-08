"""
"""

import logging

logger = logging.getLogger()

# TODO: Configure this!

def configure_logging():
    """
    """
    import logging.config
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "formatter-id": {
                    "format": None,
                }
            },
            "filters": {
                "filter-id": {
                    "filter": None,
                }
            },
            "handlers": {
                "handler-id": None,
            },
            "loggers": {
                "level": None,
                "propagate": None,
                "filters": [],
                "handlers": [],
            }
        }
    )
