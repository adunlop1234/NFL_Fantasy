import pandas as pd
import os
import statistics
import numpy as np

### Create dictionaries to store data

## Team data (defence and offence)
team_data = {}

# Get list of teams
ref = pd.read_csv(os.path.join('References','teams.csv'))
nfl_teams = list(pd.read_csv(os.path.join('References','teams.csv')).Abrev)

# Create dictionaries to store data (by default a BYE week)
features_D = {'home_game': 'BYE', 'pass_cmp' : 0, 'pass_att' : 0, 'pass_yds' : 0, 'pass_td' : 0, 'pass_int' : 0, 'pass_sacked' : 0, 'rush_att' : 0, 'rush_yds' : 0, 'rush_td' : 0}
features_O = {'rush_att' : 0, 'opp' : 0, 'rush_yds' : 0, 'rush_td' : 0}    
    
# Loop over each season
for season in [15, 16, 17, 18, 19, 20]:
    team_data[season] = {}

    # Loop over teams
    for team in nfl_teams:
        team_data[season][team] = {}

        # Loop over weeks
        for week in range(1,18):

            team_data[season][team][week] = {}

            team_data[season][team][week]['D'] = features_D.copy()
            team_data[season][team][week]['O'] = features_O.copy()

## Player data
player_data = {}

# Create dictionary to store data (by default player is NO_PLAY (either BYE or OUT injured))
features_P = {'team' : 0, 'home_game': 'NO_PLAY', 'pass_cmp' : 0, 'pass_att' : 0, 'pass_yds' : 0, 'pass_td' : 0, 'pass_int' : 0, 'pass_sacked' : 0, 'rush_att' : 0, 'rush_yds' : 0, 'rush_td' : 0}

# Loop over each season
for season in [15, 16, 17, 18, 19, 20]:
    player_data[season] = {}
    
    # Get set of QBs from season
    df = pd.read_csv(os.path.join('PrimaryProcess','Data', str(season) + 'Lf.csv'))
    players = set(df.loc[df.position == 'QB']['name'])

    # Loop over players
    for player in players:
        player_data[season][player] = {}

        # Loop over weeks
        for week in range(1,18):

            player_data[season][player][week] = features_P.copy()


### Populate 

## Team data (defence and offence)

# Loop over each season
for season in [15, 16, 17, 18, 19, 20]:
    
    # Loop over defence and offence
    for side in ['D', 'O']:

        # Open DataFrame
        df = pd.read_csv(os.path.join('PrimaryProcess','Data', str(season) + side + '.csv'))
        
        # Loop over rows
        for index, row in df.iterrows():

            # Populate dictonaries
            for key in team_data[season][row.team][row.week_num][side].keys():
                team_data[season][row.team][row.week_num][side][key] = row[key]


## Player data

# Loop over each season
for season in [15, 16, 17, 18, 19, 20]:

    # Open DataFrame
    df = pd.read_csv(os.path.join('PrimaryProcess','Data', str(season) + 'Lf.csv'))

    # Only keep QBs
    df = df.loc[df.position == 'QB']

    # Loop over rows
    for index, row in df.iterrows():

        for key in features_P.keys():
            if key == 'home_game':
                continue
            player_data[season][row['name']][row.week_num][key] = row[key]

        player_data[season][row['name']][row.week_num]['home_game'] = False if row.game_location == '@' else True


### Create labelled features DataFrame

# Define multi-index feature columns ('name', 'week', 'season' are for checking purposes only)
columns = [('','name'), ('','week'), ('','season')]
# Begin with player data (seperate loops for desired column order)
for preceeding in range(1,7):
    for feature in [f for f in features_P.keys() if f != 'team']:
        columns.append(('QB', feature + '_' + str(preceeding)))
# Remaining offence data
for preceeding in range(1,7):
    for feature in [f for f in features_O.keys() if f != 'opp']:
        columns.append(('Offence', feature + '_' + str(preceeding)))
# Previous defence data
for preceeding in range(1,7):
    for feature in [f for f in features_D.keys() if f != 'home_game']:
        columns.append(('Defence_prev_mean', feature + '_' + str(preceeding)))
# Upcoming defence data
for feature in [f for f in features_D.keys() if f != 'home_game']:
        columns.append(('Defence_upcom_mean', feature + '_upcoming'))
columns.append(('Label','pass_yds'))

# Create multi-index column DataFrame
features = pd.DataFrame(columns=pd.MultiIndex.from_tuples(columns))

# Loop over each season
c = 0
null_count = 0
# Loop over each season
for season, season_dict in player_data.items():

    # Loop over QBs
    for qb, qb_dict in season_dict.items():

        # Loop over weeks from week 7, discounting week 17
        for week in range(7,17):

            # Check if QB didn't play week
            if player_data[season][qb][week]['pass_yds'] == 0:
                continue

            # Add data for ease of checking
            features.loc[c, ('','name')] = qb
            features.loc[c, ('','week')] = week
            features.loc[c, ('','season')] = season

            # Add label
            features.loc[c, ('Label','pass_yds')] = player_data[season][qb][week]['pass_yds']

            team = player_data[season][qb][week]['team']


            # Loop over preceeding weeks
            for preceeding in range(1,7):

                # Populate player features
                for feature in [f for f in features_P.keys() if f != 'team']:
                    features.loc[c, ('QB', feature + '_' + str(preceeding))] = player_data[season][qb][week-preceeding][feature]

                # Populate offence features
                for feature in [f for f in features_O.keys() if f != 'opp']:
                    features.loc[c, ('Offence', feature + '_' + str(preceeding))] = team_data[season][team][week-preceeding]['O'][feature]
                
                # Populate previous games defence features
                opp = team_data[season][team][week-preceeding]['O']['opp']
                # Check if week-preceeding was bye week
                if opp == 0:
                    for feature in [f for f in features_D.keys() if f != 'home_game']:
                        features.loc[c, ('Defence_prev_mean', feature + '_' + str(preceeding))] = 0
                else:
                    f_D = {f : [] for f in features_D.keys() if f != 'home_game'}
                    # Calculate mean value for 6 weeks previous to upcoming week
                    for week_i in range(1,7):
                        # Check if BYE
                        if team_data[season][opp][week-week_i]['D']['rush_yds'] == 0:
                            continue
                        for f in f_D.keys():
                            f_D[f].append(team_data[season][opp][week-week_i]['D'][f])
                    for feature in [f for f in features_D.keys() if f != 'home_game']:
                        features.loc[c, ('Defence_prev_mean', feature + '_' + str(preceeding))] = statistics.mean(f_D[feature])


            # Populate upcoming defence mean features
            # Populate previous games defence features
            opp = team_data[season][team][week]['O']['opp']
            f_D = {f : [] for f in features_D.keys() if f != 'home_game'}
            # Calculate mean value for 6 weeks previous to upcoming week
            for week_i in range(1,7):
                # Check if BYE
                if team_data[season][opp][week-week_i]['D']['rush_yds'] == 0:
                    continue
                for f in f_D.keys():
                    f_D[f].append(team_data[season][opp][week-week_i]['D'][f])
            for feature in [f for f in features_D.keys() if f != 'home_game']:
                features.loc[c, ('Defence_upcom_mean', feature + '_upcoming')] = statistics.mean(f_D[feature])

            # Check for null values
            if features.loc[c].isnull().values.any():
                null_count += 1
                features.loc[c] = np.nan
            else:
                c += 1

print(str(null_count) + ' rows were removed due to containing NULL values')

# Save features as DataFrame
features.to_csv(os.path.join('NeuralPassing','Data','qbPassingFeatures.csv'))
