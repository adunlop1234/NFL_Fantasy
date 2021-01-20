import pandas as pd
from collections import Counter
import os

df = pd.read_csv(os.path.join('Static', 'staticData', 'players.csv'))

# Only keep players who have played in most recent years
df = df[df.end.isin([2015,2016,2017,2018,2019,2020])]

# Only keep offensive fantasy position groups
df = df[df.position.isin(['WR', 'TE', 'FB', 'RB', 'HB', 'QB', 'K'])]

# Map HBs and FBs as RBs
df.position = df.position.replace({'HB' : 'RB', 'FB' : 'RB'})

# Strip whitespace from names
df['name'] = df['name'].str.strip()

df.reset_index(drop=True).to_csv(os.path.join('Static', 'staticData', 'filteredPlayers.csv'))
