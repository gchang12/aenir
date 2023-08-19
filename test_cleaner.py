#!/usr/bin/python3
"""
"""

import unittest

import pandas as pd

class TestCleaning(unittest.TestCase):
    """
    Provides testing for functions that clean up
    pd.DataFrame objects to be referenced for stats.
    """

    def setUp(self):
        """
        Create generic pd.DataFrame objects for cleaning here.
        - One must have nonnumeric string data in numeric columns.
        - One must have a designated nonnumeric columns.
        - Two must be linked via non-matching foreign key set.
        """
        pass

    def test_remove_nonnumeric_rows(self):
        """
        Asserts that rows with a nonnumeric value
        in a numeric column are removed.
        """
        pass

    def test_convert_to_int_df(self):
        """
        Asserts that the pd.DataFrame.dtypes is int.
        """
        pass

    def test_create_field_mapfile(self):
        """
        Asserts that a file to map the field names of all
        pd.DataFrame objects is created.
        """
        pass

    def test_remap_foreignprimary_keys(self):
        """
        Tests that foreign-primary key pairs match,
        and are ready to be cross-referenced.
        """
        pass


if __name__ == '__main__':
    pass
