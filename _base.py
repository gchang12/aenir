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
    TABLE_TO_URLPATH = {
            "characters_growthrates": "characters/growth-rates",
            "characters_basestats": "characters/base-stats",
            "classes_maximumstats": "classes/maximum-stats",
            "classes_promotiongains": "classes/promotion-gains",
            "classes_growthrates": "classes/growth-rates",
            }
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


if __name__ == '__main__':
    pass
