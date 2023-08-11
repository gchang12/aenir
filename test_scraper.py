#!/usr/bin/python3
"""
Tests functionality of SerenesScraper methods
"""
# pylint: disable=E1111

import logging
import unittest

import requests as r
import pandas as pd

import scraper

class SerenesTestCase(unittest.TestCase):
    """
    Tests that the methods defined in scraper.SerenesScraper work.
    """

    def setUp(self):
        """
        Set up the scraper.SerenesScraper instance.
        """
        game_name = 'binding-blade'
        logging.info("self.sos_scraper = scraper.SerenesScraper('%s');", game_name)
        self.sos_scraper = scraper.SerenesScraper(game_name)

    def test__init__gamename_isnotstr(self):
        """
        Tests that no scraper.SerenesScraper instance is created
        if the game_name is not a string.
        """
        logging.info("nonexistent_scraper = scraper.SerenesScraper(None);")
        with self.assertRaises(TypeError):
            nonexistent_scraper = scraper.SerenesScraper(None)
        logging.info("TypeError has been successfully raised;")
        with self.assertRaises(NameError):
            del nonexistent_scraper
        logging.info("NameError has been successfully raised; 'nonexistent_scraper' not defined;")

    def test__init__gamename_notexists(self):
        """
        Tests that no scraper.SerenesScraper instance is created
        if the game name does not exist as a path on SF.net.
        """
        bad_name = 'yabba-dabba-doo'
        logging.info("nonexistent_scraper = scraper.SerenesScraper('%s');", bad_name)
        with self.assertRaises(r.exceptions.HTTPError):
            nonexistent_scraper = scraper.SerenesScraper(bad_name)
        logging.info("requests.exceptions.HTTPError successfully raised; '%s' is not a path on SF.net;", bad_name)
        with self.assertRaises(NameError):
            del nonexistent_scraper
        logging.info("NameError successfully raised; 'nonexistent_scraper' not defined;")

    def test_scrape_tables__path_notexists(self):
        """
        Asserts that an error is raised if the path does not exist.
        No tables are appended to the 'table_dict'.
        """
        section_page = ("characters", "accuracy")
        logging.info("no_name = scraper.SerenesScraper.scrape_tables('%s', '%s');", section_page[0], section_page[1])
        with self.assertRaises(r.exceptions.HTTPError):
            no_name = self.sos_scraper.scrape_tables(*section_page)
        logging.info("requests.exceptions.HTTPError successfully raised; '%s' is not a valid path;", section_page)
        url_key = '_'.join(section_page)
        self.assertNotIn(url_key, self.sos_scraper.table_dict)
        logging.info("'%s' not in self.sos_scraper.table_dict;", url_key)
        with self.assertRaises(NameError):
            del no_name
        logging.info("NameError successfully raised; 'no_name' is not defined;")

    def test_scrape_tables__path_isnotstr(self):
        """
        Asserts that an error is raised if the path is not a str.
        No tables are appended to the 'table_dict'.
        """
        section_page = ["characters", "accuracy"]
        for index in range(len(section_page)):
            argcopy = section_page.copy()
            argcopy[index] = None
            logging.info("arg%d is None;", index)
            logging.info("no_name = self.sos_scraper.scrape_tables(*%s);", argcopy)
            with self.assertRaises(TypeError):
                no_name = self.sos_scraper.scrape_tables(*argcopy)
            logging.info("TypeError successfully raised;")
            with self.assertRaises(NameError):
                del no_name
            logging.info("NameError successfully raised; 'no_name' is not defined;")
        self.assertDictEqual(self.sos_scraper.table_dict, {})
        logging.info("self.sos_scraper.table_dict == {};")

    def test_scrape_tables__path_exists(self):
        """
        Asserts that the 'table_dict' object is appended
        with a list of pd.DataFrame objects.
        """
        section_page = ("characters", "base-stats")
        logging.info("self.scrape_tables('%s', '%s');", section_page[0], section_page[1])
        self.sos_scraper.scrape_tables(*section_page)
        url_key = '_'.join(section_page)
        self.assertIn(url_key, self.sos_scraper.table_dict)
        logging.info("'%s' in self.sos_scraper.table_dict;", url_key)
        self.assertIsInstance(self.sos_scraper.table_dict[url_key], list)
        logging.info("isinstance(self.sos_scraper['%s'], list)", url_key)
        for table in self.sos_scraper.table_dict[url_key]:
            self.assertIsInstance(table, pd.DataFrame)
        logging.info("for table in self.sos_scraper['%s']: assert isinstance(table, pd.DataFrame);", url_key)

if __name__ == '__main__':
    unittest.main()
