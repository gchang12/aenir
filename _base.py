#!/usr/bin/python3
"""
Defines the SerenesBase class
"""
# pylint: disable=R0903

from pathlib import Path

class SerenesBase:
    """
    Defines data directories for use by
    descendants, including the scraper
    and data management classes.
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
        Initialize:
        - game_name: One of the folders in the serenesforest.net site
        - home_dir: pathlib.Path object to the directory
        """
        self._game_num = game_num
        self._page_dict = self.URL_TO_TABLE.copy()
        self._game_name = self.NUM_TO_NAME[self._game_num]
        self._home_dir = Path("data", self._game_name)
        self._url_to_tables = {}

    @property
    def URL_TO_TABLE(self):
        """
        Get:    {urlpath: urlpath.replace("/", "__").replace("-", "_")
        """
        return self._URL_TO_TABLE

    @property
    def NUM_TO_NAME(self):
        """
        Get:    {num: game-title as it appears on SF.net}
        """
        return self._NUM_TO_NAME

    @property
    def game_num(self):
        """
        Get:    The number of the game in the Fire Emblem series.
        """
        return self._game_num

    @property
    def page_dict(self):
        """
        Get:    dict that maps urlpath -> table_name
        """
        return self._page_dict

    @property
    def game_name(self):
        """
        Get:    str representing the name of the game as shown in the urlpath.
        """
        return self._game_name

    @property
    def home_dir(self):
        """
        Get:    pathlib.Path to the directory where all scraped data for the game is stored.
        """
        return self._home_dir

    @property
    def url_to_tables(self):
        """
        Get:    dict that maps urlpath -> List[stat_tables]
        """
        return self._url_to_tables

    def get_datafile_path(self, filename: str):
        """
        Returns a path to a data file in the home directory
        """
        return self.home_dir.joinpath(filename)

    def get_urlname(self, tablename: str):
        """
        Maps: str -> str.replace(self, "__", "/").replace("_", "-")
        """
        return tablename.replace("__", "/").replace("_", "-")

if __name__ == '__main__':
    pass
