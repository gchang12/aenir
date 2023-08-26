#!/usr/bin/python3
"""
Defines methods to clean up data for use in interactive stat-comparison session.
"""

from aenir.scraper import SerenesScraper
import re
import json

class SerenesCleaner(SerenesScraper):
    """
    Inherits: SerenesScraper
    Defines methods for data cleanup process.
    """

    def __init__(self, game_num):
        """
        Defines:
        - gender_dict: dict[character_name] = 'M|F|.*'
        - field_dict: dict[oldfiled] = newfield
        """
        SerenesScraper.__init__(self, game_num, check_if_url_exists=False)
        self.gender_dict = {}
        self.field_dict = {}

    def create_field_consolidation_file(self, filename):
        """
        Loop over all tables.
        Compile field names.
        Create dict of field names to be mapped to a common standard.
        Saves dict to JSON
        """
        field_set = set()
        for table in self.url_to_tables.values():
            field_set.update(set(table.columns))
        field_dict = {field: None for field in field_set}
        with open(filename, mode='w', encoding='utf-8') as wfile:
            json.dump(field_dict, wfile)

    def load_field_consolidation_file(self, filename):
        """
        Loop over all tables.
        Renames the column indices per JSON dict.
        Fails if any of the names in the dict is blank.
        """
        with open(filename, encoding='utf-8') as rfile:
            field_dict = json.load(rfile)
        if None in field_dict.values():
            raise ValueError
        for table in self.url_to_tables.values():
            table.rename(field_dict, axis=1, inplace=True)

    def replace_with_int_dataframes(self, urlpath, columns):
        """
        Loop over self.url_to_tables[urlpath]
        Replace each table with a table with numerical data.
        - re.sub [^0-9]*([0-9]+)[^0-9].* -> \\1
        - int
        """
        def convert_to_int(cell):
            """
            Converts cell-text to int-compatible format,
            then converts the text to int.
            1.  Each numerical cell should be left-stripped of non-digits.
            2.  Each numerical cell should be right-stripped of everything after
                the first non-digit in the sequence.
            """
            new_cell = re.sub("[^0-9]*([0-9]+)[^0-9].*", "\\1", cell)
            return int(new_cell)
        for index, table in enumerate(self.url_to_tables[urlpath]):
            self.url_to_tables[index] = table.applymap(convert_to_int)

    def create_class_reconciliation_file(self, sections_columns):
        """
        sections_columns:
        - 1: left table
        - 2: right table
        - 3: column in left table
        - 4: column in right table
        Creates dict of rows in 3 that don't match
        that in 4. Saves that dict to JSON file with
        filename: '1_JOIN_2.json'.
        """
        left_table, right_table, ltable_col, rtable_col = section_columns
        left_cls_set = set()
        right_cls_set = set()
        for ltable in self.url_to_tables[left_table]:
            left_cls_set.update(set(ltable.loc[:, ltable_col]))
        for rtable in self.url_to_tables[right_table]:
            right_cls_set.update(set(rtable.loc[:, rtable_col]))
        cls_dict = {lname: None for lname in left_cls_set.difference(right_cls_set)}
        filename = f"{left_table}_JOIN_{right_table}.json"
        with open(filename, mode='w', encoding='utf-8') as wfile:
            json.dump(cls_dict, wfile)

    def load_class_reconciliation_file(self, sections_columns, filename):
        """
        sections_columns:
        - 1: left table
        - 2: right table
        - 3: column in left table
        - 4: column in right table
        Loads dict from 1_JOIN_2.json
        If there are unmapped names, quit.
        Creates a pd.DataFrame to match 1.3 to 2.4
        with filename
        Also loads gender file if applicable
        """
        left_table, right_table, ltable_col, rtable_col = section_columns
        if left_table.starts_with("characters"):
            gender_dict = {}
            pass

    def create_gender_file(self, filename):
        """
        Creates a list of character names to
        be mapped to gender, if they belong to a
        class whose genders have different stats.
        """
        table_name = "characters/base-stats"
        character_set = set()
        for table in self.url_to_tables[table_name]:
            character_set.update(set(table.iloc[:, 0]))
        character_dict = {char: None for char in character_set}
        with open(filename, mode='w', encoding='utf-8') as wfile:
            json.dump(character_dict, wfile)

if __name__ == '__main__':
    x = SerenesCleaner(6)
