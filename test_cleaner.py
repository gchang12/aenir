#!/usr/bin/python3
"""
"""

import io
import re
import random
import json
import unittest
from unittest.mock import patch

from aenir.cleaner import SerenesCleaner

class RewriteableIO(io.StringIO):
    """
    """

    def __exit__(self, *args, **kwargs):
        """
        """
        self.seek(0)


class CleanerTest(unittest.TestCase):
    """
    """

    def setUp(self):
        """
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
        """
        self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file).unlink(missing_ok=True)
        self.clsrecon_path.unlink(missing_ok=True)

    def test_drop_nonnumeric_rows(self):
        """
        """
        # nothing can go wrong
        urlpath = "characters/base-stats"
        # main
        self.sos_cleaner.drop_nonnumeric_rows(urlpath)
        # check that all rows in a numeric column are numeric
        nonnumeric_columns = ("Name", "Class", "Affin", "Weapon ranks")
        # for filter call
        def is_numeric_col(col: object):
            """
            """
            return col not in nonnumeric_columns
        # commence check
        for df in self.sos_cleaner.url_to_tables[urlpath]:
            for num_col in filter(is_numeric_col, df.columns):
                for stat in df.loc[:, num_col]:
                    self.assertTrue(re.fullmatch("[+-]?[0-9]+", str(stat)) is not None)

    def test_replace_with_int_df(self):
        """
        """
        # nothing can go wrong
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

    def test_create_fieldrecon_file__file_exists(self):
        """
        """
        # the file may already exist
        fieldrecon_path = self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file)
        fieldrecon_path.write_text("")
        # saving old stat to compare against post-call result
        old_stat = fieldrecon_path.stat()
        with self.assertRaises(FileExistsError):
            self.sos_cleaner.create_fieldrecon_file()
        # file must remain untouched
        self.assertEqual(old_stat, fieldrecon_path.stat())

    def test_create_fieldrecon_file(self):
        """
        """
        fieldrecon_path = str(self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file))
        # compile fieldnames
        fieldnames = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                fieldnames.update(set(table.columns))
        # main
        self.sos_cleaner.create_fieldrecon_file()
        with open(fieldrecon_path, encoding='utf-8') as rfile:
            fieldrecon_dict = json.load(rfile)
        self.assertSetEqual(set(fieldrecon_dict), fieldnames)
        self.assertSetEqual(set(fieldrecon_dict.values()), {None})

    def test_apply_fieldrecon_file__failures(self):
        """
        """
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
        with open(fieldrecon_path, mode='w', encoding='utf-8') as wfile:
            json.dump(fieldrecon_dict, wfile)
        with self.assertRaises(ValueError):
            self.sos_cleaner.apply_fieldrecon_file()
        # check that weird HP alias still does not exist in the fieldname set
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                self.assertNotIn("health-points", table.columns)

    def test_apply_fieldrecon_file(self):
        """
        """
        fieldrecon_dict = {
                "Name": "Name",
                "Class": "Class",
                "Affin": "DROP!",
                "Weapon ranks": "DROP!",
                "HP": "health-points",
                }
        fieldrecon_path = str(self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file))
        with open(fieldrecon_path, mode='w', encoding='utf-8') as wfile:
            json.dump(fieldrecon_dict, wfile)
        # compile old fieldset for comparison
        old_fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                old_fieldset.update(set(table.columns))
        self.assertTrue(set(fieldrecon_dict).issubset(old_fieldset))
        # main
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
    def test_create_clsrecon_file__file_exists(self, mock_clsrecon_file):
        """
        """
        ltable_columns = ("characters/base-stats", "Class")
        rtable_columns = ("classes/maximum-stats", "Class")
        # 1: the file may already exist
        self.clsrecon_path.write_text("")
        old_stat = self.clsrecon_path.stat()
        # main: fails because the file exists
        mock_clsrecon_file.return_value = True
        with self.assertRaises(FileExistsError):
            self.sos_cleaner.create_clsrecon_file(ltable_columns, rtable_columns)
        mock_clsrecon_file.assert_called()
        # existing file is unchanged
        self.assertEqual(old_stat, self.clsrecon_path.stat())

    @patch("pathlib.Path.exists")
    def test_create_clsrecon_file__columns_dne(self, mock_path):
        """
        """
        ltable_columns = ("characters/base-stats", "lass")
        rtable_columns = ("classes/maximum-stats", "Class")
        mock_path.return_value = False
        with self.assertRaises(KeyError): # for pd.DataFrame_s
            self.sos_cleaner.create_clsrecon_file(ltable_columns, rtable_columns)
        self.assertFalse(self.clsrecon_path.exists())

    def test_create_clsrecon_file__tables_dne(self):
        """
        """
        ltable_columns = ("characters/base-stats", "Class")
        rtable_columns = ("casses/maximum-stats", "Class")
        with self.assertRaises(KeyError): # for url_to_tables dict
            self.sos_cleaner.create_clsrecon_file(ltable_columns, rtable_columns)
        self.assertFalse(self.clsrecon_path.exists())

    @patch("io.open")
    def test_create_clsrecon_file(self, mock_wfile):
        """
        """
        ltable_columns = ("classes/maximum-stats", "Class")
        rtable_columns = ("classes/promotion-gains", "Promotion")
        # creating a mock-file class
        mock_wfile.return_value = RewriteableIO()
        # main
        self.sos_cleaner.create_clsrecon_file(ltable_columns, rtable_columns)
        ltable = self.sos_cleaner.page_dict[ltable_columns[0]]
        rtable = self.sos_cleaner.page_dict[rtable_columns[0]]
        mock_wfile.assert_called_once_with(
                f"data/binding-blade/{ltable}-JOIN-{rtable}.json",
                mode="w",
                encoding="utf-8",
                )
        clsrecon_dict = json.load(mock_wfile.return_value)
        self.assertIsInstance(clsrecon_dict, dict)
        self.assertSetEqual(set(clsrecon_dict.values()), {None})
        self.assertSetEqual(set(type(cls) for cls in clsrecon_dict), {str})

    def test_verify_clsrecon_file__file_dne(self):
        """
        """
        ltable_url = "characters/growth-rates"
        rtable_columns = ("classes/maximum-stats", "Class")
        with self.assertRaises(FileNotFoundError):
            self.sos_cleaner.verify_clsrecon_file(ltable_url, rtable_columns)

    def test_verify_clsrecon_file__tables_dne(self):
        """
        """
        ltable_url = "characters/base-stats"
        rtable_columns = ("classes/mximum-stats", "Class")
        with self.assertRaises(KeyError):
            self.sos_cleaner.verify_clsrecon_file(ltable_url, rtable_columns)

    @patch("io.open")
    def test_verify_clsrecon_file__column_dne(self, mock_rfile):
        """
        """
        ltable_url = "characters/base-stats"
        rtable_columns = ("classes/maximum-stats", "lass")
        json_io = io.StringIO()
        json.dump({}, json_io)
        json_io.seek(0)
        mock_rfile.return_value = json_io
        with self.assertRaises(KeyError):
            self.sos_cleaner.verify_clsrecon_file(ltable_url, rtable_columns)

    @patch("io.open")
    def test_verify_clsrecon_file(self, mock_wfile):
        """
        """
        ltable_url = "characters/base-stats"
        rtable_columns = ("classes/maximum-stats", "Class")
        rtable_url, tocol_name = rtable_columns
        # compile clsrecon_dict
        clsrecon_dict = {}
        for name in self.sos_cleaner.url_to_tables[ltable_url][0].loc[:, "Name"]:
            clsrecon_dict[name] = random.choice(
                    self.sos_cleaner.url_to_tables[rtable_url][0].loc[:, tocol_name]
                    )
        clsrecon_dict["Karel"] = None
        # dump clsrecon_dict into virtual file
        with RewriteableIO() as wfile:
            json.dump(clsrecon_dict, wfile)
        mock_wfile.return_value = wfile
        # main
        nomatch_set = self.sos_cleaner.verify_clsrecon_file(ltable_url, rtable_columns)
        self.assertSetEqual(nomatch_set, set())
        ltable_name = self.sos_cleaner.page_dict[ltable_url]
        rtable_name = self.sos_cleaner.page_dict[rtable_url]
        mock_wfile.assert_called_once_with(
                f"data/binding-blade/{ltable_name}-JOIN-{rtable_name}.json",
                encoding="utf-8",
                )
        # test that non-existent class fails the test
        nonexistent_cls = "master-knight"
        unmapped_name = self.sos_cleaner.url_to_tables[ltable_url][0].at[0, "Name"]
        self.assertNotIn(
                nonexistent_cls ,
                self.sos_cleaner.url_to_tables[rtable_url][0].loc[:, tocol_name]
                )
        clsrecon_dict[unmapped_name] = nonexistent_cls
        with RewriteableIO() as wfile:
            json.dump(clsrecon_dict, wfile)
        # main
        mock_wfile.return_value = wfile
        nomatch_set = self.sos_cleaner.verify_clsrecon_file(ltable_url, rtable_columns)
        self.assertSetEqual(nomatch_set, {unmapped_name})

if __name__ == '__main__':
    unittest.main(
            #defaultTest=[test for test in dir(CleanerTest) if test.startswith("test_verify_clsrecon_file")],
            #module=CleanerTest,
            )
