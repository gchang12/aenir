#!/usr/bin/python3
"""
"""

import logging
import json
import re
from typing import List

import pandas as pd


def remove_nonnumeric_rows(df: pd.DataFrame):
    """
    Deletes rows with a nonnumeric value
    in a numeric column.
    """
    pass

def convert_to_int_df(df: pd.DataFrame):
    """
    Converts pd.DataFrame.dtypes to int.
    """
    pass

def create_field_mapfile(df_list: List[pd.DataFrame]):
    """
    Creates a file to map the field names of all pd.DataFrame objects.
    """
    pass

def remap_foreignprimary_keys(df1: pd.DataFrame, df2: pd.DataFrame):
    """
    Matches foreign-primary key pairs so that
    they are ready to be cross-referenced.
    """
    pass

if __name__ == '__main__':
    pass
