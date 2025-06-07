"""
"""

import csv
import sqlite3
from pathlib import Path

from aenir.games import FireEmblemGame

def _convert_to_numeric(row):
    """
    """
    for field, value in row.items():
        try:
            new_value = int(value)
        except ValueError:
            new_value = value
        row[field] = new_value
    return row

def grab_csv_data(filename):
    """
    """
    with open(filename) as rfile:
        data = list(csv.DictReader(rfile))
    data = list(map(_convert_to_numeric, data))
    print(data[0])
    return data

def update_db(filename, table, data):
    """
    """
    # identify which fields are numeric; which are not
    print(table)
    key_fields = list()
    value_fields = list()
    for field, value in data[0].items():
        if isinstance(value, str):
            key_fields.append(field)
        elif isinstance(value, int):
            value_fields.append(field)
    print(key_fields, value_fields)
    # TODO: How to put in query parameters...
    # field=:field as %r, ...
    action = ", ".join(field + "=:" + field for field in value_fields)
    condition = " AND ".join(field + "=:" + field for field in key_fields)
    statement = "UPDATE %s SET %s WHERE %s ;" % (table, action, condition)
    print(statement)
    print(data[0])
    print(filename)
    with sqlite3.connect(filename) as cnxn:
        cnxn.executemany(statement, data)

for game in FireEmblemGame:
    url_name = game.url_name
    print(url_name)
    for csv_path in Path(f"static/{url_name}/").glob("*.csv"):
        print(csv_path)
        #csv_name = f"static/{url_name}/{csv_file}"
        csv_data = grab_csv_data(csv_path)
        db_filename = f"static/{url_name}/cleaned_stats.db"
        table = csv_path.with_suffix("").name
        update_db(db_filename, table, csv_data)

# grab csv data
# make it as numeric as possible
# all string fields should act as keys
# all numeric fields should act as values
# update db with csv data corresponding to table that csv name corresponds to
