#!/usr/bin/python3
"""
Tests functionality of SerenesScraper methods
"""
# pylint: disable=E1111,W3101

import unittest
import logging

import requests as r
import pandas as pd
from bs4 import BeautifulSoup

from aenir import scraper

logging.basicConfig(level=logging.DEBUG)

class SerenesTestCase(unittest.TestCase):
    """
    Tests that the methods defined in scraper.SerenesScraper work.
    """
    def setUp(self):
        """
        Set up the scraper.SerenesScraper instance.
        """
        self.sos_scraper = scraper.SerenesScraper('binding-blade')
        self.sos_scraper.home_dir.joinpath("raw_stats.db").unlink(missing_ok=True)

    def test__init__gamename_isnotstr(self):
        """
        Tests that no scraper.SerenesScraper instance is created
        if the game_name is not a string.
        """
        logging.info("Asserting that __init__ fails when its argument is not a string.")
        with self.assertRaises(TypeError):
            nonexistent_scraper = scraper.SerenesScraper(None)
        with self.assertRaises(NameError):
            del nonexistent_scraper

    def test__init__gamename_notexists(self):
        """
        Tests that no scraper.SerenesScraper instance is created
        if the game name does not exist as a path on SF.net.
        """
        logging.info("Asserting that __init__ fails when its str-argument is not a game.")
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
        logging.info("Asserting that scrape_tables fails when its path does not exist.")
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
        logging.info("Asserting that scrape_tables fails when its argument is not a string.")
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
        logging.info("Asserting that scrape_tables succeeds.")
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

    def test_save_tables(self):
        """
        Asserts that the tables are saved and so forth.
        They must be identical to the tables fetched.
        """
        logging.info("Asserting that save_tables succeeds.")
        section_page = "characters/growth-rates"
        self.sos_scraper.scrape_tables(section_page)
        self.sos_scraper.save_tables(section_page)
        # key should be cleared after the save.
        self.assertNotIn(section_page, self.sos_scraper.url_to_tables)
        db_path = self.sos_scraper.home_dir.joinpath("raw_stats.db")
        self.assertTrue(db_path.exists())
        table_name_root = "characters__growth_rates"
        source_url = "/".join( [self.sos_scraper.home_url, section_page] )
        response = r.get(source_url)
        fetched_table = pd.read_html(response.text)[0]
        sql_table = pd.read_sql_table(table_name_root + '0', "sqlite:///" + str(db_path))
        self.assertFalse(sql_table.empty)
        self.assertTrue(all(sql_table == fetched_table))

    def test_save_tables__keynotfound(self):
        """
        Asserts that the operation is not carried out if
        the key is not found.
        """
        logging.info("Asserting that save_tables fails if the urlpath is not found.")
        notpath = ""
        with self.assertRaises(KeyError):
            self.sos_scraper.save_tables(notpath)

    def test_load_tables(self):
        """
        Asserts that the loaded table is no different
        from one fetched from the worldwide web.
        """
        logging.info("Asserting that load_tables succeeds.")
        table_name = "characters__growth_rates"
        urlpath = self.sos_scraper.tablename_to_urlpath(table_name)
        self.sos_scraper.scrape_tables(urlpath)
        original_table = self.sos_scraper.url_to_tables[urlpath][0]
        self.sos_scraper.save_tables(urlpath)
        self.sos_scraper.load_tables(table_name)
        self.assertIn(urlpath, self.sos_scraper.url_to_tables)
        url_source = "/".join( [self.sos_scraper.home_url, urlpath] )
        loaded_table = self.sos_scraper.url_to_tables[urlpath][0]
        self.assertTrue(all(loaded_table == original_table))

if __name__ == '__main__':
    unittest.main()
