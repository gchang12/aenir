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
    NUM_TO_NAME = {
            4: "genealogy-of-the-holy-war",
            5: "thracia-776",
            6: "binding-blade",
            7: "blazing-sword",
            8: "the-sacred-stones",
            9: "path-of-radiance",
            }
    def __init__(self, game_num: int):
        """
        Initialize:
        - game_name: One of the folders in the serenesforest.net site
        - home_dir: pathlib.Path object to the directory
        """
        self.game_num = game_num
        self.game_name = self.NUM_TO_NAME[self.game_num]
        self.home_dir = Path("data", self.game_name)
        self.url_to_tables = {}

    def get_datafile_path(self, filename: str):
        """
        Returns a path to a data file in the home directory
        """
        return self.home_dir / Path(filename)

if __name__ == '__main__':
    pass
