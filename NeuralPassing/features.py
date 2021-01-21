import pandas as pd
import os

print('REMEMBER THIS IS QB SPECIFIC')

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

# Define feature columns ('name', 'week', 'season' are for checking purposes only)
columns = ['name', 'week', 'season']
for preceeding in range(1,7):
    for item in ['P', 'D']:
        for feature in features_D.keys():
            columns.append(item + str(preceeding) + '_' + feature)
    for feature in features_O.keys():
        columns.append('O' + str(preceeding) + '_' + feature)
# Add label column
columns.append('Label_pass_yds')

# Create dictionary to store feature values
features = {column : [] for column in columns}


# Loop over each season
for season, season_dict in player_data.items():

    # Loop over QBs
    for qb, qb_dict in season_dict.items():

        # Loop over weeks from week 7, discounting week 17
        for week in range(7,17):

            # Check if QB didn't play week
            if player_data[season][qb][week]['team'] == 0:
                continue
            
            features['name'].append(qb)
            features['week'].append(week)
            features['season'].append(season)

            # Add label
            features['Label_pass_yds'].append(player_data[season][qb][week]['pass_yds'])          

            # Loop over preceeding weeks
            for preceeding in range(1,7):

                # Populate player features
                for feature in set(features_P.keys()) - set(['team']):
                    features['P' + str(preceeding) + '_' + feature].append(player_data[season][qb][week-preceeding][feature])

                # Populate defence and offence features
                team = player_data[season][qb][week]['team']
                for feature in features_D.keys():
                    features['D' + str(preceeding) + '_' + feature].append(team_data[season][team][week-preceeding]['D'][feature])
                for feature in features_O.keys():
                    features['O' + str(preceeding) + '_' + feature].append(team_data[season][team][week-preceeding]['O'][feature])


                
# Save features as DataFrame
pd.DataFrame.from_dict(features).to_csv(os.path.join('NeuralPassing','Data','qbPassingFeatures.csv'))
