"""
"""

import argparse
import sqlite3
import csv
from pathlib import Path

from aenir.logging import logger

def create_table_from_csv(path_to_csv, path_to_db):
    """
    """
    with open(path_to_csv) as rfile:
        records = tuple(csv.DictReader(rfile))
        fields = tuple(records[0].keys())
    name_of_table = Path(path_to_csv).with_suffix("").name
    create_stmt = f"CREATE TABLE {name_of_table}({', '.join(fields)});"
    insertion_values = ", ".join(map(lambda field: ":" + field, fields))
    insert_stmt = f"INSERT INTO {name_of_table} VALUES ({insertion_values});"
    query_stmt = f"SELECT COUNT(*) FROM {name_of_table};"
    with sqlite3.connect(path_to_db) as cnxn:
        cnxn.row_factory = sqlite3.Row
        logger.debug("%s", create_stmt)
        cnxn.execute(create_stmt)
        logger.debug("%s", insert_stmt)
        cnxn.executemany(insert_stmt, records)
        logger.debug("%s", query_stmt)
        (num_rows_written,) = cnxn.execute(query_stmt)
    logger.debug("(%d) rows from '%s' have been written to '%s:%s'.", num_rows_written, path_to_csv, path_to_db, name_of_table)
    return num_rows_written

parser = argparse.ArgumentParser()
parser.add_argument("path_to_csv", type=str)
parser.add_argument("path_to_db", type=str)
args = parser.parse_args()
path_to_csv = args.path_to_csv
path_to_db = args.path_to_db
# invoke main
logger.debug("create_table_from_csv('%s', '%s')", path_to_csv, path_to_db)
create_table_from_csv(path_to_csv, path_to_db)
