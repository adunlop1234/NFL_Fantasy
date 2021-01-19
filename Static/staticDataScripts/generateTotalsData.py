import pandas as pd
import os

# Create dictionary to store defensive and offensive data
columns = ['team', 'opp', 'game_date', 'week_num', 'home_game', 'pass_cmp', 'pass_att', 'pass_cmp_perc',
       'pass_yds','pass_td','pass_int','pass_sacked','pass_yds_per_att', 'rush_att', 'rush_yds', 'rush_yds_per_att', 'rush_td', 'fumbles']
def_dict = {column : [] for column in columns}
off_dict = {column : [] for column in columns}

# Use offensive gamelogs to calculate defense data
df = pd.read_csv(os.path.join("Static", "staticDataScripts", "staticData", "playersGamelogs.csv"))

# Create new column to allow for iteration
df['helper_id'] = df['game_date'] + df['opp']


# Iterate over each game for each defence
for id in set(df['helper_id']):

       # Get subset corresponding to one defence for one game
       game = df[df.helper_id == id].fillna(0)

       ## DEFENCE
       def_dict['team'].append(list(game['opp'])[0])
       def_dict['opp'].append(list(game['team'])[0])
       def_dict['game_date'].append(list(game['game_date'])[0])
       def_dict['week_num'].append(list(game['week_num'])[0])
       if list(game['game_location'])[0] == '@':
              def_dict['home_game'].append(True)
       else:
              def_dict['home_game'].append(False)
       def_dict['pass_cmp'].append(sum(list(game['pass_cmp'])))
       def_dict['pass_att'].append(sum(list(game['pass_att'])))
       def_dict['pass_cmp_perc'].append(round(100 * sum(list(game['pass_cmp'])) / sum(list(game['pass_att'])),1))
       def_dict['pass_yds'].append(sum(list(game['pass_yds'])))
       def_dict['pass_td'].append(sum(list(game['pass_td'])))
       def_dict['pass_int'].append(sum(list(game['pass_int'])))
       def_dict['pass_sacked'].append(sum(list(game['pass_sacked'])))
       def_dict['pass_yds_per_att'].append(round(sum(list(game['pass_yds'])) / sum(list(game['pass_att'])),2))
       def_dict['rush_att'].append(sum(list(game['rush_att'])))
       def_dict['rush_yds'].append(sum(list(game['rush_yds'])))
       def_dict['rush_yds_per_att'].append(round(sum(list(game['rush_yds'])) / sum(list(game['rush_att']),2)))
       def_dict['rush_td'].append(sum(list(game['rush_td'])))
       def_dict['fumbles'].append(sum(list(game['fumbles'])))

       ## OFFENCE
       off_dict['team'].append(list(game['team'])[0])
       off_dict['opp'].append(list(game['opp'])[0])
       off_dict['game_date'].append(list(game['game_date'])[0])
       off_dict['week_num'].append(list(game['week_num'])[0])
       if list(game['game_location'])[0] == '@':
              off_dict['home_game'].append(False)
       else:
              off_dict['home_game'].append(True)
       off_dict['pass_cmp'].append(sum(list(game['pass_cmp'])))
       off_dict['pass_att'].append(sum(list(game['pass_att'])))
       off_dict['pass_cmp_perc'].append(round(100 * sum(list(game['pass_cmp'])) / sum(list(game['pass_att'])),1))
       off_dict['pass_yds'].append(sum(list(game['pass_yds'])))
       off_dict['pass_td'].append(sum(list(game['pass_td'])))
       off_dict['pass_int'].append(sum(list(game['pass_int'])))
       off_dict['pass_sacked'].append(sum(list(game['pass_sacked'])))
       off_dict['pass_yds_per_att'].append(round(sum(list(game['pass_yds'])) / sum(list(game['pass_att'])),2))
       off_dict['rush_att'].append(sum(list(game['rush_att'])))
       off_dict['rush_yds'].append(sum(list(game['rush_yds'])))
       off_dict['rush_yds_per_att'].append(round(sum(list(game['rush_yds'])) / sum(list(game['rush_att']),2)))
       off_dict['rush_td'].append(sum(list(game['rush_td'])))
       off_dict['fumbles'].append(sum(list(game['fumbles'])))


# Create dataframe from dictionary
defence = pd.DataFrame.from_dict(def_dict).sort_values(['team', 'game_date']).reset_index(drop=True)
offence = pd.DataFrame.from_dict(off_dict).sort_values(['team', 'game_date']).reset_index(drop=True)

defence.to_csv(os.path.join("Static", "staticDataScripts", "staticData", "defenceData.csv"))
offence.to_csv(os.path.join("Static", "staticDataScripts", "staticData", "offenceData.csv"))