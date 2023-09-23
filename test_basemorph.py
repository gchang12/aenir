#!/usr/bin/python3
"""
"""

import unittest

from aenir._basemorph import BaseMorph

class BaseMorphTest(unittest.TestCase):

    def setUp(self):
        """
        """
        self.sos_unit = BaseMorph(6)

    def test_verify_clsrecon_file(self):
        """
        """
        # [lr]table_url not in self.page_dict
        # {ltable_name}-JOIN-{rtable_name}.json DNE
        # lpkey not in ltable
        # to_col not in rtable
        ltable_url = "characters/base-stats"
        rtable_url = "classes/promotion-gains"
        lpkey = "Name"
        from_col = "Class"
        to_col = "Class"


if __name__ == '__main__':
    pass
