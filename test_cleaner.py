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
        Asserts that nonexistent columns are ignored,
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
        that lists table1 classes not in table2.
        """
        table1 = "characters__base_stats0"
        table2 = "characters__maximum_stats0"
        # Should create a JSON file
        self.sos_cleaner.create_class_reconciliation_file(table1, table2)
        json_path = self.sos_cleaner.get_datafile_path(f"{table1}_JOIN_{table2}.json")
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
        """
        # i.e. 'Class' column remains the same.
        pass

    def test_load_class_reconciliation_file(self):
        """
        Asserts that the mappings are done if there are
        no None values in the target-value list.
        """
        # i.e. 'Class' column is mapped to a new column per mapping.
        pass

if __name__ == '__main__':
    pass
