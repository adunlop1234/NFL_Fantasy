'''
Filters the Paddy Points data for eligable games
'''

import pandas as pd
import re
from collections import Counter
import sys, os

# Find the teams playing in eligable games
def eligable_teams(week):

    # Need to get full name (from reference file)
    ref = pd.read_csv('References/teams.csv')
    # Create dictionary of {NYG: New York Giants, etc.}
    nfl_teams = pd.Series(ref.Name.values,index=ref.Abrev).to_dict()

    # Read in schedule for week
    sched = pd.read_csv('Scraped/Schedule/Schedule_Week_' + str(week) + '.csv')

    # Eligable games are scheduled for Sunday and maybe Monday (i.e. Sunday late game)
    sched = sched[(sched['Day'] == "Sun")] #| (sched['Day'] == "Mon")]
    
    # Return list of eligable teams
    teams = [team for team in (sched["Home"].tolist() + sched["Away"].tolist())]

    # Return dictionary of eligable teams in format {NYG: New York Giants, etc.}
    return {key: nfl_teams[key] for key in teams}


# Filter defence data by eligable teams   
def D_filtered(week, teams):

    # Read Defence data
    defence = pd.read_csv('Processed/PaddyPoints/D_Week_' + str(week) + '.csv')

    # Filter for eligable teams
    defence = defence[defence["Name"].isin(list(teams.values()))]

    # Create dict of week's teams and paddy points
    points_temp = {row["Name"] : row["Paddy"] for index, row in defence.iterrows()}

    # Replace full name keys with abbrev keys
    # Need to get full name (from reference file)
    ref = pd.read_csv('References/teams.csv')

    # Create dictionary of {New York Giants: NYG, etc.}
    nfl_teams = pd.Series(ref.Abrev.values,index=ref.Name).to_dict()

    # Return dictionary of teams and paddy points for this week
    return {nfl_teams[key] : value for key, value in points_temp.items()}
    
    

# Filter offence data by eligable teams   
def O_filtered(week, teams, schedule_week):

    # Read Offence data for week
    offence = pd.read_csv('Processed/PaddyPoints/O_Week_' + str(week) + '.csv')

    # Read Offence data for week prior to schedule week (needed for correct team for filtering)
    # * ASSUMPTION: Player at same team as previous week
    offence_sched = pd.read_csv('Scraped/Statistics/O_Week_' + str(schedule_week-1) + '.csv')
    # Need to reassign LA as LAR
    offence_sched = offence_sched.replace(to_replace=r'\bLA\b', value='LAR', regex=True)

    # Find eligable players (based on team)
    offence_sched = offence_sched[offence_sched["Team"].isin(list(teams.keys()))]
    players = offence_sched["Name"].tolist()

    # Filter for eligable players
    offence = offence[offence["Name"].isin(players)]


    # Return dictionary of {players : [paddy points, team] } for this week
    return {row["Name"] : [row["Paddy"], row["Team"]] for index, row in offence.iterrows()}



# Collate all week's defence Paddy Points data into one csv
def collate_D(schedule_week, teams):

    # Create dictionary to store list of each week's paddy points for each team
    D_weeks_pp = {key : [] for key in sorted(list(teams.keys()))}
    
    # Append Paddy Points for each week
    for i in range(1, schedule_week):
        week_i = D_filtered(i, teams)
        for team, points in week_i.items():
            D_weeks_pp[team].append(points)
    
    # Create column names
    columns = [("Week " + str(i)) for i in range(1, schedule_week)]

    # Create DataFrame to store summary
    summary_D = pd.DataFrame.from_dict(D_weeks_pp, orient='index', columns=columns).round(1)
    
    # Save summary as output file
    summary_D.to_csv(os.path.join('Processed','Defence_Summary.csv'))
    
  

# Collate all week's offence Paddy Points data into one csv
def collate_O(schedule_week, teams):
    
    # Read in fantasy data scraped from previous week
    df = pd.read_csv("Scraped/Statistics/O_Week_" + str(schedule_week-1) + ".csv")

    # Create list of names which appear more than once (no significant players, so just going to ignore these people)
    cnt = Counter(df["Name"].tolist())
    common_names = [k for k, v in cnt.items() if v > 1]

    # Create dictionary with players' teams
    play_team = dict(zip(df["Name"].tolist(), df["Team"].tolist()))
    for name, team in play_team.items():
        if team == "LA":
            play_team[name] = "LAR"
    
    # Create dictionary to store list of each week's paddy points for each eligable player
    O_weeks_pp = {name : ['']*(schedule_week-1) for name, team in play_team.items() if team in teams}

    # Append Paddy Points for each week
    for i in range(1, schedule_week):
        week_i = O_filtered(i, teams, schedule_week)
        for player, values in week_i.items():
            # Ignore players with same name as another player (no significant players, so just going to ignore these people for simplicity)
            if player in common_names:
                continue
            # Add Paddy Points
            O_weeks_pp[player][i-1] = round(values[0],2)

    # Create column names
    columns = [("Week " + str(i)) for i in range(1, schedule_week)]

    # Create DataFrame to store summary
    summary_O = pd.DataFrame.from_dict(O_weeks_pp, orient='index', columns=columns).round(1)

    # Add players' teams
    summary_O["Team"] = pd.Series(play_team)
    # Reorder columns
    columns.insert(0, "Team")
    summary_O = summary_O[columns]

    # Save summary as output file
    summary_O.to_csv(os.path.join('Processed','Offence_Summary.csv'))

    
  

def main():
    
    # Choose upcoming week
    schedule_week = 9

    # Grab eligable teams
    teams = eligable_teams(schedule_week)

    # Output collated data
    collate_D(schedule_week, teams)
    collate_O(schedule_week, teams)

    


if __name__ == "__main__":
    main()
