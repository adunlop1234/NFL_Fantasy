import requests
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar
import os
import pandas as pd
import copy

# Years and Columns to keep
YEARS = [2015,2016,2017,2018,2019,2020]
DATA_STATS = ['game_date', 'game_num', 'week_num', 'team', 'game_location', 'opp', 'game_result', 'pass_cmp', 'pass_att', 'pass_cmp_perc', 'pass_yds', 'pass_td', 'pass_int', 'pass_sacked', 'pass_yds_per_att', 'rush_att', 'rush_yds', 'rush_yds_per_att', 'rush_td', 'targets', 'rec', 'rec_yds', 'rec_yds_per_rec', 'rec_td', 'catch_pct', 'rec_yds_per_tgt', 'fumbles']

# Read in players of interest
df = pd.read_csv(os.path.join('Static','staticData','filteredPlayers.csv'))

# Create progress bar
bar = IncrementalBar('Scraping Player Gamelogs', max = len(df), suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')

# Create a dictionary to store all data
data = dict()
for col in ['name', 'position'] + DATA_STATS:
    data[col] = []

# Loop over players
for index, df_row in df.iterrows():

    # Get player's gamelog HTML
    URL = 'https://www.pro-football-reference.com/players/' + df_row.id[0] + '/' + df_row.id + '/gamelog/'
    page = requests.get(URL, allow_redirects=True)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get rows of 'all_stats' table
    try:
        rows = soup.find('div', attrs={'id': 'all_stats'}).find_all('tr')
    # If no data exists for player
    except AttributeError:
        continue

    # Only keep rows of desired year
    rows_keep = []
    for row in rows:
        # Check it's a stat row (not header)
        try:
            if row['id'][:6] == 'stats.':
                # Check year
                if int(row.find('td', attrs={'data-stat' : "year_id"}).text) in YEARS:
                    rows_keep.append(row)
        except KeyError:
            continue
    rows = rows_keep

    # Create dictionary to store column values (columns in different order depending on player, hence use of dict)
    values = {'name' : [df_row['name']] * len(rows),'position' : [df_row['position']] * len(rows)}
    for header in DATA_STATS:
        values[header] = [None] * len(rows)

    # Loop over each row and populate dictionary
    for i, row in enumerate(rows):

        # Get all entries
        items = row.find_all('td')

        for item in items:
            if item['data-stat'] in DATA_STATS:
                values[item['data-stat']][i] = item.text

    # Add current player's data to complete dataset
    for col in data.keys():
        data[col] += values[col]

    bar.next()

bar.finish()

# Create a dataframe from data dict
df = pd.DataFrame.from_dict(data)

# Map team abbreviations
ref = pd.read_csv(os.path.join('References','abrev.csv'))
abrevs = pd.Series(ref.abrev.values,index=ref.pfr).to_dict()
df = df.replace({'team' : abrevs, 'opp' : abrevs})

df.to_csv(os.path.join("Static", "staticData", "playersGamelogs.csv"))
        

    
