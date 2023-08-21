#!/usr/bin/python3
"""
Tests data-cleaning capabilities of SerenesCleaner.
"""

import logging
import unittest
import json
import pandas as pd

from aenir.cleaner import SerenesCleaner

logging.basicConfig(filename="log_test-cleaner.log", level=logging.DEBUG)

class TestCleaner(unittest.TestCase):
    """
    Defines tests for SerenesCleaner.
    """

    def setUp(self, game_num=6):
        """
        Instance of SerenesCleaner must be initialized.
        All data must be compiled into a source.
        """
        self.cls_recon_sections = ("characters__base_stats", "classes__maximum_stats")
        self.cls_recon_file = "{}-JOIN-{}.json".format(*self.cls_recon_sections)
        self.consolidation_file = "mock_fieldconsolidation.json"
        self.datasource_file = "mock_datasource.db"
        self.clsmatch_file = "mock_clsmatch.db"
        self.gender_file = "mock_genders.json"
        self.sos_cleaner = SerenesCleaner(game_num)
        for page in self.sos_cleaner.page_dict:
            if not self.sos_cleaner.get_datafile_path(self.datasource_file).exists():
                self.sos_cleaner.scrape_tables(page, filename=self.datasource_file)
                self.sos_cleaner.save_tables(page, filename=self.datasource_file)
            self.sos_cleaner.load_tables(page, filename=self.datasource_file)
        self.sos_cleaner.get_datafile_path(self.consolidation_file).unlink(missing_ok=True)
        for filename in (self.cls_recon_file, self.consolidation_file, self.gender_file, self.clsmatch_file):
            self.get_datafile_path(filename).unlink(missing_ok=True)
        self.cls_mappings = {
                'Archer': 'Non-promoted',
                'Bandit': 'Non-promoted',
                'Bard': 'Non-promoted',
                'Bishop': 'Bishop',
                'Cavalier': 'Non-promoted',
                'Dancer': 'Non-promoted',
                'Druid': 'Druid',
                'Fighter': 'Non-promoted',
                'General': 'General',
                'Hero': 'Hero',
                'Knight': 'Non-promoted',
                'Lord': 'Non-promoted',
                'Mage': 'Non-promoted',
                'Mamkute': 'Non-promoted',
                'Mercenary': 'Non-promoted',
                'Myrmidon': 'Non-promoted',
                'Nomad': 'Non-promoted',
                'Nomadic Trooper': ,
                'Paladin': 'Paladin',
                'Pegasus Knight': 'Non-promoted',
                'Pirate': 'Non-promoted',
                'Priest': 'Non-promoted',
                'Sage': 'Sage',
                'Shaman': 'Non-promoted',
                'Sniper': 'Sniper',
                'Swordmaster': 'Swordmaster',
                'Thief': 'Non-promoted',
                'Troubadour': 'Non-promoted',
                'Wyvern Lord': 'Wyvern Lord',
                'Wyvern Rider': 'Non-promoted',
                }

    def test_create_field_consolidation_file(self):
        """
        Asserts that a blank JSON file for mapping field names to
        a common standard is created.
        """
        self.sos_cleaner.create_field_consolidation_file(filename=self.consolidation_file)
        # File should exist after the function call
        cfile_path = self.sos_cleaner.get_datafile_path(self.consolidation_file)
        self.assertTrue(cfile_path.exists())
        with open(self.sos_cleaner.get_datafile_path(self.consolidation_file)) as rfile:
            field_mappings = json.load(rfile)
        # JSON file must contain dict object
        self.assertIsInstance(field_mappings, dict)
        # The aforementioned dict must map all unique field names to None
        self.assertListEqual(list(field_mappings.values()), [None])
        fieldset = set()
        for df_list in self.sos_cleaner.url_to_tables.values():
            for df in df_list:
                fieldset.update(set(df.columns))
        # Said dict must contain every field in the tables
        self.assertSetEqual(set(field_mappings.keys()), fieldset)
        # The dict cannot contain duplicate keys
        self.assertEqual(len(field_mappings), len(fieldset))

    def test_load_field_consolidation_file__missing_keys(self):
        """
        Asserts that the DataFrame objects remain as they are if
        there are keys in the DataFrame not present in the file.
        """
        # Save blank file with incomplete set of mappings
        field_mappings = {} # Blank by construction
        with open(self.sos_cleaner.get_datafile_path(self.consolidation_file), mode='w') as wfile:
            json.dump(field_mappings, wfile)
        # get old field-lists and in order
        fielddict = {}
        for page, df_list in self.sos_cleaner.url_to_tables.items():
            fielddict[page] = []
            for df in df_list:
                df.rename(axis=1, mapper={'HP': 'health-points'}, inplace=True)
                fielddict[page].append(tuple(df.columns))
        # ValueError: dict has an incomplete mapping
        with self.assertRaises(ValueError):
            self.sos_cleaner.load_field_consolidation_file(filename=self.consolidation_file)
        # compile new field names
        new_fielddict = {}
        for page, df_list in self.sos_cleaner.url_to_tables.items():
            new_fielddict[page] = []
            for df in df_list:
                new_fielddict[page].append(tuple(df.columns))
        # The names should remain as they are
        self.assertDictEqual(new_fielddict, fielddict)

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
                fielddict[page].append(tuple(df.columns))
                df.rename(axis=1, mapper={'HP': 'health-points'}, inplace=True)
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
        self.assertDictEqual(new_fielddict, fielddict)

    def test_load_field_consolidation_file(self):
        """
        Asserts that the mappings as indicated by the JSON file are applied appropriately.
        """
        field_mappings = {
                'Affin': 'Affinity (DROP)',
                'Class': 'Class',
                'Con': 'Con',
                'Def': 'Def',
                'HP': 'HP',
                'Lck': 'Lck',
                'Lv': 'Lv',
                'Mov': 'Mov',
                'Name': 'Character',
                'Promotion': 'Promotion',
                'Res': 'Res',
                'S/M': 'S/M',
                'Skl': 'Skl',
                'Spd': 'Spd',
                'Weapon ranks': 'Weapon Ranks (DROP)',
                }
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
        self.assertNotEqual(fielddict, new_fielddict)
        # assert that the old names are mapped to the new
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
        # pre-drop: columns in all tables contain 'columns' contents
        contains_columns = False
        for df in self.sos_cleaner.url_to_tables[section]:
            if not set(columns).issubset(set(df.columns)):
                continue
            contains_columns = True
        self.assertTrue(contains_columns)
        # main operation
        self.sos_cleaner.pd_drop(columns)
        # post-drop: no columns should intersect with 'columns'
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
        # compile column list
        for df in self.sos_cleaner.url_to_tables[section]:
            columnlist.append(tuple(df.columns))
        # do operation here; it should fail
        with self.assertRaises(KeyError):
            self.sos_cleaner.pd_drop(columns)
        # compile new column list
        new_columnlist = []
        for df in self.sos_cleaner.url_to_tables[section]:
            new_columnlist.append(tuple(df.columns))
        # make sure the two column lists are equal
        self.assertListEqual(columnlist, new_columnlist)

    def test_replace_with_int_dataframes__column_dne(self):
        """
        Tests that the following have been applymap'ed to a 
        list of pd.DataFrames in a given section:
        - re.sub
        - int
        - DataFrame.convert_dtypes
        Tests that the function fails when nonexistent columns
        are passed as arguments to pd.DataFrame.drop
        """
        # test that everything can be cast to int in a growths-df
        section = "characters/growth-rates"
        columns = [""]
        # compile old columns to compare
        old_columns = []
        for df in self.sos_cleaner.url_to_tables[section]:
            old_columns.append(tuple(df.columns))
        # call should fail
        with self.assertRaises(KeyError):
            self.sos_cleaner.replace_with_int_dataframes(section, columns)
        # compile new columns to compare against old
        new_columns = []
        for df in self.sos_cleaner.url_to_tables[section]:
            new_columns.append(tuple(df.columns))
            df = df.drop("Name", axis=1)
            # Assume nothing is in its most efficient datatype
            self.assertFalse(all(df.dtypes == int))
            self.assertFalse(all(df.convert_dtypes().dtypes == df.dtypes))
        # make sure old == new
        self.assertListEqual(new_columns, old_columns)

    def test_replace_with_int_dataframes(self):
        """
        Tests that the following have been applymap'ed to a 
        list of pd.DataFrames in a given section:
        - re.sub
        - int
        """
        section = "characters/growth-rates"
        columns = ["Name"]
        # compile old columns to compare
        old_columns = []
        for df in self.sos_cleaner.url_to_tables[section]:
            old_columns.append(tuple(df.columns))
        # main operation should succeed with no errors
        self.sos_cleaner.replace_with_int_dataframes(section, columns)
        new_columns = []
        # compile new columns to compare against old
        for df in self.sos_cleaner.url_to_tables[section]:
            new_columns.append(tuple(df.columns))
            df = df.drop(columns, axis=1)
            # all columns should be in the most efficient dtype
            self.assertTrue(all(df.dtypes == int))
            self.assertTrue(all(df.convert_dtypes().dtypes == df.dtypes))
        # operation may involve taking out columns, and putting them back in
        # this test asserts that they are put back in in the right order
        self.assertListEqual(new_columns, old_columns)

    def test_create_class_reconciliation_file(self):
        """
        Tests for the creation of a blank JSON file
        that lists 'char-bases' classes not in 'maximum-stats'.
        """
        # main operation
        self.sos_cleaner.create_class_reconciliation_file(*self.cls_recon_sections)
        # a JSON file should be created
        json_path = self.sos_cleaner.get_datafile_path(self.cls_recon_file)
        self.assertTrue(json_path.exists())
        # load dict from JSON
        with open(json_path) as rfile:
            class_mappings = json.load(rfile)
        # Tests that the JSON object is a dict
        self.assertIsInstance(class_mappings, dict)
        # Assert that only the to-be-reconciled names are in the keys of the mapping
        basestats_classes = set(
                self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]][0].loc[:, "Class"]
                )
        maxstats_classes = set(
                self.sos_cleaner.url_to_tables[self.cls_recon_sections[1]][0].loc[:, "Class"]
                )
        # The goal of this function is to identify non-matching classes
        unmatched_classes = basestats_classes.difference(maxstats_classes)
        self.assertSetEqual(unmatched_classes, set(class_mappings.keys()))
        self.assertTrue(self.get_datafile_path(self.clsmatch_file).exists())

    def test_load_class_reconciliation_file__mappings_not_done(self):
        """
        Asserts that the mappings are not done if there is
        at least one None value in the target-value list.
        Checks that the Class column for the source remains the same.
        """
        # must fail if at least one mapping is None
        cls_mappings = {'Lord': None}
        # dump complete class mapping into JSON
        json_path = self.sos_cleaner.get_datafile_path(self.cls_recon_file)
        with open(json_path, mode='w') as wfile:
            json.dump(cls_mappings, wfile)
        # compile copies of pd.DataFrame['Class']
        clscolumns = []
        for df_list in self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]]:
            for df in df_list:
                clscolumns.append(df.loc[:, "Class"])
        # ValueError: recon not done
        with self.assertRaises(ValueError):
            self.load_class_reconciliation_file(*self.cls_recon_sections)
        # compile copies of pd.DataFrame['Class'] post-call
        new_clscolumns = []
        for df_list in self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]]:
            for df in df_list:
                new_clscolumns.append(df.loc[:, "Class"])
        # classes should be the same
        self.assertListEqual(clscolumns, new_clscolumns)

    def test_load_class_reconciliation_file(self):
        """
        Asserts that the mappings are done if there are
        no None values in the target-value list.
        The 'Class' column in 'char-bases' should be remapped.
        """
        # extract deep-copies of pd.DataFrame['Class']
        clscolumns = []
        for df_list in self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]]:
            for df in df_list:
                clscolumns.append(df.loc[:, "Class"])
        # dump complete class mappings for reconciliation
        json_path = self.sos_cleaner.get_datafile_path(self.cls_recon_file)
        with open(json_path, mode='w') as wfile:
            json.dump(self.cls_mappings, wfile)
        # create gender file for reconciliation
        self.sos_cleaner.create_gender_file(self.gender_file)
        # main operation
        self.load_class_reconciliation_file(*self.cls_recon_sections)
        # extract deep-copies of pd.DataFrame['Class'] post-load
        new_clscolumns = []
        for df_list in self.sos_cleaner.url_to_tables[self.cls_recon_sections[0]]:
            for df in df_list:
                new_clscolumns.append(df.loc[:, "Class"])
        # check that the columns have changed
        self.assertNotEqual(clscolumns, new_clscolumns)

    def test_validate_classes(self):
        """
        Asserts that True is returned when all classes match.
        """
        # dump complete class mappings to JSON
        json_path = self.sos_cleaner.get_datafile_path(self.cls_recon_file)
        with open(json_path, mode='w') as wfile:
            json.dump(self.cls_mappings, wfile)
        # create gender file for reconciliation
        self.sos_cleaner.create_gender_file(self.gender_file)
        # load reconciliations: assume successful
        self.load_class_reconciliation_file(*self.cls_recon_sections)
        # main operation
        true = self.validate_classes(*self.cls_recon_sections, self.clsmatch_file)
        self.assertTrue(true)
        char_bases_classes = self.sos_cleaner
            .url_to_tables[self.cls_recon_sections[0]][0].loc[:, 'Class']
        cls_maxes_classes = self.sos_cleaner
            .url_to_tables[self.cls_recon_sections[1]][0].loc[:, 'Class']
        # check that the matches are complete
        match_table = pd.read_sql(
                self.cls_recon_file,
                str(self.get_datafile_path(self.clsmatch_file))
                )
        self.assertTrue(
                match_table.join(char_bases_classes, on="Class")
                .loc[:, self.cls_recon_sections[1]].isnull().empty
                )

    def test_validate_classes__unmatched_classes_exist(self):
        """
        Asserts that if there are unmapped classes, a pd.DataFrame
        containing those classes is returned.
        """
        # validate without doing any operations
        unmatched_classes = self.validate_class_match(*self.cls_recon_sections, self.clsmatch_file)
        unmatched_classes = unmatched_classes[
                unmatched_classes.loc[:, self.cls_recon_sections[1]].notnull()
                ]
        # check matches manually
        char_bases_classes = self.sos_cleaner
            .url_to_tables[self.cls_recon_sections[0]][0].loc[:, 'Class']
        cls_maxes_classes = self.sos_cleaner
            .url_to_tables[self.cls_recon_sections[1]][0].loc[:, 'Class']
        # check that the matches are incomplete
        match_table = pd.read_sql(
                self.cls_recon_file,
                str(self.get_datafile_path(self.clsmatch_file))
                )
        match_table = match_table[match_table.loc[:, self.cls_recon_sections[1]].notnull()]
        self.assertTrue(all(unmatched_classes, match_table))

    def test_create_gender_file(self):
        """
        Tests that a JSON file with the character names is created.
        """
        # Note: Gender file is to be loaded while mapping foreign keys
        self.sos_cleaner.create_gender_file(self.gender_file)
        gender_file = self.sos_cleaner.get_datafile_path(self.gender_file)
        self.assertTrue(gender_file.exists())
        with open(gender_file) as rfile:
            gender_dict = json.load(rfile)
        character_set = set(
                self.sos_cleaner.url_to_tables["characters/base-stats"][0].loc[:, "Name"]
                )
        self.assertSetEqual(character_set, set(gender_dict.keys()))
        self.assertSetEqual(set(gender_dict.values()), {None})

if __name__ == '__main__':
    unittest.main()
