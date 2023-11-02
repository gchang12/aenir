#!/usr/bin/python3
"""
Defines the CleanerTest class for SerenesCleaner class.
"""

import io
import logging
from pathlib import Path
import re
import random
import json
#import json.decoder
import unittest
from unittest.mock import patch

from aenir.cleaner import SerenesCleaner

class RewriteableIO(io.StringIO):
    """
    Inherits: io.StringIO

    Redefines the __exit__ method for mocking purposes.
    """

    def __exit__(self, *args, **kwargs):
        """
        Overrides automatic close procedure when calling io.StringIO via context-manager.

        As a bonus, the io.StringIO instance has its cursor moved back to the beginning.
        """
        self.seek(0)


class CleanerTest(unittest.TestCase):
    """
    Defines tests for the data clean-up methods.

    Write-methods:
    - create_clsrecon_file
    - create_fieldrecon_file
    """

    def setUp(self):
        """
        Initializes SerenesCleaner instance, and creates necessary tables_file if it doesn't exist.

        Loads tables into register, and sets *recon_file_s to their mock-equivalents.
        """
        self.sos_cleaner = SerenesCleaner(6)
        # compile tables if they don't exist
        if not self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.tables_file).exists():
            for urlpath in self.sos_cleaner.page_dict:
                self.sos_cleaner.scrape_tables(urlpath)
                self.sos_cleaner.save_tables(urlpath)
        for urlpath in self.sos_cleaner.page_dict:
            self.sos_cleaner.load_tables(urlpath)
        self.sos_cleaner.fieldrecon_file = "MOCK-" + self.sos_cleaner.fieldrecon_file
        self.clsrecon_path = self.sos_cleaner.home_dir.joinpath(
                "MOCK-characters__base_stats-JOIN-classes__maximum_stats.json" 
                )

    def tearDown(self):
        """
        Deletes *recon_file_s.
        """
        self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file).unlink(missing_ok=True)
        self.clsrecon_path.unlink(missing_ok=True)

    def test_drop_nonnumeric_rows(self):
        """
        Tests that all numeric columns contain [pseudo-]numeric data.
        """
        logging.info("CleanerTest.test_drop_nonnumeric_rows(self)")
        # nothing can go wrong
        urlpath = "characters/base-stats"
        # main
        self.sos_cleaner.drop_nonnumeric_rows(urlpath)
        # check that all rows in a numeric column are numeric
        nonnumeric_columns = ("Name", "Class", "Affin", "Weapon ranks")
        # for filter call
        def is_numeric_col(col: object):
            """
            Determines if a column is 'non-numeric'.
            """
            return col not in nonnumeric_columns
        # commence check
        for df in self.sos_cleaner.url_to_tables[urlpath]:
            for num_col in filter(is_numeric_col, df.columns):
                for stat in df.loc[:, num_col]:
                    self.assertTrue(re.fullmatch("[+-]?[0-9]+", str(stat)) is not None)

    def test_replace_with_int_df(self):
        """
        Tests that otherwise numeric stats have no extraneous trailing/leading non-numerics.
        """
        # nothing can go wrong
        logging.info("CleanerTest.test_replace_with_int_df(self)")
        urlpath = "characters/base-stats"
        bases = self.sos_cleaner.url_to_tables[urlpath][0]
        former_hp = int(bases.at[0, "HP"])
        bases.at[0, "HP"] = str(bases.at[0, "HP"]) + " *"
        former_def = int(bases.at[0, "Def"])
        bases.at[0, "Def"] = "-" + str(bases.at[0, "Def"])
        # main
        self.sos_cleaner.replace_with_int_df(urlpath)
        # check that all rows in a numeric column are numeric
        nonnumeric_columns = ("Name", "Class", "Affin", "Weapon ranks")
        # for filter call
        def is_numeric_col(col: object):
            """
            Determines if a column is 'non-numeric'.
            """
            return col not in nonnumeric_columns
        # commence check
        for df in self.sos_cleaner.url_to_tables[urlpath]:
            for num_col in filter(is_numeric_col, df.columns):
                for stat in df.loc[:, num_col]:
                    # recall that non-numeric rows have not been dropped yet
                    if stat == num_col:
                        continue
                    self.assertIsInstance(stat, int)
        bases = self.sos_cleaner.url_to_tables[urlpath][0]
        # nonnumerics stay intact
        self.assertEqual(bases.at[0, "Name"], "Roy")
        # bad stats are replaced
        self.assertEqual(bases.at[0, "HP"], former_hp)
        self.assertEqual(bases.at[0, "Def"], -former_def)

    @patch("pathlib.Path.exists")
    def test_create_fieldrecon_file__file_exists(self, mock_exists):
        """
        Tests that the fieldrecon_file is untouched if it exists when the method is called.
        """
        logging.info("CleanerTest.test_create_fieldrecon_file_exists(self)")
        # the file may already exist
        fieldrecon_path = self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file)
        #fieldrecon_path.write_text("")
        # saving old stat to compare against post-call result
        #old_stat = fieldrecon_path.stat()
        mock_exists.return_value = True
        with self.assertRaises(FileExistsError):
            self.sos_cleaner.create_fieldrecon_file()
        # file must remain untouched
        #self.assertEqual(old_stat, fieldrecon_path.stat())

    def test_create_fieldrecon_file(self):
        """
        Tests that the fieldrecon_file is created, and that its dict-equivalent is of the desired form.
        """
        logging.info("CleanerTest.test_create_fieldrecon_file(self)")
        fieldrecon_path = str(self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file))
        # compile fieldnames
        fieldnames = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                fieldnames.update(set(table.columns))
        # main
        with patch("io.open") as mock_wfile:
            mock_wfile.return_value = RewriteableIO()
            self.sos_cleaner.create_fieldrecon_file()
        #with open(fieldrecon_path, encoding='utf-8') as rfile:
        fieldrecon_dict = json.load(mock_wfile.return_value)
        self.assertSetEqual(set(fieldrecon_dict), fieldnames)
        self.assertSetEqual(set(fieldrecon_dict.values()), {None})

    def test_apply_fieldrecon_file__failures(self):
        """
        Documents/tests failures that may occur when calling apply_fieldrecon_file.

        Exceptions:
        - FileNotFoundError
        - ValueError: Null-values found in JSON-dict
        """
        logging.info("CleanerTest.test_apply_fieldrecon_file__failures(self)")
        # 1: the file may not exist
        fieldrecon_path = str(self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file))
        # compile before-fieldnames to check against after-fieldnames after failed call
        old_fieldnames = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                old_fieldnames.update(set(table.columns))
        # main: fails because the file does not exist
        with self.assertRaises(FileNotFoundError):
            self.sos_cleaner.apply_fieldrecon_file()
        # compile after-fieldnames
        new_fieldnames = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                new_fieldnames.update(set(table.columns))
        # compare
        self.assertSetEqual(new_fieldnames, old_fieldnames)
        # 2: there may be nulls in the file
        fieldrecon_dict = {"HP": "health-points", "Def": None}
        # check that weird HP alias does not exist in the fieldname set
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                self.assertNotIn("health-points", table.columns)
        wfile = RewriteableIO()
        #with open(fieldrecon_path, mode='w', encoding='utf-8') as wfile:
        json.dump(fieldrecon_dict, wfile)
        wfile.seek(0)
        with self.assertRaises(ValueError):
            with patch("io.open") as mock_rfile:
                mock_rfile.return_value = wfile
                self.sos_cleaner.apply_fieldrecon_file()
        # check that weird HP alias still does not exist in the fieldname set
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                self.assertNotIn("health-points", table.columns)

    def test_apply_fieldrecon_file(self):
        """
        Tests apply_fieldrecon_file method.
        """
        logging.info("CleanerTest.test_apply_fieldrecon_file(self)")
        fieldrecon_dict = {
                "Name": "Name",
                "Class": "Class",
                "Affin": "DROP!",
                "Weapon ranks": "DROP!",
                "HP": "health-points",
                }
        fieldrecon_path = str(self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file))
        wfile = RewriteableIO()
        #with open(fieldrecon_path, mode='w', encoding='utf-8') as wfile:
        json.dump(fieldrecon_dict, wfile)
        wfile.seek(0)
        # compile old fieldset for comparison
        old_fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                old_fieldset.update(set(table.columns))
        self.assertTrue(set(fieldrecon_dict).issubset(old_fieldset))
        # main
        with patch("io.open") as mock_rfile:
            mock_rfile.return_value = wfile
            self.sos_cleaner.apply_fieldrecon_file()
        # compile new fieldset
        new_fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                new_fieldset.update(set(table.columns))
        self.assertTrue({"Affin", "Weapon ranks"}.isdisjoint(new_fieldset))
        self.assertNotIn("DROP!", new_fieldset)
        self.assertIn("health-points", new_fieldset)

    @patch("pathlib.Path.exists")
    def test_create_clsrecon_file__failures(self, mock_exists):
        """
        Lists everything that can go wrong when calling this function.
        """
        logging.info("CleanerTest.test_create_clsrecon_file__failures(self)")
        ltable_url = "characters/base-stats"
        rtable_url = "classes/promotion-gains"
        lindex_col = "Name"
        from_col = "Class"
        to_col = "Class"
        # ltable_url not in self.url_to_tables
        with self.assertRaises(KeyError):
            self.sos_cleaner.create_clsrecon_file(
                    ("", lindex_col, from_col),
                    (rtable_url, to_col),
                    )
        # rtable_url not in self.url_to_tables
        with self.assertRaises(KeyError):
            self.sos_cleaner.create_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    ("", to_col),
                    )
        # to_col not in rtable
        with self.assertRaises(KeyError):
            self.sos_cleaner.create_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    (rtable_url, ""),
                    )
        # ltable_url not in self.url_to_tables
        with self.assertRaises(KeyError):
            bases_list = self.sos_cleaner.url_to_tables.pop(ltable_url)
            self.sos_cleaner.create_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    (rtable_url, to_col),
                    )
        self.sos_cleaner.url_to_tables[ltable_url] = bases_list
        # rtable_url not in self.url_to_tables
        with self.assertRaises(KeyError):
            promo_list = self.sos_cleaner.url_to_tables.pop(rtable_url)
            self.sos_cleaner.create_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    (rtable_url, to_col),
                    )
        self.sos_cleaner.url_to_tables[rtable_url] = promo_list
        # from_col not in ltable; no longer relevant since new code accounts for KeyError
        #mock_exists.return_value = False
        #with self.assertRaises(KeyError):
            #self.sos_cleaner.create_clsrecon_file(
                    #(ltable_url, lindex_col, ""),
                    #(rtable_url, to_col),
                    #)
        # [lr]table_url not in self.page_dict
        with self.assertRaises(KeyError):
            ltable_name = self.sos_cleaner.page_dict.pop(ltable_url)
            self.sos_cleaner.create_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    (rtable_url, to_col),
                    )
        self.sos_cleaner.page_dict[ltable_url] = ltable_name
        # [lr]table_url not in self.page_dict
        with self.assertRaises(KeyError):
            rtable_name = self.sos_cleaner.page_dict.pop(rtable_url)
            self.sos_cleaner.create_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    (rtable_url, to_col),
                    )
        self.sos_cleaner.page_dict[rtable_url] = rtable_name
        # {ltable_name}-JOIN-{rtable_name}.json exists
        mock_exists.return_value = True
        with self.assertRaises(FileExistsError):
            self.sos_cleaner.create_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    (rtable_url, to_col),
                    )

    @patch("io.open")
    @patch("pathlib.Path.exists")
    def test_create_clsrecon_file(self, mock_exists, mock_wfile):
        """
        An example of a successful run.
        """
        logging.info("CleanerTest.test_create_clsrecon_file(self)")
        # initialize necessary variables
        ltable_url = "characters/base-stats"
        rtable_url = "classes/promotion-gains"
        lindex_col = "Name"
        from_col = "Class"
        to_col = "Class"
        # safeguard against error-raiser
        mock_exists.return_value = False
        # create IO pool for function to send JSON to
        mock_wfile.return_value = RewriteableIO()
        # main
        self.sos_cleaner.create_clsrecon_file(
                (ltable_url, lindex_col, from_col),
                (rtable_url, to_col),
                )
        # load
        clsrecon_dict = json.load(mock_wfile.return_value)
        mock_wfile.return_value.close()
        # check that keys match primary key-values in ltable
        self.assertSetEqual(
                set(self.sos_cleaner.url_to_tables[ltable_url][0].loc[:, lindex_col]),
                set(clsrecon_dict),
                )
        # check that unmapped lot are None, mapped lot are mapped to selves
        bases_table = self.sos_cleaner.url_to_tables[ltable_url][0].set_index(lindex_col)
        to_series = self.sos_cleaner.url_to_tables[rtable_url][0].set_index(to_col).index
        for lindex_val, fromval in clsrecon_dict.items():
            # recall that nonnumeric rows have yet to be dropped
            if lindex_val == "Name":
                continue
            if fromval is None:
                self.assertNotIn(
                        bases_table.at[lindex_val, from_col],
                        to_series,
                        )
            else:
                self.assertIn(
                        bases_table.at[lindex_val, from_col],
                        to_series,
                        )

    @patch("io.open")
    @patch("pathlib.Path.exists")
    def test_create_clsrecon_file1(self, mock_exists, mock_wfile):
        """
        Tests the file when values in an index column are compared to those in a column in another table.
        """
        logging.info("CleanerTest.test_create_clsrecon_file1(self)")
        # initialize necessary variables
        ltable_url = "classes/promotion-gains"
        rtable_url = "classes/maximum-stats"
        lindex_col = "Class"
        from_col = "Class"
        to_col = "Class"
        # safeguard against error-raiser
        mock_exists.return_value = False
        # create IO pool for function to send JSON to
        mock_wfile.return_value = RewriteableIO()
        # main
        self.sos_cleaner.create_clsrecon_file(
                (ltable_url, lindex_col, from_col),
                (rtable_url, to_col),
                )
        # load
        clsrecon_dict = json.load(mock_wfile.return_value)
        mock_wfile.return_value.close()
        # check that keys match primary key-values in ltable
        self.assertSetEqual(
                set(self.sos_cleaner.url_to_tables[ltable_url][0].loc[:, lindex_col]),
                set(clsrecon_dict),
                )
        # check that unmapped lot are None, mapped lot are mapped to selves
        bases_table = self.sos_cleaner.url_to_tables[ltable_url][0].set_index(lindex_col)
        to_series = self.sos_cleaner.url_to_tables[rtable_url][0].set_index(to_col).index
        #print(bases_table)
        for lindex_val, fromval in clsrecon_dict.items():
            # recall that nonnumeric rows have yet to be dropped
            if fromval is None:
                self.assertNotIn(
                        lindex_val,
                        to_series,
                        )
            else:
                self.assertIn(
                        lindex_val,
                        #bases_table.at[lindex_val, from_col],
                        to_series,
                        )

    def test_verify_clsrecon_file(self):
        """
        Documents all possible errors for the SerenesCleaner.verify_clsrecon_file method 

        - FileNotFoundError: File does not exist
        - json.decode.JSONDecodeError: File is not in JSON format.
        - KeyError: rtable_url not in url_to_tables.
        - KeyError: to_col not a column in rtable
        """
        logging.info("CleanerTest.test_verify_clsrecon_file")
        ltable_url, lindex_col, from_col = "characters/base-stats", "Name", "Class"
        rtable_url, to_col = "classes/promotion-gains", "Class"
        # file does not exist
        with patch("pathlib.Path.joinpath") as mock_open:
            mock_open.return_value = ""
            with self.assertRaises(FileNotFoundError):
                self.sos_cleaner.verify_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    (rtable_url, to_col),
                )
        # file is not in JSON format
        with patch("io.open") as mock_open:
            mock_open.return_value = io.StringIO()
            mock_open.return_value.write("")
            with self.assertRaises(json.decoder.JSONDecodeError):
                self.sos_cleaner.verify_clsrecon_file(
                    (ltable_url, lindex_col, from_col),
                    (rtable_url, to_col),
                )
        # rtable_url is not in the url_to_tables dict
        rtable_list = self.sos_cleaner.url_to_tables.pop(rtable_url)
        with self.assertRaises(KeyError):
            self.sos_cleaner.verify_clsrecon_file(
                (ltable_url, lindex_col, from_col),
                (rtable_url, to_col),
            )
        self.sos_cleaner.url_to_tables[rtable_url] = rtable_list
        # to_col is not in the rtable
        to_col = ""
        with self.assertRaises(KeyError):
            self.sos_cleaner.verify_clsrecon_file(
                (ltable_url, lindex_col, from_col),
                (rtable_url, to_col),
            )
        # main: missing values
        to_col = "Class"
        with patch("io.open") as mock_open:
            mock_open.return_value = io.StringIO()
            # method allows for keys that don't exist in the bases, but this affects nothing.
            json.dump({"": "non-existent class"}, mock_open.return_value)
            mock_open.return_value.seek(0)
            missing_items = self.sos_cleaner.verify_clsrecon_file(
                (ltable_url, lindex_col, from_col),
                (rtable_url, to_col),
            )
            self.assertIsInstance(missing_items, set)
            self.assertSetEqual({"non-existent class"}, missing_items)
        # main: no missing values
        missing_items = self.sos_cleaner.verify_clsrecon_file(
            (ltable_url, lindex_col, from_col),
            (rtable_url, to_col),
        )
        self.assertSetEqual(missing_items, set())

if __name__ == '__main__':
    unittest.main(
            defaultTest="test_create_clsrecon_file1",
            module=CleanerTest,
            )
