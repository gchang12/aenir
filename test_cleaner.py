#!/usr/bin/python3
"""
Tests data-cleaning capabilities of SerenesCleaner.
"""

import logging
import unittest
import json

from aenir.cleaner import SerenesCleaner

class TestCleaner(unittest.TestCase):
    """
    Defines tests for SerenesCleaner.
    """

    def setUp(self):
        """
        Instance of SerenesCleaner must be initialized.
        All data must be compiled into a source.
        """
        self.consolidation_file = "mock_fieldconsolidation.json"
        self.datasource_file = "mock_datasource.db"
        self.sos_cleaner = SerenesCleaner(6)
        for page in self.sos_cleaner.page_dict:
            if not self.sos_cleaner.get_datafile_path(self.datasource_file).exists():
                self.sos_cleaner.scrape_tables(page, filename=self.datasource_file)
                self.sos_cleaner.save_tables(page, filename=self.datasource_file)
            self.sos_cleaner.load_tables(page, filename=self.datasource_file)

    def test_create_field_consolidation_file(self):
        """
        Asserts that a blank JSON file for mapping field names to
        a common standard is created.
        """
        self.sos_cleaner.create_field_consolidation_file(filename=self.consolidation_file)
        cfile_path = self.sos_cleaner.get_datafile_path(self.consolidation_file)
        self.assertTrue(cfile_path.exists())
        # JSON file must have dict mapping unique field names to None
        with open(self.sos_cleaner.get_datafile_path(self.consolidation_file)) as rfile:
            field_mappings = json.load(rfile)
        self.assertIsInstance(field_mappings, dict)
        self.assertListEqual(list(field_mappings.values()), [None])
        # Said dict must contain every field in the tables
        fieldset = set()
        for df_list in self.sos_cleaner.url_to_tables.values():
            for df in df_list:
                fieldset.update(set(df.columns))
        self.assertSetEqual(set(field_mappings.keys()), fieldset)

    def test_load_field_consolidation_file__mappings_not_done(self):
        """
        Asserts that the mappings per the JSON file are not applied
        if they are not complete.
        """
        with open(self.sos_cleaner.get_datafile_path(self.consolidation_file)) as rfile:
            field_mappings = json.load(rfile)
        # To ensure that the loading operation fails
        field_mappings['health-points'] = None
        # Sample mapping; this should fail
        field_mappings['S/M'] = 'Pow'
        with open(self.sos_cleaner.get_datafile_path(self.consolidation_file), mode='w') as wfile:
            json.dump(field_mappings, wfile)
        #self.assertIn(None, field_mappings.values())
        fieldset = set()
        for df_list in self.sos_cleaner.url_to_tables.values():
            for df in df_list:
                df.rename(axis=1, mapper={'HP': 'health-points'}, inplace=True)
                fieldset.update(set(df.columns))
        self.assertIn("S/M", fieldset)
        # Invocation should not change field set
        self.sos_cleaner.load_field_consolidation_file(filename=self.consolidation_file)
        new_fieldset = set()
        for df_list in self.sos_cleaner.url_to_tables.values():
            for df in df_list:
                new_fieldset.update(set(df.columns))
        # If the sets are equal, then the field-set hasn't changed
        self.assertNotIn("Pow", new_fieldset)
        self.assertSetEqual(fieldset, new_fieldset)

    def test_load_field_consolidation_file(self):
        """
        Asserts that the mappings as indicated by the JSON file are applied
        to the appropriate cells. 
        """
        with open(self.sos_cleaner.get_datafile_path(self.consolidation_file)) as rfile:
            field_mappings = json.load(rfile)
        # map stuff here
        self.sos_cleaner.load_field_consolidation_file(filename=self.consolidation_file)
        # compile field names
        # check that the old field names are erased if the new ones differ from them
        pass


if __name__ == '__main__':
    pass
