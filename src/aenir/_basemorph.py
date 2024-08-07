#!/usr/bin/python3
"""
Defines the BaseMorph class.

BaseMorph: Defines methods for verifying manual input, and matching it to the proper sources.
"""

# TODO: Create docstrings. Organize documentation better.

import logging
import io
from typing import Tuple, List
import json
from pathlib import Path

import pandas as pd
#from aenir.cleaner import SerenesCleaner

class ProtoMorph:
    """
    Defines parameters and methods for stat look-up and name verification.

    current_clstype: Determines which table to match from.
    current_cls: Value of the current class, to be matched.
    target_stats: Stores the stats to be retrieved.
    history: Stores the history of a unit as a list of (Class, Lv) tuples.
    STAT_ORDERING: Stores the order of stat labels.
    """

    DATADIR_ROOT = "data"
    STAT_ORDERING = {
        4: ["HP", "Str", "Mag", "Skl", "Spd", "Lck", "Def", "Res"],
        5: ["HP", "Str", "Mag", "Skl", "Spd", "Lck", "Def", "Con", "Mov"],
        6: ["HP", "Pow", "Skl", "Spd", "Lck", "Def", "Res"],
        7: ["HP", "Pow", "Skl", "Spd", "Lck", "Def", "Res"],
        8: ["HP", "Pow", "Skl", "Spd", "Lck", "Def", "Res"],
        9: ["HP", "Str", "Mag", "Skl", "Spd", "Lck", "Def", "Res"],
    }

    NUM_TO_NAME = {
        4: "genealogy-of-the-holy-war",
        5: "thracia-776",
        6: "binding-blade",
        7: "blazing-sword",
        8: "the-sacred-stones",
        9: "path-of-radiance",
    }

    NUM_TO_FULLNAME = {
        4: "Genealogy of the Holy War",
        5: "Thracia 776",
        6: "Sword of Seals",
        7: "Blazing Sword",
        8: "The Sacred Stones",
        9: "Path of Radiance",
    }

    page_dict = {
        "characters/base-stats": "characters__base_stats",
        "characters/growth-rates": "characters__growth_rates",
        "classes/maximum-stats": "classes__maximum_stats",
        "classes/promotion-gains": "classes__promotion_gains",
    }

    tables_file = "cleaned_stats.db"

    @property
    def game_num(self):
        return self._game_num

    @property
    def game_name(self):
        return self._game_name

    @property
    def history(self):
        return self._history

    @property
    def comparison_labels(self):
        return self._comparison_labels

    @property
    def home_dir(self):
        return self._home_dir

    def __init__(self, game_num: int):
        """
        Defines:
        current_clstype - For use in cross-referencing names in tables.
        current_cls - Stores current class
        target_stats - Temporary store for stat-augmenting arrays
        """

        """ SerenesCleaner
        self.fieldrecon_file = "fieldrecon.json" # not needed
        self.clsrecon_list = [
            (("characters/base-stats", "Name", "Name"), ("characters/growth-rates", "Name")),
            (("characters/base-stats", "Name", "Class"), ("classes/maximum-stats", "Class")),
            (("characters/base-stats", "Name", "Class"), ("classes/promotion-gains", "Class")),
            (("classes/promotion-gains", "Promotion", "Promotion"), ("classes/maximum-stats", "Class")),
            (("classes/promotion-gains", "Promotion", "Promotion"), ("classes/promotion-gains", "Class")),
        ] # not needed
        """

        """ SerenesTranscriber
        # To be edited never
        self.tables_file = "cleaned_stats.db"
        """

        # To be edited only by program
        self.url_to_tables = {}
        """ SerenesScraper
        _URL_ROOT = "https://serenesforest.net" # not needed
        self.URL_ROOT = "https://serenesforest.net" # not needed
        """

        """ SerenesBase
        self._NUM_TO_NAME = { # not needed
        self.NUM_TO_NAME = {
            4: "genealogy-of-the-holy-war",
            5: "thracia-776",
            6: "binding-blade",
            7: "blazing-sword",
            8: "the-sacred-stones",
            9: "path-of-radiance",
        } # not needed
        """
        # To be edited never
        self._game_num = game_num
        # To be edited never
        self._game_name = self.NUM_TO_NAME[game_num]
        # essential to set_targetstats method
        # TODO: To be edited only by program. Is set by `set_targetstats` method.
        #       How to restrict permissions on this field so that it can only be modified by `set_targetstats`?
        #       Perhaps a pd-Series equivalent of list.append?
        self.target_stats = None
        # Can be edited by user.
        self.current_stats = None
        # To be edited only by program
        # history (class, lv) tuples, and labels for comparison DataFrame
        self._history = []
        # To be edited only by program
        self._comparison_labels = {}
        # load tables
        # To be edited never
        self._home_dir = Path(self.DATADIR_ROOT).joinpath(self.game_name)
        # To be edited by user. Turned into class attribute.
        #self.tables_file = "cleaned_stats.db"

    def load_tables(self, urlpath: str):
        """
        Loads the table-list into url_to_tables[urlpath] from home_dir/tables_file.

        Raises:
        - FileNotFoundError: tables_file does not exist.
        - KeyError: urlpath is not registered in page_dict.
        """
        logging.info("SerenesTranscriber.load_tables(self, '%s')", urlpath)
        load_path = self.home_dir.joinpath(self.tables_file)
        if not load_path.exists():
            raise FileNotFoundError(f"'{str(load_path)}' does not exist. Aborting.")
        load_file = str(load_path)
        tablename_root = self.page_dict[urlpath]
        logging.info("SerenesTranscriber.url_to_tables['%s'] = []", urlpath)
        self.url_to_tables[urlpath] = []
        tableindex = 0
        logging.info("Loading tables into SerenesTranscriber.url_to_tables['%s'].", urlpath)
        while True:
            table_name = tablename_root + str(tableindex)
            con = "sqlite:///" + load_file
            try:
                logging.info("pd.read_sql_table('%s', '%s')", table_name, con)
                table = pd.read_sql_table(table_name, con)
                tableindex += 1
                logging.info("SerenesTranscriber.url_to_tables['%s'].append(tables[%d])", urlpath, tableindex-1)
                self.url_to_tables[urlpath].append(table)
            except ValueError:
                logging.info("%d table(s) have been loaded into SerenesTranscriber.url_to_tables['%s']", tableindex, urlpath)
                break


class BaseMorph(ProtoMorph):
    """
    """

    url_to_tables = {}

    def __init__(self, game_num: int):
        ProtoMorph.__init__(self, game_num)
        # initialize instance attribute `url_to_tables`
        del self.url_to_tables
        # delete instance attribute `url_to_tables`, and allow class attribute `url_to_tables` to occupy namespace
        #if not self.url_to_tables:
        for urlpath in self.page_dict:
            # TODO: Find out why this generates an error
            #if urlpath in self.url_to_tables: continue
            """
                FAILED tests/integration/test_morph__integration.py::Morph6IntegrationTest::test_fe8_units - KeyError: 'Non-promoted (foot)'
                FAILED tests/integration/test_morph__integration.py::Morph6IntegrationTest::test_fe9_units - KeyError: 'Non-promoted physical'
                FAILED tests/integration/test_morph__integration.py::Morph6IntegrationTest::test_villager_amelia - KeyError: 'Non-promoted (foot)'
                FAILED tests/integration/test_morph__integration.py::Morph6IntegrationTest::test_villager_ewan - KeyError: 'Non-promoted (foot)'
                FAILED tests/integration/test_morph__integration.py::Morph6IntegrationTest::test_villager_ross - KeyError: 'Non-promoted (foot)'
                FAILED tests/integration/test_morph__integration.py::Morph7IntegrationTest::test_all_units - KeyError: 'Wallace'
                FAILED tests/integration/test_morph__integration.py::Morph7IntegrationTest::test_main_wallace - KeyError: 'Wallace'
                FAILED tests/integration/test_morph__integration.py::Morph7IntegrationTest::test_tutorial_wallace - KeyError: 'Wallace'
                FAILED tests/integration/test_morph__integration.py::Morph9IntegrationTest::test_all_units - KeyError: 'Non-promoted physical'
                FAILED tests/unit/test__basemorph.py::BaseMorphTest::test_get_character_list - AssertionError: False is not true
                FAILED tests/unit/test__basemorph.py::BaseMorphTest::test_set_targetstats - KeyError: 'Fir'
                FAILED tests/unit/test_morph.py::Morph6Test::test_level_up - KeyError: 'Roy'
                FAILED tests/unit/test_morph.py::Morph7Test::test__lt__ - KeyError: 'Wallace'
                FAILED tests/unit/test_morph.py::Morph7Test::test__lt__HM - KeyError: 'Wallace'
                FAILED tests/unit/test_morph.py::Morph7Test::test__repr__ - KeyError: 'Wallace'
                FAILED tests/unit/test_morph.py::Morph7Test::test_get_repr_series__comparison_labels - KeyError: 'Wallace'
            """
            self.load_tables(urlpath)

    def verify_clsrecon_file(self, ltable_args: Tuple[str, str, str], rtable_args: Tuple[str, str]):
        """
        Prints: clsrecon_dict.keys not in ltable[lindex_col], clsrecon_dict.values not in rtable[to_col].

        Note: In order for this method to work, logging.level must be set to logging.INFO.
        Find cls-recon list in unittest.TestCase subclass for BaseMorph.
        """
        logging.info("BaseMorph.verify_clsrecon_file(self, %s, %s)", ltable_args, rtable_args)
        # unpack arguments
        ltable_url, lindex_col, from_col = ltable_args
        rtable_url, to_col = rtable_args
        # load clsrecon_dict
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with io.open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        # compile ltable pkey names
        ltable_nameset = set()
        for table in self.url_to_tables[ltable_url]:
            ltable_nameset.update(set(table.loc[:, lindex_col]))
        # compile rtable values
        rtable_nameset = set()
        for table in self.url_to_tables[rtable_url]:
            rtable_nameset.update(set(table.loc[:, to_col]))
        # check1: clsrecon_dict.keys subset of ltable_nameset
        check1 = set(clsrecon_dict) - ltable_nameset
        logging.info("%d key(s) in '%s', but not in '%s.%s': %s", len(check1), str(json_path), ltable_name, lindex_col, check1)
        # check2: clsrecon_dict.values subset of rtable_nameset
        check2 = set(clsrecon_dict.values()) - {None} - rtable_nameset
        logging.info("%d value(s) in '%s', but not in '%s.%s': %s", len(check2), str(json_path), rtable_name, to_col, check2)

    def verify_maximum_stats(self):
        """
        Prints columns that are in 'classes/maximum-stats' but not in 'characters/base-stats'.

        Note: In order for this method to work, logging.level must be set to logging.INFO.
        """
        logging.info("BaseMorph.verify_maximum_stats(self)")
        bases_name = "characters/base-stats"
        maxes_name = "classes/maximum-stats"
        bases = set(self.url_to_tables[bases_name][0].columns) - {"Name", "Class", "Lv"}
        maxes = set(self.url_to_tables[maxes_name][0].columns) - {"Class"}
        diff = maxes - bases
        logging.info("%d names in '%s' but not in '%s': %s", len(diff), maxes_name, bases_name, diff)

    def set_targetstats(self, ltable_args: Tuple[str, str], rtable_args: Tuple[str, str], tableindex: int):
        """
        Sets BaseMorph.target_stats to the pd.[DataFrame|Series] per clsrecon_dict.

        ltable_url, lindex_col = ltable_args
        rtable_url, to_col = rtable_args
        lindex_col |-(clsrecon_dict)-> from_col === to_col
        """
        logging.info("BaseMorph.set_targetstats(self, %s, %s)", ltable_args, rtable_args)
        # unpack arguments
        ltable_url, lindex_val = ltable_args
        rtable_url, to_col = rtable_args
        # load clsrecon_dict from json
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        from_col = clsrecon_dict[lindex_val]
        if from_col is None:
            self.target_stats = None
        else:
            self.target_stats = self.url_to_tables[rtable_url][tableindex].set_index(to_col).loc[from_col, :]

    def get_lynmode_options(self) -> List[str]:
        """
        Returns a List[str] of possible pseudo-booleans for a member of the Lyndis League.
        """
        lyn_options = [False, True]
        return [str(option) for option in lyn_options]

    def get_hardmode_options(self) -> List[str]:
        """
        Returns a List[str] of possible pseudo-booleans for a character with Hard Mode bonuses.
        """
        hm_options = [False, True]
        return [str(option) for option in hm_options]

    def get_character_list(self) -> List[str]:
        """
        Returns a List[str] of base!character names mapped to growths!character names.

        Raises:
        - FileNotFoundError: not home_dir.joinpath("characters__base_stats-JOIN-characters__growth_rates.json").exists()
        - json.decoder.JSONDecodeError: File is not in JSON form.
        """
        logging.info("BaseMorph.get_character_list(self)")
        ltable_url = "characters/base-stats"
        rtable_url = "characters/growth-rates"
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        # query character list from JSON (FileNotFoundError may be raised before that)
        with io.open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        chrlist = []
        # filter to include non-None entries
        for chrname, growth_equivalent in clsrecon_dict.items():
            if growth_equivalent is None:
                continue
            chrlist.append(chrname)
        # return keys mapped to non-None
        logging.info("%d names found: %s", len(chrlist), chrlist)
        return chrlist

    def get_fe4_unit_list(self, unit_type: str) -> List[str]:
        """
        Shortcut function to get a list of either FE4 kids or fathers.
        """
        assert self.game_num == 4
        tgt_colname = {
            "kid": "Name",
            "father": "Father",
        }[unit_type]
        tablename = "characters/growth-rates"
        src_tablelist = self.url_to_tables[tablename]
        src_table = src_tablelist[1]
        src_column = src_table[tgt_colname].copy()
        src_column.drop_duplicates(inplace=True)
        unit_list = src_column.to_list()
        return unit_list

