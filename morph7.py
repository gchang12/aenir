#!/usr/bin/python3
"""
Defines Morph7 class.

Morph: Defines methods to simulate level-ups and promotions for FE7 units.
"""

from aenir.morph import Morph

class Morph7(Morph):
    """
    Defines methods to simulate level-ups and promotions for interactive user session.
 
    Inherits: Morph
    - differs in that the Wallace exception is added.
    """

    def __init__(self, unit_name: str, lyn_mode: bool = False, *, datadir_root: str = None):
        """
        Implements: Morph.__init__

        - Adds Wallace exception
        - Allows user to choose Lyn Mode or otherwise
        """
        tableindex = (1 if lyn_mode else 0)
        Morph.__init__(self, 7, unit_name, tableindex=tableindex, datadir_root=datadir_root)
        if not lyn_mode and unit_name == "Wallace":
            # must add in line with 'General (M)' -> None in promo-JOIN-promo JSON file
            self.current_clstype = "classes/promotion-gains"

if __name__ == '__main__':
    pass
