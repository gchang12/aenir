#!/usr/bin/python3
"""
"""

from pathlib import Path

class SerenesBase:
    """
    """

    _NUM_TO_NAME = {
            4: "genealogy-of-the-holy-war",
            5: "thracia-776",
            6: "binding-blade",
            7: "blazing-sword",
            8: "the-sacred-stones",
            9: "path-of-radiance",
            }

    _URL_TO_TABLE = {
            "characters/base-stats": "characters__base_stats",
            "characters/growth-rates": "characters__growth_rates",
            "classes/maximum-stats": "classes__maximum_stats",
            "classes/promotion-gains": "classes__promotion_gains",
            }

    def __init__(self, game_num: int):
        """
        """
        self._game_num = game_num
        self._page_dict = self.URL_TO_TABLE.copy()
        self._game_name = self.NUM_TO_NAME[self._game_num]
        self._home_dir = Path("data", self._game_name)
        self._url_to_tables = {}

    @property
    def URL_TO_TABLE(self):
        """
        """
        return self._URL_TO_TABLE

    @property
    def NUM_TO_NAME(self):
        """
        """
        return self._NUM_TO_NAME

    @property
    def game_num(self):
        """
        """
        return self._game_num

    @property
    def page_dict(self):
        """
        """
        return self._page_dict

    @property
    def game_name(self):
        """
        """
        return self._game_name

    @property
    def home_dir(self):
        """
        """
        return self._home_dir

    @property
    def url_to_tables(self):
        """
        """
        return self._url_to_tables

    def get_datafile_path(self, filename: str):
        """
        """
        return self.home_dir.joinpath(filename)

    def get_urlname(self, tablename: str):
        """
        """
        urlname = tablename.replace("__", "/").replace("_", "-")
        assert urlname in self.page_dict
        return urlname

if __name__ == '__main__':
    pass
