#!/usr/bin/python3
"""
"""

import aenir.morph
from aenir._basemorph import BaseMorph

def get_morph(game_num: int, unit_name: str, **kwds):
    morph_cls = getattr(aenir.morph, "Morph" + str(game_num))
    morph_inst = morph_cls(unit_name, **kwds)
    return morph_inst

def get_character_list(game_num: int, *, datadir_root: str = "data"):
    basemorph_inst = BaseMorph(game_num, datadir_root=datadir_root)
    return basemorph_inst.get_character_list()


if __name__ == '__main__':
    pass
