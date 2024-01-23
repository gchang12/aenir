#!/usr/bin/python3
"""
"""

import aenir.morph

def get_morph(game_num: int, unit_name: str, *, **kwds):
    morph_cls = getattr(aenir.morph, "Morph" + str(game_num))
    morph_inst = morph_cls(unit_name, **kwds)
    return morph_inst


if __name__ == '__main__':
    pass
