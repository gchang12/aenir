"""
"""

import unittest

from aenir.weapon import *
from aenir._logging import (
    configure_logging,
    logger,
    time_logger,
)

configure_logging()
time_logger.critical("")

class Test(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())
