#!/usr/bin/python3
"""
"""

from aenir.morph import Morph

class Morph5(Morph):
    """
    """

    def __init__(self, unit_name: str, *, datadir_root: str = None):
        """
        """
        game_num = 5
        tableindex = 0
        Morph.__init__(game_num, unit_name, tableindex=tableindex, datadir_root=datadir_root)

    def promote(self):
        """
        """
        if self.current_cls == "Thief Fighter" and self.unit_name != "Lara":
            raise ValueError(f"{self.unit_name} has no available promotions.")
        elif self.unit_name == "Lara" and len(self.history == 3):
            raise ValueError(f"{self.unit_name} has no available promotions.")
        Morph.promote()

if __name__ == '__main__':
    pass
