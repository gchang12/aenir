#!/usr/bin/python3
"""
Defines tests for the SerenesReconciler methods. 
"""

import unittest

from aenir.reconciler import SerenesReconciler

class TestReconciler(unittest.TestCase):
    """
    Defines tests for the SerenesReconciler methods. 
    """

    def setUp(self):
        """
        Sets up a SerenesReconciler instance.
        Sets the mock filename generator.
        """
        # initialize variables for the one test
        self.ltable_columns = (
                "characters/base-stats",
                "Name",
                "Class",
                )
        self.rtable_columns = (
                "classes/maximum-stats",
                "Class",
                )
        self.namerecon_path = self.sos_reconciler.get_datafile_path(
                self.ltable_columns[0],
                self.rtable_columns[0],
                )
        # initialize main object
        self.sos_reconciler = SerenesReconciler(6)
        # compile tables from db file
        self.sos_reconciler.tables_file = "MOCK-" + self.sos_reconciler.tables_file
        if not self.sos_reconciler.get_datafile_path(self.sos_reconciler.tables_file).exists():
            for urlpath in self.sos_reconciler.page_dict:
                self.sos_reconciler.scrape_tables(urlpath)
                self.sos_reconciler.save_tables(urlpath)
        for urlpath in self.sos_reconciler.page_dict:
            self.sos_reconciler.load_tables(urlpath)
        # clean data
        self.sos_reconciler.sanitize_all_tables()

    def tearDown(self):
        """
        Deletes the JSON dict
        """
        self.namerecon_path.unlink(missing_ok=True)

    def test_create_namerecon_file__file_exists(self):
        """
        Tests that the method fails if the file exists.
        The databases ought to remain untouched.
        """
        self.namerecon_path.write("")
        with self.assertRaises(FileExistsError):
            self.create_namerecon_file(
                    self.ltable_columns,
                    self.rtable_columns,
                    )

    def test_create_namerecon_file(self):
        """
        Creates a name-recon file in JSON format.
        The file contains a list of names in one table
        but not the other.
        """
        ltable, key_col, from_col = self.ltable_columns
        rtable, to_col = self.rtable_columns
        # gather set from left table.
        ltable_df = self.sos_reconciler.url_to_tables[ltable][0]
        ldict = dict()
        for index in ltable_df.index:
            pkey = ltable_df.at[index, key_col]
            pval = ltable_df.at[index, from_col]
            ldict[pkey] = pval
        # gather set from right table.
        # subtract right from left set.
        rtable_df = self.sos_reconciler.url_to_tables[rtable][0]
        for index in rtable_df.index:
            if rtable_df.at[index, to_col] not in ldict.values():
                continue
            for pkey, pval in ldict.items():
                if pval != rtable_df.at[index, to_col]:
                    continue
                ldict.pop(pkey)
        # ##run##
        self.sos_reconciler.create_namerecon_file(
                self.ltable_columns,
                self.rtable_columns,
                )
        # fetch JSON dict
        self.assertTrue(self.namerecon_path.exists())
        with open(str(self.namerecon_path)) as rfile:
            ltable_to_rtable = json.load(rfile)
        self.assertIsInstance(ltable_to_rtable, dict)
        # assert all values are null
        self.assertSetEqual(set(ltable_to_rtable.values()), {None})
        # assert all keys match {right - left}
        self.assertSetEqual(set(ltable_to_rtable), set(ldict))

if __name__ == '__main__':
    pass
