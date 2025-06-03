"""
"""

import sqlite3
from aenir.games import FireEmblemGame
from pathlib import Path
import json

# one JSON file -> one table

def dump_json_into_db(json_path, table_name, db_path):
    # load from JSON
    with open(json_path) as rfile:
        #with open("static/binding-blade/characters__base_stats-JOIN-classes__maximum_stats.json") as rfile:
        data = json.load(rfile)
    # save to database
    #table_name = "characters__base_stats-JOIN-classes__maximum_stats"
    print(json_path)
    with sqlite3.connect(db_path) as cnxn:
        #with sqlite3.connect("static/binding-blade/cleaned_stats.db") as cnxn:
        cnxn.execute("CREATE TABLE '%s'(Name, Alias)" % table_name)
        print(data)
        cnxn.executemany("INSERT INTO '%s' VALUES(?, ?)" % table_name, data.items())

for game in FireEmblemGame:
    url_name = game.url_name
    db_path = f"static/{url_name}/cleaned_stats.db"
    for json_path in filter(lambda path: "JOIN" in path.name, Path(f"static/{url_name}").iterdir()):
        table_name = json_path.with_suffix("").name
        dump_json_into_db(json_path, table_name, db_path)
