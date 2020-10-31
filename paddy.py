'''
Appends Paddy Power Points column to scraped data
'''

import pandas as pd
import sys

def paddy_points(week):

    # Read csv into a dataframe
    defence = pd.read_csv('Statistics/D_Week_' + str(week) + '.csv')
    offence = pd.read_csv('Statistics/O_Week_' + str(week) + '.csv')

    # Replace '-' with 0
    defence = defence.replace('-', 0)
    offence = offence.replace('-', 0)
    # Fill empty values with 0
    offence = offence.fillna(0)

    # Convert numbers to numeric data types
    d_stats = ["Sacks", "Def INT", "Fum Rec", "Saf", "Def TD",
               "Def 2pt Ret", "Def Ret TD", "Pts Allowed", "Points Total"]
    o_stats = ["Pass Yds", "Pass TD", "Pass INT", "Rush Yds", "Rush TD",
               "Receptions", "Rec Yds", "Rec TD", "Ret TD", "Fumb TD", "2PT", "Fumb Lost"]
    for stat in d_stats:
        defence[stat] = pd.to_numeric(defence[stat], errors='ignore')
    for stat in o_stats:
        offence[stat] = pd.to_numeric(offence[stat], errors='ignore')

    # Calculate Paddy Power points and add column
    print("WARNING: DEFENCE: Incomplete data so 'Blocked Punts/Kicks' and 'Extra Point Return' cannot be included")
    
    # DEFENCE
    # Add Paddy Points column (all but Points Allowed points)
    defence = defence.assign(Paddy=defence["Sacks"] + 2*defence["Saf"] +
                             2*defence["Fum Rec"] + 2*defence["Def INT"] + 6*defence["Def TD"])
    #  Now add Points Allowed points
    for i in range(0, len(defence.index)):
        if defence["Pts Allowed"][i] == 0:
            defence.iloc[i, defence.columns.get_loc("Paddy")] = defence.iloc[i, defence.columns.get_loc("Paddy")] + 10
        elif defence["Pts Allowed"][i] <= 6:
            defence.iloc[i, defence.columns.get_loc("Paddy")] = defence.iloc[i, defence.columns.get_loc("Paddy")] + 7
        elif defence["Pts Allowed"][i] <= 13:
            defence.iloc[i, defence.columns.get_loc("Paddy")] = defence.iloc[i, defence.columns.get_loc("Paddy")] + 4
        elif defence["Pts Allowed"][i] <= 20:
            defence.iloc[i, defence.columns.get_loc("Paddy")] = defence.iloc[i, defence.columns.get_loc("Paddy")] + 1
        elif defence["Pts Allowed"][i] <= 27:
            defence.iloc[i, defence.columns.get_loc("Paddy")] = defence.iloc[i, defence.columns.get_loc("Paddy")] + 0
        elif defence["Pts Allowed"][i] <= 34:
            defence.iloc[i, defence.columns.get_loc("Paddy")] = defence.iloc[i, defence.columns.get_loc("Paddy")] - 1
        else:
            defence.iloc[i, defence.columns.get_loc("Paddy")] = defence.iloc[i, defence.columns.get_loc("Paddy")] - 4


    # OFFENCE
    offence = offence.assign(Paddy=0.04*offence["Pass Yds"] + 4*offence["Pass TD"] -
                             offence["Pass INT"] + 0.1*offence["Rush Yds"] + 6*offence["Rush TD"] + 0.5*offence["Receptions"] 
                             + 0.1*offence["Rec Yds"] + 6*offence["Rec TD"] + 6*offence["Fumb TD"] + 6*offence["Ret TD"] - 2*offence["Fumb Lost"] + 2*offence["2PT"])

    # Save offence and defence data
    defence.to_csv('PaddyPoints/D_Week_' + str(week) + '.csv')
    offence.to_csv('PaddyPoints/O_Week_' + str(week) + '.csv')


def main():

    # Set weeks to add Paddy Points
    week_start = 1
    week_end = 7

    # Add Paddy Points
    for week in range(week_start, week_end+1):
        paddy_points(week)
        print('Paddy Points added for week ' + str(week))


if __name__ == "__main__":
    main()
