#!/usr/bin/python3
"""
"""

import re
import json
import unittest

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

    def tearDown( self ):
        """
        """
        self.sos_cleaner.home_dir.joinpath( self.sos_cleaner.fieldrecon_file ).unlink( missing_ok=True )

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

    def test_create_fieldrecon_file( self ):
        """
        """
        # the file may already exist
        fieldrecon_path = self.sos_cleaner.home_dir.joinpath(self.sos_cleaner.fieldrecon_file)
        fieldrecon_path.write_text( "" )
        with self.assertRaises( FileExistsError ):
            self.sos_cleaner.create_fieldrecon_file()
        fieldrecon_path.unlink()
        # compile fieldnames
        fieldnames = set()
        for tablelist in self.sos_cleaner.url_to_tables.values():
            for table in tablelist:
                fieldnames.update( set( table.columns ) )
        # main
        self.sos_cleaner.create_fieldrecon_file()
        with open( str(fieldrecon_path) , encoding='utf-8' ) as rfile:
            fieldrecon_dict = json.load( rfile )
        self.assertSetEqual( set( fieldrecon_dict ) , fieldnames )
        self.assertSetEqual( set( fieldrecon_dict.values() ) , { None } )

    def test_apply_fieldrecon_file( self ):
        """
        """
        # the file may not exist
        pass

    def test_create_namerecon_file( self ):
        """
        """
        # the file may already exist
        pass

    def test_verify_namerecon_file( self ):
        """
        """
        # false positives
        # false negatives
        pass


if __name__ == '__main__':
    unittest.main()
