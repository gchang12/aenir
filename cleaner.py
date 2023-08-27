#!/usr/bin/python3
"""
Defines methods to clean up fields, null-rows, and non-int cells.
"""

from aenir.scraper import SerenesScraper
import re
import json

class SerenesCleaner(SerenesScraper):
    """
    Inherits: SerenesScraper.
    Defines methods for data cleanup process.
    """

    def __init__(self, game_num):
        """
        Defines filename to be manually filled
        for field cleanup process, in addition to parent
        attributes.
        """
        SerenesScraper.__init__(game_num, check_if_url_exists=False)
        self.fieldrecon_json = "fieldrecon.json"
