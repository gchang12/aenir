#!/usr/bin/python3
"""
Contains the test to see if the same table saved is the same loaded.
"""

import logging
from pathlib import Path
import unittest
from unittest.mock import patch
import tempfile # for use in testing successful save-load operation

import pandas as pd

from aenir.transcriber import SerenesTranscriber


class MockPath(str):
    """
    A str subclass with an exists method that returns True.
    """

    def exists(self):
        """
        Returns True for the save-load table operation.

        Mocks pathlib.Path.exists.
        """
        return True



class TranscriberTestIntegration(unittest.TestCase):
    """
    Defines methods to account for all scenarios when calling methods for IO-operations.

    Write-methods:
    - save_tables: Saves data tables
    """

    def setUp(self):
        """
        Initializes SerenesTranscriber instance, and binds it to 'sos_transcriber'.

        The tables_file parameter is set to a mock-file.
        """
        self.sos_transcriber = SerenesTranscriber(6)
        self.sos_transcriber.tables_file = "MOCK-" + self.sos_transcriber.tables_file

    @patch("pathlib.Path.joinpath")
    def test_saveload_tables(self, mock_joinpath):
        """
        Tests that save-load methods function in that the table saved is the same one loaded.
        """
        urlpath = "characters/base-stats"
        # compile tables
        self.sos_transcriber.scrape_tables(urlpath)
        # save scraped table for comparison
        saved_bases = self.sos_transcriber.url_to_tables[urlpath][0].copy()
        # main:
        tfile = tempfile.NamedTemporaryFile()
        mock_joinpath.return_value = MockPath(tfile.name)
        self.sos_transcriber.save_tables(urlpath)
        # urlpath is popped from url_to_tables
        self.assertNotIn(urlpath, self.sos_transcriber.url_to_tables)
        # data-dir should now exist
        self.assertTrue(self.sos_transcriber.home_dir.exists())
        tables_file = self.sos_transcriber.tables_file
        # tables-file should now exist
        #self.assertTrue(self.sos_transcriber.home_dir.joinpath(tables_file).exists())
        # main:
        with patch("__main__.list") as mocklist:
            mocklist.append.side_effect = ValueError
            self.sos_transcriber.load_tables(urlpath)
        self.assertIn(urlpath, self.sos_transcriber.url_to_tables)
        self.assertGreater(len(self.sos_transcriber.url_to_tables[urlpath]), 0)
        # before-table should match after-table
        loaded_bases = self.sos_transcriber.url_to_tables[urlpath][0]
        self.assertTrue(all(saved_bases == loaded_bases))
        # fail: table already exists
        url_to_tables = self.sos_transcriber.url_to_tables.copy()
        with self.assertRaises(ValueError):
            self.sos_transcriber.save_tables(urlpath)
        self.assertDictEqual(url_to_tables, self.sos_transcriber.url_to_tables)


if __name__ == '__main__':
    pass
