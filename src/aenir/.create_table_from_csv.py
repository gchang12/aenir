#!/usr/bin/python3
"""
Auxiliary module for loading CSV data into db-tables.
"""

import argparse
import sqlite3
import csv
from pathlib import Path

#from aenir._logging import logger

# TODO: Weapons should all be in one table.

def convert_to_numeric(record, nonnumeric_columns):
    """
    Converts values in a record to numerical form, zero'ing them out if necessary.
    """
    new_record = {}
    # get nonnumeric values
    for column in nonnumeric_columns:
        new_record[column] = record.pop(column)
    # this contains only the numeric fields
    fields = tuple(record.keys())
    # get numeric fields; if error, set to zero
    for field in fields:
        try:
            new_record[field] = int(record[field])
        except ValueError:
            new_record[field] = 0
    return new_record

def create_table_from_csv(path_to_csv, path_to_db, cs_nonnumeric_columns):
    """
    Creates SQL table in db-file and loads it with data from the CSV table.
    """
    nonnumeric_columns = cs_nonnumeric_columns.split(",")
    with open(path_to_csv) as rfile:
        records = tuple(map(lambda record: convert_to_numeric(record, nonnumeric_columns), csv.DictReader(rfile)))
        fields = tuple(records[0].keys())
    name_of_table = Path(path_to_csv).with_suffix("").name
    create_stmt = f"CREATE TABLE '{name_of_table}'({', '.join(fields)});"
    insertion_values = ", ".join(map(lambda field: ":" + field, fields))
    insert_stmt = f"INSERT INTO '{name_of_table}' VALUES ({insertion_values});"
    query_stmt = f"SELECT COUNT(*) FROM '{name_of_table}';"
    with sqlite3.connect(path_to_db) as cnxn:
        cnxn.row_factory = sqlite3.Row
        print("%s" % create_stmt)
        cnxn.execute(create_stmt)
        print("%s" % insert_stmt)
        cnxn.executemany(insert_stmt, records)
        print("%s" % query_stmt)
        (num_rows_written,) = cnxn.execute(query_stmt).fetchone()
    print("(%d) rows from '%s' have been written to '%s:%s'." % (num_rows_written, path_to_csv, path_to_db, name_of_table))
    return num_rows_written

parser = argparse.ArgumentParser()
parser.add_argument("path_to_csv", type=str)
parser.add_argument("path_to_db", type=str)
parser.add_argument("cs_nonnumeric_columns", type=str)
args = parser.parse_args()
path_to_csv = args.path_to_csv
path_to_db = args.path_to_db
cs_nonnumeric_columns = args.cs_nonnumeric_columns
# invoke main
print("create_table_from_csv('%s', '%s', '%s')" % (path_to_csv, path_to_db, cs_nonnumeric_columns))
create_table_from_csv(path_to_csv, path_to_db, cs_nonnumeric_columns)
#
