#!/usr/bin/python3
"""
"""

import unittest
from unittest.mock import patch
import logging
import json
from pathlib import Path
from datetime import datetime

from aenir.reconciler import SerenesReconciler



class TestReconciler(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.sos_reconciler = SerenesReconciler(6)
        self.ltable_columns = (
                "characters/base-stats",
                "Name",
                "Class",
                )
        self.rtable_columns = (
                "classes/maximum-stats",
                "Class",
                )
        self.mock_jsondict = "table1-JOIN-table2.json"
        self.namerecon_path = self.sos_reconciler.get_namerecon_json(
                self.ltable_columns[0],
                self.rtable_columns[0],
                ).with_name(self.mock_jsondict)
        self.sos_reconciler.tables_file = "MOCK-" + self.sos_reconciler.tables_file
        if not self.sos_reconciler.get_datafile_path(self.sos_reconciler.tables_file).exists():
            for urlpath in self.sos_reconciler.page_dict:
                self.sos_reconciler.scrape_tables(urlpath)
                self.sos_reconciler.save_tables(urlpath)
        for urlpath in self.sos_reconciler.page_dict:
            self.sos_reconciler.load_tables(urlpath)
            self.sos_reconciler.drop_nonnumeric_rows(urlpath, numeric_col="Def")
        if not self.sos_reconciler.get_datafile_path(self.sos_reconciler.fieldrecon_json).exists():
            self.sos_reconciler.create_fieldrecon_file()
            exit()
        else:
            self.sos_reconciler.apply_fieldrecon_file()

    def tearDown(self):
        """
        """
        self.namerecon_path.unlink(missing_ok=True)

    def test_create_namerecon_file__file_exists(self):
        """
        """
        self.namerecon_path.write_text("")
        with self.assertRaises(FileExistsError):
            self.sos_reconciler.create_namerecon_file(
                    self.ltable_columns,
                    self.rtable_columns,
                    )

    @patch("aenir.reconciler.SerenesReconciler.get_namerecon_json")
    def test_create_namerecon_file(self, mock_json):
        """
        """
        ltable, key_col, from_col = self.ltable_columns
        rtable, to_col = self.rtable_columns
        ldict = {}
        for ltable_df in self.sos_reconciler.url_to_tables[ltable]:
            for index in ltable_df.index:
                pkey = ltable_df.at[index, key_col]
                pval = ltable_df.at[index, from_col]
                ldict[pkey] = pval
        lset = set()
        for rtable_df in self.sos_reconciler.url_to_tables[rtable]:
            lset.update(set(rtable_df.loc[:, to_col]))
        rnamerecon_dict = {}
        for pkey, pval in ldict.items():
            if pval in lset:
                continue
            rnamerecon_dict[pkey] = None
        mock_json.return_value = Path("data", "binding-blade", self.mock_jsondict)
        self.sos_reconciler.create_namerecon_file(
                self.ltable_columns,
                self.rtable_columns,
                )
        self.assertTrue(self.namerecon_path.exists())
        with open(str(self.namerecon_path)) as rfile:
            ltable_to_rtable = json.load(rfile)
        self.assertIsInstance(ltable_to_rtable, dict)
        self.assertSetEqual(set(ltable_to_rtable.values()), {None})

    def test_verify_namerecons(self):
        """
        """
        checkdict = [
                ("characters/base-stats", ("characters/growth-rates", "Name")),
                ("characters/base-stats", ("classes/maximum-stats", "Class")),
                ("characters/base-stats", ("classes/promotion-gains", "Class")),
                ("classes/promotion-gains", ("classes/maximum-stats", "Class")),
                ]
        self.sos_reconciler.tables_file = "cleaned_stats.db"
        self.sos_reconciler.url_to_tables.clear()
        for urlpath in self.sos_reconciler.page_dict:
            self.sos_reconciler.load_tables(urlpath)
            self.sos_reconciler.drop_nonnumeric_rows(urlpath, numeric_col="Def")
        self.sos_reconciler.apply_fieldrecon_file()
        for args in checkdict:
            self.assertTrue(self.sos_reconciler.verify_namerecons(*args))

    def test_verify_namerecons__fail(self):
        """
        """
        args = ("characters/base-stats", ("characters/growth-rates", "Name"))
        self.sos_reconciler.tables_file = "cleaned_stats.db"
        self.sos_reconciler.url_to_tables.clear()
        for urlpath in self.sos_reconciler.page_dict:
            self.sos_reconciler.load_tables(urlpath)
            self.sos_reconciler.drop_nonnumeric_rows(urlpath, numeric_col="Def")
        self.sos_reconciler.apply_fieldrecon_file()
        json_path = self.sos_reconciler.get_namerecon_json(args[0], args[1][0])
        with open(str(json_path), encoding='utf-8') as rfile:
            json_dict = json.load(rfile)
        json_dict['Zephiel'] = '6'
        with open(str(json_path), encoding='utf-8', mode='w') as wfile:
            json.dump(json_dict, wfile, indent=4)
        self.assertFalse(self.sos_reconciler.verify_namerecons(*args))
        json_dict['Zephiel'] = None
        with open(str(json_path), encoding='utf-8', mode='w') as wfile:
            json.dump(json_dict, wfile, indent=4)

if __name__ == '__main__':
    unittest.main()
