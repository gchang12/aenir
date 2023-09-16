#!/usr/bin/python3
"""
Defines the SerenesBase class.

SerenesBase: Defines parameters for web-scraping.
"""

class SerenesBase:
    """
    Defines parameters for web-scraping serenesforest.net.

    URL_ROOT: URL of the website to be scraped.
    NUM_TO_NAME: Index that looks up FE title by game number.
    """

    _URL_ROOT = "https://serenesforest.net"
    _NUM_TO_NAME = {
            4: "genealogy-of-the-holy-war",
            5: "thracia-776",
            6: "binding-blade",
            7: "blazing-sword",
            8: "the-sacred-stones",
            9: "path-of-radiance",
            }

    def __init__(self, game_num: int):
        """
        Defines parameters that identify a FE game.
        """
        self._game_num = game_num
        #!will raise KeyError if not found
        self._game_name = self.NUM_TO_NAME[self._game_num]

    @property
    def game_num(self):
        """
        The number of a FE game in the series.
        """
        return self._game_num

    @property
    def game_name(self):
        """
        The name of a FE game, given the number.
        """
        return self._game_name

    @property
    def URL_ROOT(self):
        """
        URL of the website to be scraped.
        """
        return self._URL_ROOT

    @property
    def NUM_TO_NAME(self):
        """
        Index that looks up FE title by game number.
        """
        return self._NUM_TO_NAME


if __name__ == '__main__':
    pass
