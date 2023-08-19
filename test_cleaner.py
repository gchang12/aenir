#!/usr/bin/python3
"""
"""

import unittest

class TestCleaner(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        pass

    def test_create_field_consolidation_file(self):
        """
        Asserts that a blank JSON file for mapping field names to
        a common standard is created.
        """
        filename = "mock__field_consolidation.json"
        self.sos_scraper.create_field_consolidation_file(filename=filename)
        cfile_path = self.sos_scraper.get_datafile_path(filename)
        self.assertTrue(cfile_path.exists())
        pass


if __name__ == '__main__':

