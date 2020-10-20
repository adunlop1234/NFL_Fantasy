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

    # Eligable games are scheduled for Sunday (late games are played early monday morning)
    sched = sched.loc[sched['Day'] == "Sun"]
    
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
def O_filtered(week, teams):

    # Read Offence data
    offence = pd.read_csv('PaddyPoints/O_Week_' + str(week) + '.csv')

    # Filter for eligable teams
    offence = offence[offence["Team"].isin(list(teams.keys()))]

    # Return dictionary of players and their paddy points for this week
    return {row["Name"] : row["Paddy"] for index, row in offence.iterrows()}



# Collate all week's Paddy Points data into one csv
def collate(schedule_week):

    # Grab eligable teams
    teams = eligable_teams(schedule_week)

    # Create DataFrame to store summary
    summary_D = pd.DataFrame({"Team" : list(teams.keys())})
    # Set the Team as the index
    summary_D = summary_D.set_index("Team")

    # Add column for each week
    for i in range(1, schedule_week):
        week_i = D_filtered(i, teams)
        


    
    D_filtered(5, teams)





    
  

def main():
    
    # Choose week's data to filter 
    week = 5
    # Choose schedule week
    schedule_week = 6

    collate(schedule_week)

    


if __name__ == "__main__":
    main()
