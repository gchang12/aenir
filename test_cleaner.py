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

    def setUp(self, game_num=6):
        """
        Instance of SerenesCleaner must be initialized.
        All data must be compiled into a source.
        """
        self.consolidation_file = "mock_fieldconsolidation.json"
        self.datasource_file = "mock_datasource.db"
        self.sos_cleaner = SerenesCleaner(game_num)
        for page in self.sos_cleaner.page_dict:
            if not self.sos_cleaner.get_datafile_path(self.datasource_file).exists():
                self.sos_cleaner.scrape_tables(page, filename=self.datasource_file)
                self.sos_cleaner.save_tables(page, filename=self.datasource_file)
            self.sos_cleaner.load_tables(page, filename=self.datasource_file)
        self.sos_cleaner.get_datafile_path(self.consolidation_file).unlink(missing_ok=True)

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
        # Create a new mapping to simulate the create_field_consolidation_file function
        field_mappings['health-points'] = None  # This mapping to None ensures that the loading fails
        field_mappings['S/M'] = 'Pow'           # Sample mapping. This should fail.
        # Save the new mapping to file
        with open(self.sos_cleaner.get_datafile_path(self.consolidation_file), mode='w') as wfile:
            json.dump(field_mappings, wfile)
        # get old field-lists and in order
        fielddict = {}
        for page, df_list in self.sos_cleaner.url_to_tables.items():
            fielddict[page] = []
            for df in df_list:
                df.rename(axis=1, mapper={'HP': 'health-points'}, inplace=True)
                fielddict[page].append(tuple(df.columns))
        # Invocation should not change field set
        with self.assertRaises(ValueError):
            self.sos_cleaner.load_field_consolidation_file(filename=self.consolidation_file)
        # compile new field names
        new_fielddict = {}
        for page, df_list in self.sos_cleaner.url_to_tables.items():
            new_fielddict[page] = []
            for df in df_list:
                new_fielddict[page].append(tuple(df.columns))
        # The names should remain as they are
        for page in self.sos_cleaner.url_to_tables:
            old_fields = fielddict[page]
            new_fields = new_fielddict[page]
            for oldname, newname in zip(old_fields, new_fields):
                self.assertEqual(newname, oldname)

    def test_load_field_consolidation_file(self):
        """
        Asserts that the mappings as indicated by the JSON file are applied appropriately.
        """
        # map stuff here
        field_mappings = {}
        # save mappings
        with open(self.sos_cleaner.get_datafile_path(self.consolidation_file), mode='w') as wfile:
            json.dump(field_mappings, wfile)
        # get old field-lists and in order
        fielddict = {}
        for page, df_list in self.sos_cleaner.url_to_tables.items():
            fielddict[page] = []
            for df in df_list:
                fielddict[page].append(tuple(df.columns))
        # load mappings into DataFrame list
        self.sos_cleaner.load_field_consolidation_file(filename=self.consolidation_file)
        # compile new field names
        new_fielddict = {}
        for page, df_list in self.sos_cleaner.url_to_tables.items():
            new_fielddict[page] = []
            for df in df_list:
                new_fielddict[page].append(tuple(df.columns))
        # compare the field names
        for page in self.sos_cleaner.url_to_tables:
            old_fields = fielddict[page]
            new_fields = new_fielddict[page]
            for oldname, newname in zip(old_fields, new_fields):
                self.assertEqual(newname, field_mappings[oldname])

if __name__ == '__main__':
    # section1_JOIN_section2: name reconciliation
    # convert to int; apply re.sub call first (e.g. Levin!Ced)
    # remove unwanted columns
    pass
