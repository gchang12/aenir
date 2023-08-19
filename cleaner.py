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
        SerenesScraper.__init__(self, game_num)


if __name__ == '__main__':
    x = SerenesCleaner(6)
