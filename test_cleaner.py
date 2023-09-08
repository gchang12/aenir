#!/usr/bin/python3
"""
"""

import logging
import unittest
from datetime import datetime
import json
import pandas as pd

from aenir.cleaner import SerenesCleaner


class TestCleaner(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        fieldrecon_file = self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json)
        fieldrecon_file.unlink(missing_ok=True)

    def setUp(self):
        """
        """
        self.sos_cleaner = SerenesCleaner(6)
        self.sos_cleaner.fieldrecon_json = "MOCK-" + self.sos_cleaner.fieldrecon_json
        self.sos_cleaner.tables_file = "MOCK-" + self.sos_cleaner.tables_file
        fieldrecon_file = self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json)
        fieldrecon_file.unlink(missing_ok=True)
        if not self.sos_cleaner.get_datafile_path(self.sos_cleaner.tables_file).exists():
            for urlpath in self.sos_cleaner.page_dict:
                self.sos_cleaner.scrape_tables(urlpath)
                self.sos_cleaner.save_tables(urlpath)
        for urlpath in self.sos_cleaner.page_dict:
            self.sos_cleaner.load_tables(urlpath)

    def test_create_fieldrecon_file(self):
        """
        """
        recon_file  = self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json)
        self.sos_cleaner.create_fieldrecon_file()
        self.assertTrue(recon_file.exists())
        with open(str(recon_file), encoding='utf-8') as rfile:
            recon_dict = json.load(rfile)
        fieldname_set = set()
        for tableset in self.sos_cleaner.url_to_tables.values():
            for table in tableset:
                fieldname_set.update(set(table.columns))
        my_recon_dict = {fieldname: None for fieldname in fieldname_set}
        self.assertDictEqual(my_recon_dict, recon_dict)

    def test_create_fieldrecon_file__file_exists(self):
        """
        """
        json_path = self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json)
        json_path.write_text("", encoding='utf-8')
        with self.assertRaises(FileExistsError):
            self.sos_cleaner.create_fieldrecon_file()
        json_path.unlink()

    def test_drop_nonnumeric_rows(self):
        """
        """
        urlpath = "characters/growth-rates"
        self.sos_cleaner.drop_nonnumeric_rows(urlpath, numeric_col="HP")
        growths_table = self.sos_cleaner.url_to_tables[urlpath][0]
        self.assertTrue(
                growths_table[pd.to_numeric(growths_table["HP"], errors="coerce").isnull()].empty
                    )

    def test_apply_fieldrecon_file__file_dne(self):
        """
        """
        with self.assertRaises(FileNotFoundError):
            self.sos_cleaner.apply_fieldrecon_file()

    def test_apply_fieldrecon_file(self):
        """
        """
        json_path = str(self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json))
        fielddict = {"HP": "health-points", "Mov": "DROP"}
        with open(json_path, mode='w', encoding='utf-8') as wfile:
            json.dump(fielddict, wfile)
        fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                fieldset.update(set(table.columns))
        self.assertNotIn(fielddict["HP"], fieldset)
        self.assertIn("Mov", fieldset)
        self.sos_cleaner.apply_fieldrecon_file()
        for urlpath, tablelist in self.sos_cleaner.url_to_tables.items():
            for index, table in enumerate(tablelist):
                self.assertNotIn("Mov", table.columns)
                self.assertNotIn("DROP", table.columns)
                if {"HP", "health-points"}.isdisjoint(set(table.columns)):
                    continue
                self.assertNotIn("HP", table.columns)
                self.assertIn("health-points", table.columns)

    def test_apply_fieldrecon_file__contains_null(self):
        """
        """
        json_path = str(self.sos_cleaner.get_datafile_path(self.sos_cleaner.fieldrecon_json))
        fielddict = {"HP": "health-points", "Def": "Defense", "": None}
        with open(json_path, mode='w', encoding='utf-8') as wfile:
            json.dump(fielddict, wfile)
        fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                fieldset.update(set(table.columns))
        self.assertNotIn(fielddict["HP"], fieldset)
        with self.assertRaises(ValueError):
            self.sos_cleaner.apply_fieldrecon_file()
        for urlpath, tablelist in self.sos_cleaner.url_to_tables.items():
            for index, table in enumerate(tablelist):
                if {"HP", "health-points"}.isdisjoint(set(table.columns)):
                    continue
                self.assertNotIn("health-points", table.columns)
                self.assertIn("HP", table.columns)

    def test_replace_with_int_df(self):
        """
        """
        urlpath = "characters/base-stats"
        columns = ["Class", "Name", "Affin", "Weapon ranks", "Name"]
        bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        bad_hp = "-" + str(bases_table.at[0, "HP"]) + " *"
        bases_table.at[0, "HP"] = bad_hp
        bases_table = self.sos_cleaner.url_to_tables[urlpath][0].copy()
        self.sos_cleaner.replace_with_int_df(urlpath, columns)
        new_bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        self.assertTupleEqual(tuple(new_bases_table.columns), tuple(bases_table.columns))
        self.assertTrue( all(new_bases_table == bases_table) )
        self.assertTrue( all(new_bases_table.dtypes == new_bases_table.convert_dtypes().dtypes) )
        self.assertTrue( new_bases_table.at[0, "HP"] < 0 )
        self.assertNotIn(bad_hp, set(new_bases_table["HP"]))

    def test_replace_with_int_df__column_dne(self):
        """
        """
        urlpath = "characters/base-stats"
        columns = [""]
        bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        bad_hp = str(bases_table.at[0, "HP"]) + " *"
        bases_table.at[0, "HP"] = bad_hp
        with self.assertRaises(ValueError):
            self.sos_cleaner.replace_with_int_df(urlpath, columns)
        new_bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        self.assertTupleEqual(tuple(new_bases_table.columns), tuple(bases_table.columns))
        self.assertTrue( all(new_bases_table == bases_table) )
        self.assertIn(bad_hp, set(new_bases_table.loc[:, "HP"]))

    def test_replace_with_int_df__not_all_columns_listed(self):
        """
        """
        urlpath = "characters/base-stats"
        columns = ["Name"]
        bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        bad_hp = str(bases_table.at[0, "HP"]) + " *"
        bases_table.at[0, "HP"] = bad_hp
        bases_table = bases_table.copy()
        with self.assertRaises(TypeError):
            self.sos_cleaner.replace_with_int_df(urlpath, columns)
        new_bases_table = self.sos_cleaner.url_to_tables[urlpath][0]
        self.assertTupleEqual(tuple(new_bases_table.columns), tuple(bases_table.columns))
        self.assertTrue( all(new_bases_table == bases_table) )
        self.assertIn(bad_hp, set(new_bases_table.loc[:, "HP"]))

if __name__ == '__main__':
    unittest.main()
