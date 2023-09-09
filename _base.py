#!/usr/bin/python3
"""
"""

class SerenesBase:

    _URL_ROOT = "https://serenesforest.net"

    _NUM_TO_NAME = {
            4: "genealogy-of-the-holy-war",
            5: "thracia-776",
            6: "binding-blade",
            7: "blazing-sword",
            8: "the-sacred-stones",
            9: "path-of-radiance",
            }

    def __init__( self , game_num: int ):
        self._game_num = game_num
        #!will raise KeyError if not found
        self._game_name = self.NUM_TO_NAME[ self.game_num ]

    @property
    def game_num( self ):
        return self._game_num

    @property
    def game_name( self ):
        return self._game_name

    @property
    def URL_ROOT( self ):
        return self._URL_ROOT

    @property
    def NUM_TO_NAME( self ):
        return self._NUM_TO_NAME


if __name__ == '__main__':
    breakpoint()
