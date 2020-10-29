'''
Filters the Paddy Points data for eligable games
'''

import pandas as pd

# Find the teams playing in eligable games
def eligable_teams(week):

    # Need to get full name (from reference file)
    ref = pd.read_csv('References/teams.csv')
    # Create dictionary of {NYG: New York Giants, etc.}
    nfl_teams = pd.Series(ref.Name.values,index=ref.Abrev).to_dict()

    # Read in schedule for week
    sched = pd.read_csv('Schedule/Schedule_Week_' + str(week) + '.csv')

    # Eligable games are scheduled for Sunday or Monday (i.e. Sunday late game)
    sched = sched[(sched['Day'] == "Sun") | (sched['Day'] == "Mon")]
    
    # Return list of eligable teams
    teams = [team for team in (sched["Home"].tolist() + sched["Away"].tolist())]

    # Return dictionary of eligable teams in format {NYG: New York Giants, etc.}
    return {key: nfl_teams[key] for key in teams}


# Filter defence data by eligable teams   
def D_filtered(week, teams):

    # Read Defence data
    defence = pd.read_csv('PaddyPoints/D_Week_' + str(week) + '.csv')

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
    offence = pd.read_csv('PaddyPoints/O_Week_' + str(week) + '.csv')
    # Read Offence data for week prior to schedule week (needed for correct team for filtering)
    # ASSUMPTION: Player at same team as previous week
    offence_sched = pd.read_csv('PaddyPoints/O_Week_' + str(schedule_week-1) + '.csv')

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
    summary_D.to_csv('Output/Defence_Summary.csv')
    
  

# Collate all week's offence Paddy Points data into one csv
def collate_O(schedule_week, teams):

    # Create dictionary to store list of each week's paddy points for each player
    O_weeks_pp = {key : [] for key in sorted(list(O_filtered(schedule_week-1, teams, schedule_week).keys()))}

    # Append Paddy Points for each week
    for i in range(1, schedule_week):
        week_i = O_filtered(i, teams, schedule_week)
        for player, values in week_i.items():
            # Add Paddy Points
            O_weeks_pp[player].append(values[0])

    # Create column names
    columns = [("Week " + str(i)) for i in range(1, schedule_week)]

    # Create DataFrame to store summary
    summary_O = pd.DataFrame.from_dict(O_weeks_pp, orient='index', columns=columns).round(1)

    # Add players' teams
    # Create dictionary with players' teams
    play_team = {key : values[1] for key, values in O_filtered(1, teams, schedule_week).items()}
    summary_O["Team"] = pd.Series(play_team)
    # Reorder columns
    columns.insert(0, "Team")
    summary_O = summary_O[columns]

    # Save summary as output file
    summary_O.to_csv('Output/Offence_Summary.csv')

    
  

def main():
    
    # Choose upcoming week
<<<<<<< HEAD
    schedule_week = 7
=======
    schedule_week = 8
>>>>>>> main

    # Grab eligable teams
    teams = eligable_teams(schedule_week)

    # Output collated data
    collate_D(schedule_week, teams)
    collate_O(schedule_week, teams)

    


if __name__ == "__main__":
    main()
