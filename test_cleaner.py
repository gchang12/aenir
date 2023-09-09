#!/usr/bin/python3
"""
"""

import re
import json
import unittest
from unittest.mock import patch

from aenir.cleaner import SerenesCleaner


class CleanerTest( unittest.TestCase ):
    """
    """

    def setUp( self ):
        """
        """
        self.sos_cleaner = SerenesCleaner( 6 )
        # compile tables if they don't exist
        if not self.sos_cleaner.home_dir.joinpath( self.sos_cleaner.tables_file ).exists():
            for urlpath in self.sos_cleaner.page_dict:
                self.sos_cleaner.scrape_tables( urlpath )
                self.sos_cleaner.save_tables( urlpath )
        for urlpath in self.sos_cleaner.page_dict:
            self.sos_cleaner.load_tables( urlpath )
        self.sos_cleaner.fieldrecon_file = "MOCK-" + self.sos_cleaner.fieldrecon_file
        self.clsrecon_path = self.sos_cleaner.home_dir.joinpath(
                "MOCK-characters__base_stats-JOIN-classes__maximum_stats.json" 
                )

    def tearDown( self ):
        """
        """
        self.sos_cleaner.home_dir.joinpath( self.sos_cleaner.fieldrecon_file ).unlink( missing_ok=True )
        self.clsrecon_path.unlink( missing_ok=True )

    def test_drop_nonnumeric_rows( self ):
        """
        """
        # nothing can go wrong
        urlpath = "characters/base-stats"
        # main
        self.sos_cleaner.drop_nonnumeric_rows( urlpath )
        # check that all rows in a numeric column are numeric
        nonnumeric_columns = ( "Name" , "Class" , "Affin" , "Weapon ranks" )
        # for filter call
        def is_numeric_col(col: object):
            """
            """
            return col not in nonnumeric_columns
        # commence check
        for df in self.sos_cleaner.url_to_tables[ urlpath ]:
            for num_col in filter( is_numeric_col , df.columns ):
                for stat in df.loc[:, num_col]:
                    self.assertTrue( re.fullmatch( "[+-]?[0-9]+" , str(stat) ) is not None )

    def test_replace_with_int_df( self ):
        """
        """
        # nothing can go wrong
        urlpath = "characters/base-stats"
        bases = self.sos_cleaner.url_to_tables[ urlpath ][ 0 ]
        former_hp = int( bases.at[ 0 , "HP" ] )
        bases.at[ 0 , "HP" ] = str( bases.at[ 0, "HP" ] ) + " *"
        former_def = int( bases.at[ 0 , "Def" ] )
        bases.at[ 0 , "Def" ] = "-" + str( bases.at[ 0, "Def" ] )
        # main
        self.sos_cleaner.replace_with_int_df( urlpath )
        # check that all rows in a numeric column are numeric
        nonnumeric_columns = ( "Name" , "Class" , "Affin" , "Weapon ranks" )
        # for filter call
        def is_numeric_col(col: object):
            """
            """
            return col not in nonnumeric_columns
        # commence check
        for df in self.sos_cleaner.url_to_tables[ urlpath ]:
            for num_col in filter( is_numeric_col , df.columns ):
                for stat in df.loc[:, num_col]:
                    # recall that non-numeric rows have not been dropped yet
                    if stat == num_col:
                        continue
                    self.assertIsInstance( stat, int )
        bases = self.sos_cleaner.url_to_tables[ urlpath ][ 0 ]
        # nonnumerics stay intact
        self.assertEqual( bases.at[ 0 , "Name" ] , "Roy" )
        # bad stats are replaced
        self.assertEqual( bases.at[ 0 , "HP" ] , former_hp )
        self.assertEqual( bases.at[ 0 , "Def" ] , -former_def )

    def test_create_fieldrecon_file__file_exists( self ):
        """
        """
        # the file may already exist
        fieldrecon_path = self.sos_cleaner.home_dir.joinpath( self.sos_cleaner.fieldrecon_file )
        fieldrecon_path.write_text( "" )
        # saving old stat to compare against post-call result
        old_stat = fieldrecon_path.stat()
        with self.assertRaises( FileExistsError ):
            self.sos_cleaner.create_fieldrecon_file()
        # file must remain untouched
        self.assertEqual( old_stat , fieldrecon_path.stat() )

    def test_create_fieldrecon_file( self ):
        """
        """
        fieldrecon_path = str( self.sos_cleaner.home_dir.joinpath( self.sos_cleaner.fieldrecon_file ) )
        # compile fieldnames
        fieldnames = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                fieldnames.update( set( table.columns ) )
        # main
        self.sos_cleaner.create_fieldrecon_file()
        with open( fieldrecon_path , encoding='utf-8' ) as rfile:
            fieldrecon_dict = json.load( rfile )
        self.assertSetEqual( set( fieldrecon_dict ) , fieldnames )
        self.assertSetEqual( set( fieldrecon_dict.values() ) , { None } )

    def test_apply_fieldrecon_file__failures( self ):
        """
        """
        # 1: the file may not exist
        fieldrecon_path = str( self.sos_cleaner.home_dir.joinpath( self.sos_cleaner.fieldrecon_file ) )
        # compile before-fieldnames to check against after-fieldnames after failed call
        old_fieldnames = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                old_fieldnames.update( set( table.columns ) )
        # main: fails because the file does not exist
        with self.assertRaises( FileNotFoundError ):
            self.sos_cleaner.apply_fieldrecon_file()
        # compile after-fieldnames
        new_fieldnames = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                new_fieldnames.update( set( table.columns ) )
        # compare
        self.assertSetEqual( new_fieldnames , old_fieldnames )
        # 2: there may be nulls in the file
        fieldrecon_dict = { "HP": "health-points" , "Def": None }
        # check that weird HP alias does not exist in the fieldname set
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                self.assertNotIn( "health-points" , table.columns )
        with open( fieldrecon_path , mode='w', encoding='utf-8' ) as wfile:
            json.dump( fieldrecon_dict , wfile )
        with self.assertRaises( ValueError ):
            self.sos_cleaner.apply_fieldrecon_file()
        # check that weird HP alias still does not exist in the fieldname set
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                self.assertNotIn( "health-points" , table.columns )

    def test_apply_fieldrecon_file( self ):
        """
        """
        fieldrecon_dict = {
                "Name": "Name",
                "Class": "Class",
                "Affin": "DROP!",
                "Weapon ranks": "DROP!",
                "HP": "health-points",
                }
        fieldrecon_path = str( self.sos_cleaner.home_dir.joinpath( self.sos_cleaner.fieldrecon_file ) )
        with open( fieldrecon_path , mode='w', encoding='utf-8' ) as wfile:
            json.dump( fieldrecon_dict , wfile )
        # compile old fieldset for comparison
        old_fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                old_fieldset.update( set( table.columns ) )
        # main
        self.sos_cleaner.apply_fieldrecon_file()
        # compile new fieldset
        new_fieldset = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                new_fieldset.update( set( table.columns ) )
        self.assertFalse( { "Affin" , "Weapon ranks" , "DROP!" }.issubset( new_fieldset ) )
        self.assertIn( "health-points" , new_fieldset )

    # may have to mock some io-stuff
    @patch( "aenir.cleaner.SerenesCleaner.home_dir.joinpath" )
    def test_create_clsrecon_file__file_exists( self , mock_clsrecon_file ):
        """
        """
        ltable_columns = ( "characters/base-stats" , "Class" )
        rtable_columns = ( "characters/maximum-stats" , "Class" )
        # 1: the file may already exist
        self.clsrecon_path.write_text( "" )
        old_stat = self.clsrecon_path.stat()
        # main: fails because the file exists
        with self.assertRaises( FileExistsError ):
            self.sos_cleaner.create_clsrecon_file( ltable_columns , rtable_columns )
        # existing file is unchanged
        self.assertEqual( old_stat , clsrecon_file.stat() )

    # may have to mock some stuff
    @patch( "aenir.cleaner.SerenesCleaner.home_dir.joinpath" )
    def test_create_clsrecon_file( self , mock_clsrecon_file ):
        """
        """
        pass

    @patch( "aenir.cleaner.SerenesCleaner.home_dir.joinpath" )
    def test_verify_clsrecon_file__file_dne( self , mock_clsrecon_file ):
        """
        """
        pass

    @patch( "aenir.cleaner.SerenesCleaner.home_dir.joinpath" )
    def test_verify_clsrecon_file( self , mock_clsrecon_file ):
        """
        """
        # false positives
        # false negatives
        pass


if __name__ == '__main__':
    unittest.main()
