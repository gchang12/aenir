#!/usr/bin/python3
"""
"""

from typing import Tuple
import re
import json
import io

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
        self.cls_recon_list = [
                ( ( "characters/base-stats" , "Name" ) , ( "characters/growth-rates" , "Name" ) ),
                ( ( "characters/base-stats" , "Class" ) , ( "classes/maximum-stats" , "Class" ) ),
                ( ( "characters/base-stats" , "Class" ) , ( "classes/promotion-gains" , "Class" ) ),
                ( ( "classes/promotion-gains" , "Promotion" ) , ( "classes/maximum-stats" , "Class" ) ),
                ]


    def drop_nonnumeric_rows( self , urlpath: str , numeric_col: str = "Def" ):
        """
        """
        for index, table in enumerate( self.url_to_tables[ urlpath] ):
            self.url_to_tables[ urlpath][ index] = table[
                    pd.to_numeric( table[ numeric_col] , errors='coerce' ).notnull()
                    ]

    def replace_with_int_df( self , urlpath: str ):
        """
        """

        def replace_with_int( cell: str ) -> int:
            """
            """
            # convert cell to str, then replace it with a numeric str
            new_cell = re.sub( "[^0-9+-]*([-+]?[0-9]+).*" , "\\1" , str( cell ) )
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
            for index, table in enumerate(tablelist):
                try:
                    tablelist[ index ] = table.rename( columns=fieldrecon_dict ).drop( columns=["DROP!"] )
                except KeyError:
                    tablelist[ index ] = table.rename( columns=fieldrecon_dict )

    def create_clsrecon_file( self , ltable_columns: Tuple[ str , str ] , rtable_columns: Tuple[ str , str ] ):
        """
        """
        # unpack variables
        ltable_url, fromcol_name = ltable_columns
        rtable_url, tocol_name = rtable_columns
        # map urlpaths to tablenames
        ltable_name = self.page_dict[ ltable_url ]
        rtable_name = self.page_dict[ rtable_url ]
        # create Path for write-destination
        clsrecon_json = self.home_dir.joinpath( f"{ltable_name}-JOIN-{rtable_name}.json" )
        if clsrecon_json.exists():
            raise FileExistsError
        # resultset := (SELECT ltable.iloc[ 0, :] WHERE ltable[ fromcol] NOT IN rtable[tocol]);
        target_set = set()
        for rtable in self.url_to_tables[ rtable_url ]:
            target_set.update( set( rtable.loc[ : , tocol_name ] ) )
        clsrecon_dict = {}
        for ltable in self.url_to_tables[ ltable_url ]:
            clsrecon_dict.update(
                    {
                        primary_key: None for primary_key in
                        ltable[ ~ltable[ fromcol_name ].isin( target_set ) ].iloc[ : , 0 ]
                        }
                    )
        # save: {result: null for result in resultset} |-> ltable-JOIN-rtable.json
        with io.open( str( clsrecon_json ) , mode="w" , encoding="utf-8" ) as wfile:
            json.dump( clsrecon_dict , wfile , indent=4 )

    def verify_clsrecon_file( self , ltable_url: str , rtable_columns: Tuple[ str , str ] ):
        """
        """
        # unpack variables
        rtable_url, tocol_name = rtable_columns
        # map urlpaths to tablenames
        ltable_name = self.page_dict[ ltable_url ]
        rtable_name = self.page_dict[ rtable_url ]
        # create Path for write-destination
        clsrecon_json = self.home_dir.joinpath( f"{ltable_name}-JOIN-{rtable_name}.json" )
        with io.open( str( clsrecon_json ) , encoding='utf-8' ) as rfile:
            clsrecon_dict = json.load( rfile )
        # compile list of names to compare against
        rtable_set = set()
        for rtable in self.url_to_tables[ rtable_url ]:
            rtable_set.update( set( rtable.loc[ : , tocol_name ] ) )
        nomatch_set = set()
        for ltable in self.url_to_tables[ ltable_url ]:
            # check if ltable-values are in rtable_set
            for lkey in ltable.iloc[ : , 0 ]:
                try:
                    if clsrecon_dict[ lkey ] is None or clsrecon_dict[ lkey ] in rtable_set:
                        continue
                    nomatch_set.add( lkey )
                except KeyError:
                    continue
        return nomatch_set

if __name__ == '__main__':
    pass
