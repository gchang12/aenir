#!/usr/bin/python3
"""
"""

from aenir.transcriber import SerenesTranscriber

class BaseMorph(SerenesTranscriber):
    """
    """

    def __init__(self, game_num: int):
        """
        """
        SerenesTranscriber.__init__(self, game_num)
        # essential to set_targetstats method
        self.current_clstype = "characters/base-stats"
        self.current_cls = None
        self.target_stats = None

    def verify_clsrecon_file(self, ltable_args: Tuple[str, str, str], rtable_args: Tuple[str, str]):
        """
        """
        # unpack arguments
        ltable_url, lpkey, from_col = ltable_args
        rtable_url, to_col = rtable_args
        # load clsrecon_dict
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with io.open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        # compile ltable pkey names
        ltable_nameset = set()
        for table in self.url_to_tables[ltable_url]:
            ltable_nameset.update(set(table.loc[:, lpkey]))
        # compile rtable values
        rtable_nameset = set()
        for table in self.url_to_tables[rtable_url]:
            rtable_nameset.update(set(table.loc[:, to_col]))

if __name__ == '__main__':
    pass
