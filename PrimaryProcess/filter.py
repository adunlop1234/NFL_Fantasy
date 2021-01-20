import glob
import os
import pandas as pd
from collections import Counter

path = os.path.join('PrimaryProcess','Data','*L.csv')
for fname in glob.glob(path):

    df = pd.read_csv(fname, index_col=0)

    # Assume no player on same team with same name and position
    df['unique'] = df['name'] + df['position'] + df['team']

    # Count number appearences of each player
    appearences = Counter(list(df['unique']))

    # Only keep players with 10 or more appearances
    players_keep = []
    for unique, count in appearences.items():
        if count >= 10:
            players_keep.append(unique)
    df = df.loc[df.unique.isin(players_keep)]

    # Drop unique column and save 
    df = df.drop(columns=['unique'])
    df.to_csv(fname[:len(fname)-5] + 'Lf.csv')
    
