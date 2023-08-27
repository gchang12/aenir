#!/usr/bin/python3
"""
Tests data-cleaning capabilities of SerenesCleaner.
"""

import logging
import unittest

from aenir.cleaner import SerenesCleaner

logging.basicConfig(filename="log_test-cleaner.log", level=logging.DEBUG)

class TestCleaner(unittest.TestCase):
    """
    Defines tests for SerenesCleaner.
    """

    def setUp(self):
        """
        Create a SerenesCleaner instance.
        Modify the fieldrecon_json attribute
        to point to a mock file.
        Compile all tables from scratch.
        """
        self.sos_cleaner = SerenesCleaner(6)
        self.sos_cleaner.fieldrecon_json = "MOCK-fieldrecon.json"
        for urlpath in self.sos_cleaner.page_dict:
            self.sos_cleaner.scrape_tables(urlpath)
            self.sos_cleaner.save_tables(urlpath, filename="MOCK-raw_stats.db")
