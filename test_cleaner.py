#!/usr/bin/python3
"""
Tests data-cleaning capabilities of SerenesCleaner.
"""

import logging
import unittest
from datetime import datetime
import json
import pandas as pd

from aenir.cleaner import SerenesCleaner

logging.basicConfig(filename="log_test-cleaner.log", level=logging.DEBUG)
logging.info("\n\nStarting test-run on '%s'\n\n", str(datetime.now()))

class TestCleaner(unittest.TestCase):
    """
    Defines tests for SerenesCleaner.
    """

    def tearDown(self):
        """
        Removes all files produced during the test-run.
        """
        fieldrecon_file = self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json)
        fieldrecon_file.unlink(missing_ok=True)

    def setUp(self):
        """
        Create a SerenesCleaner instance.
        Modify the fieldrecon_json attribute
        to point to a mock file.
        Modify the table_files attribute
        to point to a mock file.
        Compile all tables from scratch.
        """
        # create instance
        self.sos_cleaner = SerenesCleaner(6)
        # modify file attributes to point to mocks
        self.sos_cleaner.fieldrecon_json = "MOCK-" + self.sos_cleaner.fieldrecon_json
        self.sos_cleaner.tables_file = "MOCK-" + self.sos_cleaner.tables_file
        # delete files
        #self.sos_cleaner.get_datafile_path(self.sos_cleaner.tables_file).unlink(missing_ok=True)
        fieldrecon_file = self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json)
        fieldrecon_file.unlink(missing_ok=True)
        logging.info("Deleting '%s'...", str(fieldrecon_file))
        if not self.sos_cleaner.get_datafile_path(self.sos_cleaner.tables_file).exists():
            for urlpath in self.sos_cleaner.page_dict:
                self.sos_cleaner.scrape_tables(urlpath)
                self.sos_cleaner.save_tables(urlpath)
        for urlpath in self.sos_cleaner.page_dict:
            self.sos_cleaner.load_tables(urlpath)

    def test_create_fieldrecon_file(self):
        """
        Tests that a JSON file containing a dict of
        column names is created, each mapped to null.
        """
        logging.info("Creating field recon file...")
        # given: recon file dne
        recon_file  = self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json)
        # main
        self.sos_cleaner.create_fieldrecon_file()
        # assert: recon file is created
        self.assertTrue(recon_file.exists())
        # assert: recon file contains all field names
        with open(str(recon_file), encoding='utf-8') as rfile:
            recon_dict = json.load(rfile)
        # compile: field names here
        fieldname_set = set()
        for tableset in self.sos_cleaner.url_to_tables.values():
            for table in tableset:
                fieldname_set.update(set(table.columns))
        my_recon_dict = {fieldname: None for fieldname in fieldname_set}
        self.assertDictEqual(my_recon_dict, recon_dict)

    def test_create_fieldrecon_file__file_exists(self):
        """
        Tests that the method fails if the file exists already.
        """
        json_path = self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json)
        json_path.write_text("", encoding='utf-8')
        with self.assertRaises(FileExistsError):
            self.sos_cleaner.create_fieldrecon_file()
        json_path.unlink()
        # check that nothing has changed?

    def test_drop_nonnumeric_rows(self):
        """
        Tests that pd.DataFrame.applymap with func=int
        works on a pd.DataFrame object that has been
        affected by the drop_nonnumeric_rows method.
        """
        logging.info("Dropping non-numeric rows...")
        urlpath = "characters/growth-rates"
        self.sos_cleaner.drop_nonnumeric_rows(urlpath, numeric_col="HP")
        growths_table = self.sos_cleaner.url_to_tables[urlpath][0]
        growths_table.drop("Name", inplace=True, axis=1)
        growths_table = growths_table.applymap(int).convert_dtypes()
        self.assertNotIn("Name", growths_table, growths_table.columns)
        #self.assertTrue( all(growths_table.dtypes == int) )
        self.assertTrue(
                growths_table[pd.to_numeric(growths_table["HP"], errors="coerce").isnull()].empty
                    )

    def test_apply_fieldrecon_file__file_dne(self):
        """
        Tests that method fails if the file does not exist.
        """
        with self.assertRaises(FileNotFoundError):
            self.sos_cleaner.apply_fieldrecon_file()

    def test_apply_fieldrecon_file(self):
        """
        Tests that field mappings are applied
        to all pd.DataFrame objects
        """
        logging.info("Testing 'apply_fieldrecon_file' method...")
        # set up for main
        json_path = str(self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json))
        fielddict = {"HP": "health-points"}
        with open(json_path, mode='w', encoding='utf-8') as wfile:
            json.dump(fielddict, wfile)
        # check: nonexistent mapping is not already in the dataframes
        fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                fieldset.update(set(table.columns))
        self.assertNotIn(fielddict["HP"], fieldset)
        # main
        self.sos_cleaner.apply_fieldrecon_file()
        # check that all instances of 'HP' have been replaced by 'health-points'
        for urlpath, tablelist in self.sos_cleaner.url_to_tables.items():
            for index, table in enumerate(tablelist):
                if {"HP", "health-points"}.isdisjoint(set(table.columns)):
                    logging.info(
                            "'HP' or equivalent not in table #%d of '%s' section.", index, urlpath
                            )
                    continue
                self.assertNotIn("HP", table.columns)
                self.assertIn("health-points", table.columns)

    def test_apply_fieldrecon_file__contains_null(self):
        """
        Tests that all field mappings remain as they are
        if a null is in the values of the JSON dict.
        """
        logging.info("Testing 'apply_fieldrecon_file' method when JSON-dict contains null.")
        # set up for main
        json_path = str(self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json))
        fielddict = {"HP": "health-points", "Def": "Defense", "": None}
        with open(json_path, mode='w', encoding='utf-8') as wfile:
            json.dump(fielddict, wfile)
        # check: nonexistent mapping is not already in the dataframes
        fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                fieldset.update(set(table.columns))
        self.assertNotIn(fielddict["HP"], fieldset)
        # main: fail
        with self.assertRaises(ValueError):
            self.sos_cleaner.apply_fieldrecon_file()
        # check: labels are untouched
        for urlpath, tablelist in self.sos_cleaner.url_to_tables.items():
            for index, table in enumerate(tablelist):
                if {"HP", "health-points"}.isdisjoint(set(table.columns)):
                    logging.info(
                            "'HP' or equivalent not in table #%d of '%s' section.", index, urlpath
                            )
                    continue
                self.assertNotIn("health-points", table.columns)
                self.assertIn("HP", table.columns)

if __name__ == '__main__':
    unittest.main()
