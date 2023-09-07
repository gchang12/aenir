#!/usr/bin/python3
"""
"""

import unittest
import logging
from datetime import datetime

import requests as r
import pandas as pd
from bs4 import BeautifulSoup

from aenir.scraper import SerenesScraper


class TestScraper(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        self.sos_scraper.home_dir.joinpath(self.sos_scraper.tables_file).unlink(missing_ok=True)

    def setUp(self):
        """
        """
        self.sos_scraper = SerenesScraper(6)
        self.sos_scraper.tables_file = "MOCK-" + self.sos_scraper.tables_file

    def test__setattr_property(self):
        """
        """
        with self.assertRaises(AttributeError):
            self.sos_scraper.game_num = None
        with self.assertRaises(AttributeError):
            self.sos_scraper.page_dict = None
        with self.assertRaises(AttributeError):
            self.sos_scraper.game_name = None
        with self.assertRaises(AttributeError):
            self.sos_scraper.home_dir = None
        with self.assertRaises(AttributeError):
            self.sos_scraper.url_to_tables = None

    def test__init__gamenum_notin_numtoname(self):
        """
        """
        with self.assertRaises(KeyError):
            nonexistent_scraper = SerenesScraper(None)
        with self.assertRaises(NameError):
            del nonexistent_scraper

    def test_scrape_tables__path_notexists(self):
        """
        """
        path = "characters/accuracy"
        with self.assertRaises(r.exceptions.HTTPError):
            no_name = self.sos_scraper.scrape_tables(path)
        self.assertNotIn(path, self.sos_scraper.url_to_tables)
        with self.assertRaises(NameError):
            del no_name

    def test_scrape_tables__path_isnotstr(self):
        """
        """
        notastr = None
        with self.assertRaises(TypeError):
            no_name = self.sos_scraper.scrape_tables(notastr)
        with self.assertRaises(NameError):
            del no_name
        self.assertDictEqual(self.sos_scraper.url_to_tables, {})

    def test_scrape_tables(self):
        """
        """
        section_page = "characters/base-stats"
        self.sos_scraper.scrape_tables(section_page)
        self.assertIn(section_page, self.sos_scraper.url_to_tables)
        self.assertIsInstance(self.sos_scraper.url_to_tables[section_page], list)
        for table in self.sos_scraper.url_to_tables[section_page]:
            self.assertIsInstance(table, pd.DataFrame)
            self.assertFalse(table.empty)
        bases_src = "https://serenesforest.net/binding-blade/characters/base-stats/"
        num_html_tables = len(
                BeautifulSoup(r.get(bases_src, timeout=1).text, 'html.parser').find_all("table")
                )
        self.assertEqual(num_html_tables, len(self.sos_scraper.url_to_tables[section_page]))

    def test_save_tables(self):
        """
        """
        section_page = "characters/growth-rates"
        self.sos_scraper.scrape_tables(section_page)
        self.sos_scraper.save_tables(section_page)
        self.assertNotIn(section_page, self.sos_scraper.url_to_tables)
        db_path = self.sos_scraper.home_dir.joinpath(self.sos_scraper.tables_file)
        self.assertTrue(db_path.exists())
        table_name_root = "characters__growth_rates"
        source_url = "/".join( [self.sos_scraper.home_url, section_page] )
        response = r.get(source_url, timeout=1)
        fetched_table = pd.read_html(response.text)[0]
        sql_table = pd.read_sql_table(table_name_root + '0', "sqlite:///" + str(db_path))
        self.assertFalse(sql_table.empty)
        self.assertTrue(all(sql_table == fetched_table))

    def test_save_tables__keynotfound(self):
        """
        """
        notpath = ""
        with self.assertRaises(KeyError):
            self.sos_scraper.save_tables(notpath)

    def test_load_tables(self):
        """
        """
        urlpath = "characters/growth-rates"
        self.sos_scraper.scrape_tables(urlpath)
        original_table = self.sos_scraper.url_to_tables[urlpath][0]
        self.sos_scraper.save_tables(urlpath)
        self.sos_scraper.load_tables(urlpath)
        self.assertIn(urlpath, self.sos_scraper.url_to_tables)
        loaded_table = self.sos_scraper.url_to_tables[urlpath][0]
        self.assertTrue(all(loaded_table == original_table))

if __name__ == '__main__':
    unittest.main()
