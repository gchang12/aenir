"""
"""

import csv
import sqlite3

def _convert_to_numeric(row):
    """
    """
    for field, value in row.items():
        try:
            new_value = int(value)
        except ValueError:
            new_value = value
        row[field] = new_value
    #return row

def grab_csv_data(filename):
    """
    """
    with open(filename) as rfile:
        data = list(csv.DictReader(rfile))
    map(_convert_to_numeric, data)
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
    condition = ", ".join(field + "=:" + field for field in key_fields)
    statement = "UPDATE TABLE %s SET %s WHERE %s ;" % (table, action, condition)
    print(statement)
    print(data[0])
    with sqlite3.connect(filename) as cnxn:
        cnxn.executemany(statement, data)

# grab csv data
# make it as numeric as possible
# all string fields should act as keys
# all numeric fields should act as values
# update db with csv data corresponding to table that csv name corresponds to
