#!/usr/bin/python3
"""
"""

from aenir.transcriber import SerenesTranscriber

class SerenesCleaner( SerenesTranscriber ):

    def __init__( self , game_num ):
        SerenesTranscriber.__init__( self , game_num )

    def drop_nonnumeric_rows(self , urlpath: str , numeric_col: str = "Def"):
        pass

    def replace_with_int_df(self , urlpath: str):
        pass

    def create_fieldrecon_file(self):
        pass

    def apply_fieldrecon_file(self):
        pass

    def create_namerecon_file(self , ltable_columns: Tuple[str , str , str] , rtable_columns: Tuple[str , str]):
        pass

    def verify_namerecons(self , ltable: str , rtable_columns: Tuple[str , str]):
        pass

if __name__ == '__main__':
    pass
