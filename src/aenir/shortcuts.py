#!/usr/bin/python3
"""
Defines shortcuts to initialize a Morph and a character list.
"""

import aenir.morph
from aenir._basemorph import BaseMorph

def get_morph(game_num: int, unit_name: str, **kwds):
    """
    Shortcut to initialize a Morph.
    """
    morph_cls = getattr(aenir.morph, "Morph" + str(game_num))
    morph_inst = morph_cls(unit_name, **kwds)
    return morph_inst

def get_character_list(game_num: int, *, datadir_root: str = "data"):
    """
    Shortcut to get a list of characters.
    """
    basemorph_inst = BaseMorph(game_num, datadir_root=datadir_root)
    return basemorph_inst.get_character_list()


if __name__ == '__main__':
    pass
