#!/usr/bin/python3
"""
Defines TranscriberTest class for SerenesTranscriber class.
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


class TranscriberTest(unittest.TestCase):
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

    def tearDown(self):
        """
        Deletes the home_dir/tables_file.
        """
        self.sos_transcriber.home_dir.joinpath(self.sos_transcriber.tables_file).unlink(missing_ok=True)

    def test_pagedict_is_clsattr(self):
        """
        Tests that page_dict parameter is an attribute.
        """
        logging.info("TranscriberTest.test_pagedict_is_clsattr(self)")
        some_transcriber = SerenesTranscriber(5)
        self.assertIs(some_transcriber.page_dict, self.sos_transcriber.page_dict)

    def test_save_tables__failures(self):
        """
        Tests/documents all possible failures the save_tables method can raise.

        Errors:
        - ValueError: urlpath not in url_to_tables (i.e. no tables to save).
        - TypeError: Non-table in url_to_tables[urlpath].
        - KeyError: urlpath not in url_to_tables.
        """
        logging.info("TranscriberTest.test_save_tables__failures(self)")
        urlpath = "characters/base-stats"
        # main: fails because there are no tables
        self.sos_transcriber.url_to_tables[urlpath] = []
        with self.assertRaises(ValueError):
            self.sos_transcriber.save_tables(urlpath)
        # assert: url still in table-dict, data-dir DNE, tables-file DNE
        self.assertIn(urlpath, self.sos_transcriber.url_to_tables)
        #self.assertFalse(Path("data").exists())
        tables_file = self.sos_transcriber.tables_file
        self.assertFalse(self.sos_transcriber.home_dir.joinpath(tables_file).exists())
        # main: fails because not all values to be saved are pd.DataFrames
        self.sos_transcriber.url_to_tables[urlpath].append(None)
        self.sos_transcriber.url_to_tables[urlpath].append(pd.DataFrame())
        with self.assertRaises(TypeError):
            self.sos_transcriber.save_tables(urlpath)
        self.assertIn(urlpath, self.sos_transcriber.url_to_tables)
        self.assertFalse(self.sos_transcriber.home_dir.joinpath(tables_file).exists())
        # main: fails because the urlpath is not registered
        self.sos_transcriber.url_to_tables.clear()
        with self.assertRaises(KeyError):
            self.sos_transcriber.save_tables(urlpath)
        self.assertFalse(self.sos_transcriber.home_dir.joinpath(tables_file).exists())

    # TODO: patch pd.read_sql_table, pd.{to_sql} methods to write to in-memory stream
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

    def test_load_tables__failures(self):
        """
        Tests/documents all possible failures for load_tables method.

        Exceptions:
        - FileNotFoundError: home_dir/tables_file does not exist.
        """
        logging.info("TranscriberTest.test_load_tables__failures(self)")
        urlpath = "characters/base-stats"
        # main: fails because file does not exist
        self.sos_transcriber.tables_file = "nonexistent_file"
        absolute_tables_file = self.sos_transcriber.home_dir.joinpath(
                self.sos_transcriber.tables_file
                )
        self.assertFalse(
                self.sos_transcriber.home_dir.joinpath(self.sos_transcriber.tables_file).exists()
                )
        self.sos_transcriber.url_to_tables[urlpath] = []
        # assert that url_to_tables contents remain the same
        old_urldict = self.sos_transcriber.url_to_tables.copy()
        old_tablelist = self.sos_transcriber.url_to_tables[urlpath].copy()
        with self.assertRaises(FileNotFoundError):
            self.sos_transcriber.load_tables(urlpath)
        new_urldict = self.sos_transcriber.url_to_tables
        self.assertIn(urlpath, self.sos_transcriber.url_to_tables)
        new_tablelist = self.sos_transcriber.url_to_tables[urlpath]
        self.assertDictEqual(new_urldict, old_urldict)
        self.assertListEqual(old_tablelist, new_tablelist)

    def test_get_urlname(self):
        """
        Tests that get_urlname method succeeds.
        """
        logging.info("TranscriberTest.test_get_urlname(self)")
        # get registered urlname
        tablename = "characters__base_stats"
        # expected output
        expected = "characters/base-stats"
        # for developer's peace of mind
        self.assertIn(expected, self.sos_transcriber.page_dict)
        # main
        actual = self.sos_transcriber.get_urlname_from_tablename(tablename)
        self.assertEqual(actual, expected)

    def test_get_urlname__dne(self):
        """
        Tests that get_urlname method fails due to non-existent table-equivalent.
        """
        logging.info("TranscriberTest.test_get_urlname__dne(self)")
        # non-registered urlname
        tablename = "characters__baked_fat"
        # expected output
        expected = "characters/baked-fat"
        # for developer's peace of mind
        self.assertNotIn(expected, self.sos_transcriber.page_dict)
        # main: fails by AssertionError
        with self.assertRaises(AssertionError):
            actual = self.sos_transcriber.get_urlname_from_tablename(tablename)

if __name__ == '__main__':
    unittest.main()
