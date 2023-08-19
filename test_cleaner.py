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
        self.cls_recon_sections = ("characters__base_stats", "classes__maximum_stats")
        self.cls_recon_file = "{}_JOIN_{}.json".format(*self.cls_recon_sections)
        for filename in (self.cls_recon_file, self.consolidation_file):
            self.get_datafile_path(filename).unlink(missing_ok=True)

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

    def test_pd_drop(self):
        """
        Asserts that the columns specified are dropped
        from the tables in one section, given as an argument.
        """
        section = "characters/base-stats"
        columns = ["Affin", "Weapon ranks"]
        for df in self.sos_cleaner.url_to_tables[section]:
            self.assertTrue(set(columns).issubset(set(df.columns)))
        self.sos_cleaner.pd_drop(columns)
        for df in self.sos_cleaner.url_to_tables[section]:
            self.assertTrue(set(columns).isdisjoint(set(df.columns)))

    def test_pd_drop__keyerror(self):
        """
        Asserts that a KeyError is raised when nonexistent columns are encountered,
        and that the tables are not affected.
        """
        section = "characters/base-stats"
        columns = [""]
        columnlist = []
        for df in self.sos_cleaner.url_to_tables[section]:
            columnlist.append(tuple(df.columns))
        with self.assertRaises(KeyError):
            self.sos_cleaner.pd_drop(columns)
        new_columnlist = []
        for df in self.sos_cleaner.url_to_tables[section]:
            new_columnlist.append(tuple(df.columns))
        self.assertListEqual(columnlist, new_columnlist)

    def test_replace_with_int_dataframes(self):
        """
        Tests that the following have been applymap'ed to a 
        list of pd.DataFrames in a given section:
        - re.sub
        - int
        """
        section = "characters/growth-rates"
        # test that everything can be cast to int in a growths-df
        self.sos_cleaner.replace_with_int_dataframes(section)
        for df in self.sos_cleaner.url_to_tables[section]:
            df = df.drop("Name", axis=1)
            self.assertTrue(all(df.dtypes == int))

    def test_create_class_reconciliation_file(self):
        """
        Tests for the creation of a blank JSON file
        that lists 'char-bases' classes not in 'maximum-stats'.
        """
        # Should create a JSON file
        self.sos_cleaner.create_class_reconciliation_file(*self.cls_recon_sections)
        json_path = self.sos_cleaner.get_datafile_path(self.cls_recon_file)
        self.assertTrue(json_path.exists())
        with open(json_path) as rfile:
            class_mappings = json.load(rfile)
        # Tests that the class_mappings dict is 'blank'
        self.assertIsInstance(class_mappings, dict)
        self.assertListEqual(list(class_mappings.values()), [None])

    def test_load_class_reconciliation_file__mappings_not_done(self):
        """
        Asserts that the mappings are not done if there is
        at least one None value in the target-value list.
        Checks that the Class column for the source remains the same.
        """
        # Partially fill out class-mappings, and save to JSON 
        cls_mappings = {} # TODO: Fill out; at least one is mapped to None.
        json_path = self.sos_cleaner.get_datafile_path(self.cls_recon_file)
        with open(json_path, mode='w') as wfile:
            json.dump(cls_mappings, wfile)
        # Extract copy of pd.DataFrame['Class']
        clscolumns = []
        for df_list in self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]]:
            for df in df_list:
                clscolumns.append(df.loc[:,"Class"])
        self.load_class_reconciliation_file(*self.cls_recon_sections)
        # Extract copy of pd.DataFrame['Class'] after loading
        new_clscolumns = []
        for df_list in self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]]:
            for df in df_list:
                new_clscolumns.append(df.loc[:,"Class"])
        self.assertEqual(len(clscolumns), len(new_clscolumns))
        for oldcls, newcls in zip(clscolumns, new_clscolumns):
            self.assertTrue(all(oldcls == newcls))

    def test_load_class_reconciliation_file(self):
        """
        Asserts that the mappings are done if there are
        no None values in the target-value list.
        The 'Class' column in 'char-bases' should be remapped.
        """
        # Fully fill out class-mappings, and save to JSON 
        cls_mappings = {} # TODO: Fill out; at least one is mapped to None.
        json_path = self.sos_cleaner.get_datafile_path(self.cls_recon_file)
        with open(json_path, mode='w') as wfile:
            json.dump(cls_mappings, wfile)
        # Extract copy of pd.DataFrame['Class']
        clscolumns = []
        for df_list in self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]]:
            for df in df_list:
                clscolumns.append(df.loc[:,"Class"])
        self.load_class_reconciliation_file(*self.cls_recon_sections)
        # Extract copy of pd.DataFrame['Class'] after loading
        new_clscolumns = []
        for df_list in self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]]:
            for df in df_list:
                new_clscolumns.append(df.loc[:,"Class"])
        self.assertEqual(len(clscolumns), len(new_clscolumns))
        for oldcls, newcls in zip(clscolumns, new_clscolumns):
            self.assertTrue(all(oldcls.map(cls_mappings) == newcls))

if __name__ == '__main__':
    unittest.main()
