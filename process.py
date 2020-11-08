'''
Adds useful metrics and sorts output data from filter.py
'''

import pandas as pd
import numpy as np
import itertools
from factors import defence_factors, offence_factors, defence_defence_factors
from scraper import scrape_injuries
import sys, os

# Open summaries
def open():

    # Open output files
    defence = pd.read_csv('Processed/Defence_Summary.csv')
    offence = pd.read_csv('Processed/Offence_Summary.csv')

    # Name teams and players columns correctly
    defence = defence.rename(columns={"Unnamed: 0": "Team"})
    offence = offence.rename(columns={"Unnamed: 0": "Name"})

    return (defence, offence)

# Add opponent column
def opponent(offence, defence, upcoming_week):

    # Open upcoming week schedule
    sched = pd.read_csv("Scraped/Schedule/Schedule_Week_" + str(upcoming_week) + ".csv")

    # Create dictionary {home : away} and {away : home}
    temp_1 = pd.Series(sched.Home.values,index=sched.Away).to_dict()
    temp_2 = pd.Series(sched.Away.values,index=sched.Home).to_dict()
    games = {**temp_1, **temp_2}
    
    # Add opponent columns
    defence.insert(loc=1, column="Opp", value="")
    offence.insert(loc=2, column="Opp", value="")

    for team, opp in games.items():
        # Only eligable teams are in offence/defence
        try:
            # Defence
            defence.at[defence.index[defence["Team"] == team][0], "Opp"] = opp
            # Offence
            # Get all players from given team
            play_ind = offence[offence["Team"] == team].index.values
            offence.at[play_ind, "Opp"] = opp
        except IndexError:
            continue

    return defence, offence


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
    offence["Avg Points"] = offence.loc[:, columns_O].replace('', np.NaN).mean(axis=1).round(1)
    offence["Avg Points (3 weeks)"] = offence.loc[:, columns_O[-3:]].replace('', np.NaN).mean(axis=1).round(1)

    return (defence, offence)

# Add column with salary
def salary(defence, offence, week):

    # Create dicitonary of {players/teams : salary} for upcoming week's salary scraped data
    sal = pd.read_csv('Scraped/Statistics/FD_Salary_Week_' + str(week) + '.csv')
    salary = pd.Series(sal.Salary.values, index=sal.Name).to_dict()

    # Create dictionary of {New York Giants : NYG, etc.}
    ref = pd.read_csv('References/teams.csv')
    nfl_teams = pd.Series(ref.Abrev.values,index=ref.Name).to_dict()

    # Add Salary column to datatables
    defence["Salary"] = ""
    offence["Salary"] = ""
    # Populate salary column
    for player, salary in salary.items():

        # Defence
        # Swap full name for short name
        if player in nfl_teams.keys():
            player = nfl_teams[player]
        if not defence.loc[defence['Team'] == player].empty:
            defence.at[defence.index[defence['Team'] == player], "Salary"] = round(salary)

        # Offence
        for name in offence['Name'].tolist():
            # Use custom made simplify function to remove offending differences
            if simplify(player) == simplify(name):
                offence.at[offence.index[offence['Name'] == name], "Salary" ] = round(salary)
                break
        

    
    return (defence, offence)

# Add injury status column
def injury(offence):

    # Open injury status data
    status = pd.read_csv("Scraped/Injury_Status.csv")

    # Add injury column to offence
    offence["Injury"] = ""

    # Populate injury column
    for name_inj in status.Name.tolist():
        for name_o in offence.Name.tolist():
            # Use custom made simplify function to remove offending differences
            if simplify(name_inj) == simplify(name_o):
                offence.at[offence.index[offence['Name'] == name_o], "Injury"] = status.at[status.index[status['Name'] == name_inj].tolist()[0], "Status"]
                break

    return offence


# Adds predicted points column to defence
def predict_D(defence):

    # Open defence_defence factors
    factors = pd.read_csv("Processed/Defence_Defence_Factors.csv")
    # Reformat as dict {Team : Factor}
    fact = pd.Series(factors["Defence Factor"].values,index=factors.Team).to_dict()

    # Create dictionary of {NYG : New York Giants, etc.}
    ref = pd.read_csv('References/teams.csv')
    nfl_teams = pd.Series(ref.Name.values,index=ref.Abrev).to_dict()

    # Add Predicted Fantasy Points column
    defence["Predicted"] = ""

    # Add column to defence
    for index, row in defence.iterrows(): 
            # Calculate predicted points (factor * (0.7 AvFPts + 0.3 3wAvFPts))
            defence.at[index, "Predicted"] = round(fact[nfl_teams[row["Team"]]]*(0.7*row["Avg Points"] + 0.3*row["Avg Points (3 weeks)"]),2)

    return defence



# Returns factor for offence player depending on opposition
def predict_O(opp, position):

    # Open defence factors
    factors = pd.read_csv("Processed/Defence_Factors.csv")
    
    # Create dictionary of {NYG : New York Giants, etc.}
    ref = pd.read_csv('References/teams.csv')
    nfl_teams = pd.Series(ref.Name.values,index=ref.Abrev).to_dict()

    # Get row for given team
    try:
        row = factors.loc[factors["Team"] == nfl_teams[opp]]
    except KeyError:
        # This is caused by different players of same name (e.g. Ryan Griffin) not being filtered by eligable teams because one is playing and one is not
        return 0

    if position == 'QB':
        return row["QB Factor"].values[0]
    elif position == 'WR' or position == 'TE':
        return row["Pass Factor (D)"].values[0]
    elif position == 'RB':
        return row["Rush Factor (D)"].values[0]

    # If not returned value by now, error happened
    print("ERROR in predict_O()")
        


# Produce separate outputs by position
def position(offence, upcoming_week):

    positions = {'QB' : [], 'WR' : [], 'RB' : [], 'TE' : []}

    # Open latest scraped offence data
    latest_O = pd.read_csv('Scraped/Statistics/O_Week_' + str(upcoming_week-1) + '.csv')

    for index, row in latest_O.iterrows():
        positions[row.Position].append(row.Name)

    # Output csv by position
    pos = pd.DataFrame(columns=offence.columns.values)
    # Add Predicted Fantasy Points column
    pos["Predicted"] = ""
    for position in positions.keys():

        # Get all QBs etc.
        for player in positions[position]:
            pos = pos.append(offence.loc[offence['Name'] == player])

        # Add Predicted Fantasy Points column
        pos["Predicted"] = ""
        for index, row in pos.iterrows(): 
            # Calculate predicted points (factor * (0.7 AvFPts + 0.3 3wAvFPts))
            pos.at[index, "Predicted"] = round(predict_O(row.Opp, position)*(0.7*row["Avg Points"] + 0.3*row["Avg Points (3 weeks)"]),2)

        # Sort by descending average fantasy points
        pos = pos.sort_values(by='Predicted', ascending=False)

        # Only take head of each table (size varies by position)
        if position == 'QB':
            pos = pos.head(32)
        elif position == 'WR':
            pos = pos.head(150)
        elif position == 'RB':
            pos = pos.head(100)
        elif position == 'TE':
            pos = pos.head(100)
            
        # Save position data as csv
        pos.to_csv("Output/" + str(position) + ".csv")
        
        # Remove all rows for next position
        pos = pos[0:0]

# For string comparisons, remove the offending parts       
def simplify(name):
    # Need to strip big to small (e.g. strip III before II otherwise doesnt work)
    return name.replace('.','').replace('Jr','').replace('Sr','').replace('III','').replace('II','').replace('IV','').replace('V','').strip()


def main():

    upcoming_week = 9

    # Update injury status
    scrape_injuries()

    # Update Factors
    c_D = {"pass_yds" : 0.25, "pass_yds_att" : 0.4, "pass_td" : 0.35, "rush_yds" : 0.4, "rush_yds_carry" : 0.3, "rush_td" : 0.3, "pass_yds_qb" : 0.4, "pass_yds_att_qb" : 0.3, "pass_td_qb" : 0.3, "INT" : 0.1}
    c_O = {"pass_yds" : 0.25, "pass_yds_att" : 0.3, "pass_td" : 0.45, "rush_yds" : 0.25, "rush_yds_carry" : 0.3, "rush_td" : 0.45}
    c_DD = {"pass" : 0.5, "rush" : 0.5, "fum" : 0, "INT" : 0, "sacks" : 0}
    defence_factors(c_D)
    offence_factors(c_O)
    defence_defence_factors(c_DD, upcoming_week)

    # Open summary files
    defence, offence = open()

    # Add opponent column
    defence, offence = opponent(offence, defence, upcoming_week)

    # Add average columns
    defence, offence = average_pts(defence, offence)

    # Add salary column
    defence, offence = salary(defence, offence, upcoming_week)

    # Add injury column
    offence = injury(offence)

    # Save seperate outputs for each position
    position(offence, upcoming_week)

    defence = predict_D(defence)

    # Save processed version of defence
    defence.to_csv(os.path.join('Output', 'DEF.csv'))


if __name__ == "__main__":
    main()