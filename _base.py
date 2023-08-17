#!/usr/bin/python3
"""
Defines the SerenesBase class
"""

from pathlib import Path

class SerenesBase:
    """
    Defines data directories for use by
    descendants, including the scraper
    and data management classes.
    """
    def __init__(self, game_name: str):
        """
        Initialize:
        - game_name: One of the folders in the serenesforest.net site
        - home_dir: pathlib.Path object to the directory
        """
        self.game_name = game_name
        self.home_dir = Path("data", self.game_name)
        self.url_to_tables = {}

    def get_datafile_path(self, filename: str):
        """
        Returns a path to a data file in the home directory
        """
        return self.home_dir / Path(filename)

    def urlpath_to_tablename(self, urlpath: str):
        """
        Converts urlpath-like str to tablename str.
        """
        return urlpath.replace("/", "__").replace("-", "_")

    def tablename_to_urlpath(self, tablename: str):
        """
        Converts tablename-like str to urlpath.
        """
        return tablename.replace("__", "/").replace("_", "-")

if __name__ == '__main__':
    pass
