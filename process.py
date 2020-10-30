'''
Adds useful metrics and sorts output data from filter.py
'''

import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
import itertools

# Open summaries
def open():

    # Open output files
    defence = pd.read_csv('Output/Defence_Summary.csv')
    offence = pd.read_csv('Output/Offence_Summary.csv')

    # Name teams and players columns correctly
    defence = defence.rename(columns={"Unnamed: 0": "Team"})
    offence = offence.rename(columns={"Unnamed: 0": "Name"})

    return (defence, offence)

# Add opponent column
def opponent(offence, defence, upcoming_week):

    # Open upcoming week schedule
    sched = pd.read_csv("Schedule/Schedule_Week_" + str(upcoming_week) + ".csv")

    # Create dictionary {home : away} and {away : home}
    temp_1 = pd.Series(sched.Home.values,index=sched.Away).to_dict()
    temp_2 = pd.Series(sched.Away.values,index=sched.Home).to_dict()
    games = {**temp_1, **temp_2}
    
    # Add opponent columns
    defence.insert(loc=1, column="Opp", value="")
    offence.insert(loc=1, column="Opp", value="")

    for team, opp in games.items():
        # Only eligable teams are in offence/defence
        try:
            defence.at[defence.index[defence["Team"] == team][0], "Opp"] = opp
            offence.at[offence.index[offence["Team"] == team][0], "Opp"] = opp
        except IndexError:
            continue

    print(offence)
    print(defence)


# Add columns with average for season and past 3 weeks
def average_pts(defence, offence):

    # Only keep 'Week i' columns 
    columns_D = sorted([s for s in list(defence) if "Week " in s])
    columns_O = sorted([s for s in list(offence) if "Week " in s])

    # Add average points column
    # Defence
    defence["Avg Points"] = defence.loc[:, columns_D].mean(axis=1).round(1)
    defence["Avg Points (3 weeks)"] = defence.loc[:, columns_D[-3:]].mean(axis=1).round(1)
    # Offence
    print("WARNING: Incorrect assumption that 0 values mean player missed week used in calculating average")
    offence["Avg Points"] = offence.loc[:, columns_O].replace(0, np.NaN).mean(axis=1).round(1)
    offence["Avg Points (3 weeks)"] = offence.loc[:, columns_O[-3:]].replace(0, np.NaN).mean(axis=1).round(1)

    return (defence, offence)

# Add column with salary
def salary(defence, offence, week):

    # Create dicitonary of {players/teams : salary} for upcoming week's salary scraped data
    sal = pd.read_csv('Statistics/FD_Salary_Week_' + str(week) + '.csv')
    salary = pd.Series(sal.Salary.values, index=sal.Name).to_dict()

    # Create dictionary of {New York Giants : NYG, etc.}
    ref = pd.read_csv('References/teams.csv')
    nfl_teams = pd.Series(ref.Abrev.values,index=ref.Name).to_dict()

    # Add Salary column to datatables
    defence["Salary"] = ""
    offence["Salary"] = ""
    # Populate salary column
    for key, value in salary.items():

        # Defence
        # Swap full name for short name
        if key in nfl_teams.keys():
            key = nfl_teams[key]
        if not defence.loc[defence['Team'] == key].empty:
            defence.at[defence.index[defence['Team'] == key], "Salary"] = round(value)

        # Offence
        for name in offence['Name'].to_list():
            # Due to differences in names of datasets need to use fuzzywuzzy. 88 value found by trial and error
            if fuzz.ratio(key, name) > 88:
                offence.at[offence.index[offence['Name'] == name], "Salary" ] = round(value)
    
    return (defence, offence)

# Add injury status column
def injury(offence):

    # Open injury status data
    status = pd.read_csv("Injury_Status.csv")

    # Add injury column to offence
    offence["Injury"] = ""

    # Populate injury column
    for name_inj in status.Name.to_list():
        for name_o in offence.Name.to_list():
            # Due to differences in names of datasets need to use fuzzywuzzy. 88 value found by trial and error
            if fuzz.ratio(name_inj, name_o) > 88:
                # Used this clunky process (.tolist()[0]) because kept getting error message 
                offence.at[offence.index[offence['Name'] == name_o], "Injury"] = status.at[status.index[status['Name'] == name_inj].tolist()[0], "Status"]

# Adds predicted fantasy points column
def predict(offence):

    a = 0


# Produce separate outputs by position
def position(offence, upcoming_week):

    positions = {'QB' : [], 'WR' : [], 'RB' : [], 'TE' : []}

    # Open latest scraped offence data
    latest_O = pd.read_csv('Statistics/O_Week_' + str(upcoming_week-1) + '.csv')

    for index, row in latest_O.iterrows():
        positions[row.Position].append(row.Name)

    # Output csv by position
    pos = pd.DataFrame(columns=offence.columns.values)
    for position in positions.keys():

        # Get all QBs etc.
        for player in positions[position]:
            pos = pos.append(offence.loc[offence['Name'] == player])

        # Sort by descending average fantasy points
        pos = pos.sort_values(by='Avg Points', ascending=False)

        # Only take head of each table (size varies by position)
        if position == 'QB':
            pos = pos.head(25)
        elif position == 'WR':
            pos = pos.head(100)
        elif position == 'RB':
            pos = pos.head(60)
        elif position == 'TE':
            pos = pos.head(50)
            
        # Save position data as csv
        pos.to_csv("Output/" + str(position) + ".csv")
        
        # Remove all rows for next position
        pos = pos[0:0]
        



def main():

    upcoming_week = 8

    # Open summary files
    defence, offence = open()

    opponent(offence, defence, upcoming_week)

'''
    # Add average columns
    defence, offence = average_pts(defence, offence)

    # Add salary column
    defence, offence = salary(defence, offence, upcoming_week)

    # Add injury column
    injury(offence)

    # Save seperate outputs for each position
    position(offence, upcoming_week)

    # Save processed version of defence and offence
    defence.to_csv('Output/DEF.csv')

  '''  

if __name__ == "__main__":
    main()