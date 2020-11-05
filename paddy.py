'''
Appends Paddy Power Points column to scraped data
'''

import pandas as pd
import sys

def paddy_points(week):

    # Read csv into a dataframe
    defence = pd.read_csv('Scraped/Statistics/D_Week_' + str(week) + '.csv')
    offence = pd.read_csv('Scraped/Data_NFL/O_Week_' + str(week) + '.csv')

    # For defence only, replace '-' with 0
    defence = defence.replace('-', 0)
    # Convert datatypes
    defence = defence.astype({"Sacks" : 'int64', "Def INT" : 'int64', "Fum Rec" : 'int64', "Saf" : 'int64', "Def TD" : 'int64', "Def 2pt Ret" : 'int64', "Def Ret TD" : 'int64', "Pts Allowed" : 'int64'})

    # Calculate Paddy Power points and add column

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
    # Drop players who did not play given week
    offence = offence.dropna(axis=0, thresh=8)
    # Need to add in '2pt' and 'Ret TD' columns using original scraper (from Fantasy NFL rather than player logs)
    # Inexplicably the scraped data from log is missing some player's teams. Take this from Fantasy NFL
    # Open 'fantasy scraped' datasets
    offence_fantasy = pd.read_csv('Scraped/Statistics/O_Week_' + str(week) + '.csv')
    # Put missing data into dict
    temp1 = [x if x not in '-' else 0 for x in offence_fantasy["Ret TD"].tolist()]
    temp2 = [x if x not in '-' else 0 for x in offence_fantasy["Ret TD"].tolist()]
    temp3 = [team for team in offence_fantasy["Team"].tolist()]
    offence_missing = dict(zip(offence_fantasy["Name"].tolist(), list(zip(temp1, temp2, temp3))))
    
    # Remove Team column values
    offence = offence.assign(Team='')
    
    # Add columns to offence
    offence["2PT"] = 0
    offence["RET TD"] = 0
    for name in offence["Player Name"].tolist():
        try:
            offence.at[offence.index[offence["Player Name"] == name], "RET TD"] = offence_missing[name][0]
            offence.at[offence.index[offence["Player Name"] == name], "2PT"] = offence_missing[name][1]
            # Need to change LA to LAR 
            offence.at[offence.index[offence["Player Name"] == name], "Team"] = offence_missing[name][2] if offence_missing[name][2] != "LA" else "LAR"
        except KeyError:
            print(name + " is in NFL Log dataset but not NFL Fantasy dataset")
            continue


    # Fill empty values with 0 and convert datatypes
    offence = offence.fillna(0)    
    offence = offence.astype({'2PT' : 'float64', 'RET TD' : 'float64'})
    
    #! Missing 'Fumb TD' in new dataset, but believe will be included in Rush TD stats
    offence = offence.assign(Paddy=0.04*offence["PASS YDS"] + 4*offence["PASS TD"] -
                             offence["PASS INT"] + 0.1*offence["RUSH YDS"] + 6*offence["RUSH TD"] + 0.5*offence["REC"] 
                             + 0.1*offence["REC YDS"] + 6*offence["REC TD"] + 6*offence["RET TD"] - 2*offence["FUM LOST"] + 2*offence["2PT"])
    # Rename Name column
    offence = offence.rename(columns={"Player Name" : "Name"})


    # Save offence and defence data
    defence.to_csv('Processed/PaddyPoints/D_Week_' + str(week) + '.csv')
    offence.to_csv('Processed/PaddyPoints/O_Week_' + str(week) + '.csv')


def main():

    # Set weeks to add Paddy Points
    week_start = 1
    week_end = 8

    print("WARNING: DEFENCE: Incomplete data so 'Blocked Punts/Kicks' and 'Extra Point Return' cannot be included")

    # Add Paddy Points
    for week in range(week_start, week_end+1):
        paddy_points(week)
        print('Paddy Points added for week ' + str(week))


if __name__ == "__main__":
    main()
