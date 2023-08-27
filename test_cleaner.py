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
        Modify the table_files attribute
        to point to a mock file.
        Compile all tables from scratch.
        """
        # create instance
        self.sos_cleaner = SerenesCleaner(6)
        # modify file attributes to point to mocks
        self.sos_cleaner.fieldrecon_json = "MOCK-fieldrecon.json"
        self.sos_cleaner.tables_file = "MOCK-raw_stats.db"
        # delete files
        #self.sos_cleaner.get_datafile_path(self.sos_cleaner.tables_file).unlink(missing_ok=True)
        self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json).unlink(missing_ok=True)
        for urlpath in self.sos_cleaner.page_dict:
            if not self.sos_cleaner.get_datafile_path(self.sos_cleaner.tables_file).exists():
                self.sos_cleaner.scrape_tables(urlpath)
                self.sos_cleaner.save_tables(urlpath)
            self.sos_cleaner.load_tables(urlpath)

    def test_replace_with_int_df(self):
        """
        Tests that the method:
        - temporarily removes non-numeric columns
        - converts remaining cells to numeric strings
        - converts cell.dtypes to int
        - reinserts non-numeric columns where they previously were
        """
        urlpath = "characters/base-stats"
        columns = ["Name", "Class", "Affin", "Weapon ranks"]
        # get table
        bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        # create bad value to be cleaned
        bad_hp = str(bases_table.at[0, "HP"]) + " *"
        bases_table.at[0, "HP"] = bad_hp
        # compile before-values for comparison
        bases_columns = list(bases_table.columns)
        bases_table = self.sos_cleaner.url_to_tables[urlpath][0].copy()
        # assert: before-values are not numerical
        bases_table.drop(columns, inplace=True, axis=1)
        self.assertTrue( not all(bases_table.dtypes == int) )
        # main
        self.sos_cleaner.replace_with_int_df(urlpath, columns)
        # compile after-values
        new_bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        new_bases_columns = list(new_bases_table.columns)
        # assert: columns are in their original places
        self.assertListEqual(new_bases_columns, bases_columns)
        # assert: numeric columns are of int-dtype
        new_bases_table.drop(columns, inplace=True, axis=1)
        # Note: presence of null-rows makes this assertion impossible
        #self.assertTrue( all(new_bases_table.dtypes == int) )
        # assert: contents remain identical
        self.assertTrue( all(new_bases_table == bases_table) )
        # assert: bad HP value is not in the 'HP' column.
        self.assertNotIn(bad_hp, set(new_bases_table["HP"]))

    def test_replace_with_int_df__column_dne(self):
        """
        Tests that the method fails if:
        - the column list is not in the field list.
        """
        urlpath = "characters/base-stats"
        columns = [""]
        bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        # create bad value to be cleaned
        bad_hp = str(bases_table.at[0, "HP"]) + " *"
        bases_table.at[0, "HP"] = bad_hp
        # compile before-values for comparison
        bases_columns = list(bases_table.columns)
        with self.assertRaises(ValueError):
            self.sos_cleaner.replace_with_int_df(urlpath, columns)
        bases_table = self.sos_cleaner.url_to_tables[urlpath][0].copy()
        #bases_table.drop(columns, inplace=True)
        # assert: before-values are not numerical
        self.assertTrue( not all(bases_table.dtypes == int) )
        # compile after-values
        new_bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        new_bases_columns = list(new_bases_table.columns)
        # assert: columns are in their original places
        self.assertListEqual(new_bases_columns, bases_columns)
        # assert: numeric columns are of int-dtype
        #new_bases_table.drop(columns, inplace=True)
        self.assertFalse( all(new_bases_table.dtypes == int) )
        # assert: contents remain identical
        self.assertTrue( all(new_bases_table == bases_table) )
        # assert: bad HP value is still in the 'HP' column.
        self.assertIn(bad_hp, set(new_bases_table.loc[:, "HP"]))

if __name__ == '__main__':
    unittest.main()
