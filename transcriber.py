#!/usr/bin/python3
"""
"""

from pathlib import Path

from aenir.scraper import SerenesScraper

class SerenesTranscriber( SerenesScraper ):
    
    def __init__( self , game_num: int ):
        SerenesScraper.__init__( self , game_num )
        self.home_dir = Path( "data" , self.game_name )
        self.tables_file = "raw_stats.db"

    def get_datafile_path( self , filename: str):
        pass

    def save_tables( self , urlpath: str ):
        pass

    def load_tables( self , urlpath: str ):
        pass


if __name__ == '__main__':
    pass
