#!/usr/bin/python3
"""
"""

from pathlib import Path

import pandas as pd

from aenir.scraper import SerenesScraper

class SerenesTranscriber( SerenesScraper ):
    """
    """
    
    def __init__( self , game_num: int ):
        """
        """
        SerenesScraper.__init__( self , game_num )
        self.home_dir = Path( "data" , self.game_name )
        self.tables_file = "raw_stats.db"

    def save_tables( self , urlpath: str ):
        """
        """
        # add in checks here
        if not self.url_to_tables[ urlpath ]:
            raise ValueError
        for table in self.url_to_tables[ urlpath ]:
            if type(table) == pd.DataFrame:
                continue
            raise TypeError
        if urlpath in self.url_to_tables:
            # real program starts here
            tablename = self.page_dict[ urlpath ]
            tableindex = 0
            self.home_dir.mkdir( exist_ok=True, parents=True )
            save_file = str( self.home_dir.joinpath( self.tables_file ) )
        while self.url_to_tables[ urlpath ]:
            table = self.url_to_tables[ urlpath ].pop(0)
            name = tablename + str( tableindex )
            con = "sqlite:///" + save_file
            table.to_sql( name, con, index=False )
            tableindex += 1
        del self.url_to_tables[ urlpath ]

    def load_tables( self , urlpath: str ):
        """
        """
        save_path = self.home_dir.joinpath( self.tables_file )
        if not save_path.exists():
            raise FileNotFoundError
        save_file = str( save_path )
        tablename_root = self.page_dict[ urlpath ]
        self.url_to_tables[ urlpath ] = []
        tableindex = 0
        while True:
            table_name = tablename_root + str( tableindex )
            con = "sqlite:///" + save_file
            try:
                table = pd.read_sql_table( table_name, con )
                tableindex += 1
                self.url_to_tables[ urlpath ].append( table )
            except ValueError:
                break

    def get_urlname_from_tablename( self , tablename: str ):
        """
        """
        urlname = tablename.replace( "__" , "/" ).replace( "_" , "-" )
        #!will raise AssertionError for invalid tablenames
        assert urlname in self.page_dict
        return urlname


if __name__ == '__main__':
    pass
