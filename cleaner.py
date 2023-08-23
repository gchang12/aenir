#!/usr/bin/python3
"""
"""

from aenir.scraper import SerenesScraper

class SerenesCleaner(SerenesScraper):
    """
    """
    def __init__(self, game_num):
        """
        """
        SerenesScraper.__init__(self, game_num, check_if_url_exists=False)
        self.gender_dict = {}

    def create_field_consolidation_file(self):
        """
        """
        pass

    def load_field_consolidation_file(self):
        """
        """
        pass

    def replace_with_int_dataframes(self):
        """
        """
        pass

    def create_class_reconciliation_file(self):
        """
        """
        pass

    def load_class_reconciliation_file(self):
        """
        """
        pass

    def create_gender_file(self):
        """
        """
        pass


if __name__ == '__main__':
    x = SerenesCleaner(6)
