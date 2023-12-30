#!/usr/bin/python3
"""
"""
#from bs4 import BeautifulSoup
from requests import get
import pandas as pd

SOURCE_URL = 'https://serenesforest.net/binding-blade/characters/growth-rates/'
SOURCE_URL = 'https://serenesforest.net/blazing-sword/characters/base-stats/'
SOURCE_URL = 'https://serenesforest.net/genealogy-of-the-holy-war/characters/base-stats/'
table_list = pd.read_html(get(SOURCE_URL).text)
# https://stackoverflow.com/questions/33961028/remove-non-numeric-rows-in-one-column-with-pandas
#new_table_list = [table[pd.to_numeric(table['HP'], errors='coerce').notnull()] for table in table_list]
breakpoint()
