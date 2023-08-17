#!/usr/bin/python3
"""
Tests functionality of SerenesScraper methods
"""
# pylint: disable=E1111

import unittest
from pathlib import Path

import requests as r
import pandas as pd
from bs4 import BeautifulSoup

import scraper

class SerenesTestCase(unittest.TestCase):
    """
    Tests that the methods defined in scraper.SerenesScraper work.
    """

    def setUp(self):
        """
        Set up the scraper.SerenesScraper instance.
        """
        self.sos_scraper = scraper.SerenesScraper('binding-blade')

    def test__init__gamename_isnotstr(self):
        """
        Tests that no scraper.SerenesScraper instance is created
        if the game_name is not a string.
        """
        with self.assertRaises(TypeError):
            nonexistent_scraper = scraper.SerenesScraper(None)
        with self.assertRaises(NameError):
            del nonexistent_scraper

    def test__init__gamename_notexists(self):
        """
        Tests that no scraper.SerenesScraper instance is created
        if the game name does not exist as a path on SF.net.
        """
        bad_name = 'yabba-dabba-doo'
        with self.assertRaises(r.exceptions.HTTPError):
            nonexistent_scraper = scraper.SerenesScraper(bad_name)
        with self.assertRaises(NameError):
            del nonexistent_scraper

    def test_scrape_tables__path_notexists(self):
        """
        Asserts that an error is raised if the path does not exist.
        No tables are appended to the 'url_to_tables'.
        """
        path = "characters/accuracy"
        with self.assertRaises(r.exceptions.HTTPError):
            no_name = self.sos_scraper.scrape_tables(path)
        self.assertNotIn(path, self.sos_scraper.url_to_tables)
        with self.assertRaises(NameError):
            del no_name

    def test_scrape_tables__path_isnotstr(self):
        """
        Asserts that an error is raised if the path is not a str.
        No tables are appended to the 'url_to_tables'.
        """
        notastr = None
        with self.assertRaises(TypeError):
            no_name = self.sos_scraper.scrape_tables(notastr)
        with self.assertRaises(NameError):
            del no_name
        self.assertDictEqual(self.sos_scraper.url_to_tables, {})

    def test_scrape_tables__path_exists(self):
        """
        Asserts that the 'url_to_tables' object is appended
        with a list of pd.DataFrame objects.
        """
        section_page = "characters/base-stats"
        self.sos_scraper.scrape_tables(section_page)
        self.assertIn(section_page, self.sos_scraper.url_to_tables)
        self.assertIsInstance(self.sos_scraper.url_to_tables[section_page], list)
        for table in self.sos_scraper.url_to_tables[section_page]:
            self.assertIsInstance(table, pd.DataFrame)
            self.assertFalse(table.empty)
        bases_src = "https://serenesforest.net/binding-blade/characters/base-stats/"
        num_html_tables = len(BeautifulSoup(r.get(bases_src).text, 'html.parser').find_all("table"))
        self.assertEqual(num_html_tables, len(self.sos_scraper.url_to_tables[section_page]))

    def test_save_table(self):
        """
        Asserts that the tables are saved and so forth.
        They must be identical to the tables fetched.
        """
        section_page = "characters/growth-rates"
        self.sos_scraper.save_table(section_page)
        # key should be cleared after the save.
        self.assertNotIn(section_page, self.sos_scraper.url_to_tables)
        db_path = Path("data", "binding-blade", "raw_stats.db")
        self.assertTrue(db_path.exists())
        table_name_root = "characters_growthrates"
        source_url = urllib.parse.urljoin(self.sos_scraper.URL_ROOT, "characters/growth-rates")
        response = r.get(table_url)
        fetched_table = pd.read_html(response.text)
        sql_table = pd.read_sql_table(table_name_root + '0', "//" + db_path)
        self.assertFalse(sql_table.empty)
        self.assertEqual(sql_table, fetched_table)

    def test_load_table(self):
        """
        Asserts that the loaded table is no different
        from one fetched from the worldwide web.
        """
        table_name_root = "characters_growthrates"
        loaded_table = self.sos_scraper.load_table(table_name_root)
        urlpath = self.sos_scraper.TABLE_TO_URLPATH[table_name_root]
        self.assertIn(urlpath, self.sos_scraper.url_to_tables)
        db_path = Path("data", "binding-blade", "raw_stats.db")
        url_source = urllib.parse.urljoin(self.sos_scraper.URL_ROOT, urlpath)
        www_table = pd.read_html(r.get(url_source).text)
        self.assertEqual(self.sos_scraper.url_to_tables[urlpath], sql_table)

if __name__ == '__main__':
    unittest.main()
