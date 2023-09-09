#!/usr/bin/python3
"""
"""

from typing import Tuple
import re
import json

import pandas as pd

from aenir.transcriber import SerenesTranscriber

class SerenesCleaner( SerenesTranscriber ):
    """
    """

    def __init__( self , game_num ):
        """
        """
        SerenesTranscriber.__init__( self , game_num )
        self.fieldrecon_file = "fieldrecon.json"

    def drop_nonnumeric_rows( self , urlpath: str , numeric_col: str = "Def" ):
        """
        """
        for index, table in enumerate(self.url_to_tables[urlpath]):
            self.url_to_tables[urlpath][index] = table[
                    pd.to_numeric(table[numeric_col], errors='coerce').notnull()
                    ]

    def replace_with_int_df( self , urlpath: str ):
        """
        """

        def replace_with_int( cell: str ) -> int:
            """
            """
            # convert cell to str, then replace it with a numeric str
            new_cell = re.sub( "[^0-9+-]*([-+]?[0-9]+).*" , "\\1", str( cell ) )
            # if the cell is numeric, return the int-cast version
            if re.fullmatch( "[-+]?[0-9]+" , new_cell ):
                return int( new_cell )
            # otherwise, return the original cell
            return cell

        for index, table in enumerate( self.url_to_tables[ urlpath ] ):
            int_df = table.applymap( replace_with_int )
            self.url_to_tables[ urlpath ][ index ] = int_df.convert_dtypes()

    def create_fieldrecon_file( self ):
        """
        """
        fieldrecon_json = self.home_dir.joinpath( self.fieldrecon_file )
        if fieldrecon_json.exists():
            raise FileExistsError
        fieldname_set = set()
        for tableset in self.url_to_tables.values():
            for table in tableset:
                fieldname_set.update( set( table.columns ) )
        fieldname_dict = { fieldname: None for fieldname in fieldname_set }
        with open( str( fieldrecon_json ) , mode='w' , encoding='utf-8' ) as wfile:
            json.dump( fieldname_dict , wfile , indent=4 )

    def apply_fieldrecon_file( self ):
        """
        """
        fieldrecon_json = str( self.home_dir.joinpath( self.fieldrecon_file ) )
        with open( fieldrecon_json , encoding='utf-8' ) as rfile:
            fieldrecon_dict = json.load( rfile )
        if None in fieldrecon_dict.values():
            raise ValueError
        for tablelist in self.url_to_tables.values():
            for table in tablelist:
                table.rename( columns=fieldrecon_dict , inplace=True )
                try:
                    table.drop( "DROP!" , inplace=True )
                except KeyError:
                    pass

    def create_clsrecon_file( self , ltable_columns: Tuple[ str , str ] , rtable_columns: Tuple[ str , str ] ):
        """
        """
        ltable, fromcol_name = ltable_columns
        rtable, tocol_name = rtable_columns
        # resultset := (SELECT ltable.iloc[0, :] WHERE ltable[fromcol] NOT IN rtable[tocol]);
        # save: {result: null for result in resultset} |-> ltable-JOIN-rtable.json
        pass

    def verify_clsrecon_file( self , ltable: str , rtable_columns: Tuple[ str , str ] ):
        """
        """
        pass


if __name__ == '__main__':
    pass
