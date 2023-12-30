#!/usr/bin/python3
"""
Demo of fetching HTML tables.
"""
import pandas as pd

# HTTP: 403 Forbidden
source_url = 'http://serenesforest.net/binding-blade/characters/growth-rates/'
source_url = 'https://en.wikipedia.org/wiki/Friends_(season_2)'
tables = pd.read_html(source_url)
breakpoint()
