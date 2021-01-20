import pandas as pd
import os

### Create dictionaries to store data

## Team data (defence and offence)
team_data = {}

# Get list of teams
ref = pd.read_csv(os.path.join('References','teams.csv'))
nfl_teams = list(pd.read_csv(os.path.join('References','teams.csv')).Abrev)

# Loop over each season
for season in [15, 16, 17, 18, 19, 20]:
    team_data[season] = {}

    # Loop over teams
    for team in nfl_teams:
        team_data[season][team] = {}

        # Loop over weeks
        for week in range(1,18):
            team_data[season][team][week] = 'BYE'

## Player data
player_data = {}

# Loop over each season
for season in [15, 16, 17, 18, 19, 20]:
    player_data[season] = {}
    
    # Get set of players from season
    players = set(pd.read_csv(os.path.join('PrimaryProcess','Data', str(season) + 'Lf.csv'))['name'])

    # Loop over players
    for player in players:
        player_data[season][player] = {}

        # Loop over weeks
        for week in range(1,18):
            player_data[season][player][week] = 'BYE'


### Populate 

## Team data (defence and offence)

# Loop over each season
for season in [15, 16, 17, 18, 19, 20]:

    # Create dictionaries to store data
    features_D = {'home_game': None, 'pass_cmp' : None, 'pass_att' : None, 'pass_yds' : None, 'pass_td' : None, 'pass_int' : None, 'pass_sacked' : None, 'rush_att' : None, 'rush_yds' : None, 'rush_td' : None}
    features_O = {'rush_att' : None, 'rush_yds' : None, 'rush_td' : None}
    
    # Loop over defence and offence
    for side in ['D', 'O']:

        # Open DataFrame
        df = pd.read_csv(os.path.join('PrimaryProcess','Data', str(season) + side + '.csv'))
        
        # Loop over rows
        for index, row in df.iterrows():

            if side == 'D':
                f = features_D.copy()
            else:
                f = features_O.copy()

            for key in f.keys():
                f[key] = row[key]

            team_data[season][row.team][row.week_num] = f

## Player data

# Loop over each season
for season in [15, 16, 17, 18, 19, 20]:

    # Create dictionaries to store data
    features = {'home_game': None, 'pass_cmp' : None, 'pass_att' : None, 'pass_yds' : None, 'pass_td' : None, 'pass_int' : None, 'pass_sacked' : None, 'rush_att' : None, 'rush_yds' : None, 'rush_td' : None}
    
    # Open DataFrame
    df = pd.read_csv(os.path.join('PrimaryProcess','Data', str(season) + 'Lf.csv'))

    # Only keep QBs
    df = df.loc[df.position == 'QB']

    # Loop over rows
    for index, row in df.iterrows():

        f = features.copy()

        for key in f.keys():
            if key == 'home_game':
                continue
            f[key] = row[key]

        f['home_game'] = False if row.game_location == '@' else True

        player_data[season][row['name']][row.week_num] = f


### Create labelled features DataFrame

# Define feature columns
columns = []
for preceeding in range(1,7):
    for item in ['P', 'D', 'O']:
        for feature in ['home_game', 'pass_cmp', 'pass_att', 'pass_yds', 'pass_td', 'pass_int', 'pass_sacked', 'rush_att', 'rush_yds', 'rush_td']:
            columns.append(item + str(preceeding) + '_' + feature)
    for feature in ['rush_att', 'rush_yds', 'rush_td']:
        columns.append('O' + str(preceeding) + '_' + feature)
# Add label column
columns.add('Label_pass_yds')


