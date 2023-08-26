#!/usr/bin/python3
"""
"""

from aenir.scraper import SerenesScraper

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
        pass

    def load_field_consolidation_file(self):
        """
        Loop over all tables.
        Renames the column indices per JSON dict.
        Fails if any of the names in the dict is blank.
        """
        pass

    def replace_with_int_dataframes(self, urlpath, columns):
        """
        Loop over self.url_to_tables[urlpath]
        Replace each table with a table with numerical data.
        - re.sub [^0-9]([0-9]+)[^0-9] -> \\1
        - int
        """
        pass

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
        pass

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
        pass

    def create_gender_file(self, filename):
        """
        Creates a list of character names to
        be mapped to gender, if they belong to a
        class whose genders have different stats.
        """
        pass


if __name__ == '__main__':
    x = SerenesCleaner(6)
