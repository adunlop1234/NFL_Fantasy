'''
Adds useful metrics and sorts output data from filter.py
'''

import pandas as pd
import numpy as np

# Open summaries
def open():

    # Open output files
    defence = pd.read_csv('Output/Defence_Summary.csv')
    offence = pd.read_csv('Output/Offence_Summary.csv')

    # Name teams and players columns correctly
    defence = defence.rename(columns={"Unnamed: 0": "Team"})
    offence = offence.rename(columns={"Unnamed: 0": "Name"})

    return (defence, offence)

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
        if not offence.loc[offence['Name'] == key].empty:
            offence.at[offence.index[offence['Name'] == key], "Salary"] = round(value)
    
    return (defence, offence)




def main():

    week = 6

    # Open summary files
    defence, offence = open()

    # Add average columns
    defence, offence = average_pts(defence, offence)

    # Add salary column
    defence, offence = salary(defence, offence, week)

    # Save processed version of defence and offence
    defence.to_csv('Output/Defence_P.csv')
    offence.to_csv('Output/Offence_P.csv')

    

if __name__ == "__main__":
    main()