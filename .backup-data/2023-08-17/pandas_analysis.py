#!/usr/bin/python3
"""
Fetches data from SF.net
Converts data into pd.DF object
Relates unit bases to growths via foreign key = unit-name
"""

base_stats_url = "https://serenesforest.net/binding-blade/characters/base-stats/"
growth_rates_url = "https://serenesforest.net/binding-blade/characters/growth-rates/"

import pandas as pd
# pd.read_html -> pd.to_sql
#import sqlalchemy

# Extract data
# Convert to DataFrame object
# Convert to SQL database
# Foreign keys
