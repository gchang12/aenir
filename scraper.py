#!/usr/bin/python3
"""
"""

from pathlib import Path
import logging

import requests
import pandas as pd


class SerenesScraper:
    """
    """

    NUM_TO_NAME = {
            4: "genealogy-of-the-holy-war",
            5: "thracia-776",
            6: "binding-blade",
            7: "blazing-sword",
            8: "the-sacred-stones",
            9: "path-of-radiance",
            }

    URL_TO_TABLE = {
            "characters/base-stats": "characters__base_stats",
            "characters/growth-rates": "characters__growth_rates",
            "classes/maximum-stats": "classes__maximum_stats",
            "classes/promotion-gains": "classes__promotion_gains",
            }

    def __init__(self, game_num: int):
        """
        """
        # all of these attributes are implicitly properties
        self.game_num = game_num
        self.page_dict = self.URL_TO_TABLE.copy()
        self.game_name = self.NUM_TO_NAME[self.game_num]
        self.home_dir = Path("data", self.game_name)
        self.url_to_tables = {}

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
