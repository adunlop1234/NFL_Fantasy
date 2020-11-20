'''
Adds useful metrics and sorts output data from filter.py
'''

import pandas as pd
import numpy as np
import itertools
from scraper import scrape_depth_charts_injuries
import sys, os
from collections import Counter
from progress.bar import IncrementalBar 

# Calculate and add Paddy Points columns to offence and defence
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
            offence.at[offence.index[offence["Player Name"] == name], "Team"] = offence_missing[name][2]
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
    defence.to_csv(os.path.join('Processed','PaddyPoints','D_Week_' + str(week) + '.csv'))
    offence.to_csv(os.path.join('Processed','PaddyPoints','O_Week_' + str(week) + '.csv'))


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


# Open summaries
def open_summaries():

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
        for count, name in enumerate(offence['Name'].tolist()):
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

    # Sort by descending average fantasy points
    defence = defence.sort_values(by='Predicted', ascending=False)

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
            # If havent played last 3 weeks, then only use overall average
            if pd.isnull(row["Avg Points (3 weeks)"]):
                pos.at[index, "Predicted"] = round(predict_O(row.Opp, position)*row["Avg Points"],2)
            else:
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

#! FACTORS

# The stats will be normalised with the following 2019 values (from https://www.pro-football-reference.com/years/NFL/passing.htm)
stats = {"pass_yds" : 235, "pass_yds_att" : 7.2, "pass_td" : 1.6, "rush_yds" : 113, "rush_yds_carry" : 4.3, "rush_td" : 0.9, "INT" : 0.9, "sacks" : 2.5, "fumbles" : 0.6}


# These defence factors are used for selecting offencive players
def defence_factors(c_D):

    # Read in Defence_Total
    df = pd.read_csv("Scraped/Data_NFL/Defence_Total.csv")
    # Add games played column
    df = games_played(df)

    # Add passing factor column
    df["Pass Factor (D)"] = (c_D["pass_yds"]*df["Pass Yds"]/stats["pass_yds"] + c_D["pass_td"]*df["Pass TD"]/stats["pass_td"])/df["Games"] + c_D["pass_yds_att"]*df["Pass Yds/Att"]/stats["pass_yds_att"]
    # Add rushing factor column
    df["Rush Factor (D)"] = (c_D["rush_yds"]*df["Rush Yds"]/stats["rush_yds"] + c_D["rush_td"]*df["Rush TD"]/stats["rush_td"])/df["Games"] + c_D["rush_yds_carry"]*df["Rush YPC"]/stats["rush_yds_carry"]
    # Add QB factor column
    df["QB Factor"] = (c_D["pass_yds_qb"]*df["Pass Yds"]/stats["pass_yds"] + c_D["pass_td_qb"]*df["Pass TD"]/stats["pass_td"] - c_D["INT"]*df["INT"]/stats["INT"])/df["Games"] + c_D["pass_yds_att_qb"]*df["Pass Yds/Att"]/stats["pass_yds_att"]

    # Now ensure mean of each 'factor' column is 1.0
    for factor in ["Pass Factor (D)", "Rush Factor (D)", "QB Factor"]:
        df[factor] = df[factor]/df[factor].mean()

    # Keep only factors columns
    columns = ["Team", "Pass Factor (D)", "Rush Factor (D)", "QB Factor"]
    df = df[columns]
    
    # Save defence with factors
    df.to_csv("Processed/Defence_Factors.csv")


def offence_factors(c_O):

    # Read in Offence_Total
    df = pd.read_csv("Scraped/Data_NFL/Offence_Total.csv")
    # Add games played column
    df = games_played(df)

    # Add passing factor column
    df["Pass Factor (O)"] = (c_O["pass_yds"]*df["Pass Yds"]/stats["pass_yds"] + c_O["pass_td"]*df["Pass TD"]/stats["pass_td"])/df["Games"] + c_O["pass_yds_att"]*df["Pass Yds/Att"]/stats["pass_yds_att"]
    # Add rushing factor column
    df["Rush Factor (O)"] = (c_O["rush_yds"]*df["Rush Yds"]/stats["rush_yds"] + c_O["rush_td"]*df["Rush TD"]/stats["rush_td"])/df["Games"] + c_O["rush_yds_carry"]*df["Rush YPC"]/stats["rush_yds_carry"]

    # Now ensure mean of each 'factor' column is 1.0
    for factor in ["Pass Factor (O)", "Rush Factor (O)"]:
        df[factor] = df[factor]/df[factor].mean()

    # Keep only factors columns
    columns = ["Team", "Pass Factor (O)", "Rush Factor (O)"]
    df = df[columns]
    
    # Save offence with factors
    df.to_csv("Processed/Offence_Factors.csv")

# These defence factors are used for selecting a defence
def defence_defence_factors(c_DD, schedule_week):

    # Read in Offence_Total
    off = pd.read_csv("Scraped/Data_NFL/Offence_Total.csv")
    # Read in Defence_Total
    defe = pd.read_csv("Scraped/Data_NFL/Defence_Total.csv")
    # Read in Offence factors
    off_f = pd.read_csv("Processed/Offence_Factors.csv")
    # Read in Defence factors
    defe_f = pd.read_csv("Processed/Defence_Factors.csv")

    # Add no. games played column
    # Open games_played.csv
    games = pd.read_csv("Scraped/Data_NFL/games_played.csv")
    games.columns = ["Team", "Games"]
    # Only keep last part name (e.g. New York Giants -> Giants)
    for index, row in games.iterrows():
        if row["Team"] == "Washington Football Team":
            games.at[index, "Team"] = "FootballTeam"
            continue
        games.at[index, "Team"] = row["Team"].split()[-1]
    # Create dictionary {Team : Games played, ...}
    games_ = pd.Series(games.Games.values,index=games.Team).to_dict()
    # Add extra column to defence with games played
    off.insert(loc=1, column = "Games", value="")
    defe.insert(loc=1, column = "Games", value="")
    for team, games_played in games_.items():
        off.at[off.index[off["Team"] == team][0], "Games"] = games_played
        defe.at[defe.index[defe["Team"] == team][0], "Games"] = games_played

    # Get list of eligable games
    eligable_games = list(eligable_teams(schedule_week).values())
    
    # Only keep eligable teams
    off = off[off_f.Team.isin(eligable_games)]
    defe = defe[off_f.Team.isin(eligable_games)]
    off_f = off_f[off_f.Team.isin(eligable_games)]
    defe_f = defe_f[defe_f.Team.isin(eligable_games)]

    # Read in the schedule
    sched = pd.read_csv("Scraped/Schedule/Schedule_Week_" + str(schedule_week) + ".csv")
    sched = sched[["Home", "Away"]]
    # Create list of games
    sched = sched.values.tolist()
    # Create dictionary of {NYG : New York Giants, etc.}
    ref = pd.read_csv('References/teams.csv')
    nfl_teams = pd.Series(ref.Name.values,index=ref.Abrev).to_dict()
    # Substitue schedule with full team name
    sched_ = []
    for game in sched:
        sched_.append([nfl_teams.get(item, item) for item in game])
    sched = sched_

    # Add column of opponent
    defe_f["Opponent"] = ""
    for index, row in defe_f.iterrows():
        for game in sched:
            if row["Team"] == game[0]:
                defe_f.at[index, "Opponent"] = game[1]
            elif row["Team"] == game[1]:
                defe_f.at[index, "Opponent"] = game[0]

    # Create new dataframe
    df = pd.merge(off_f, defe_f, left_on="Team", right_on="Opponent")
    # Keep only relevant columns
    df = df[["Team_y", "Opponent", "Pass Factor (O)", "Rush Factor (O)", "Pass Factor (D)", "Rush Factor (D)"]]
    df = df.rename(columns={"Team_y" : "Team"})

    # Add sacks column
    df["Sacks (D)"] = ""
    df["Sacks (O)"] = ""
    # Add fumbles column
    df["Fumbles (D)"] = ""
    df["Fumbles (O)"] = ""
    # Add interception column
    df["INT (D)"] = ""
    df["INT (O)"] = ""
    # Iterate over Defence_Total.csv
    for index, row in defe.iterrows():
        # Iterate over newly created dataframe 
        for i, r in df.iterrows():
            # Same team
            if row["Team"] in r["Team"]:
                df.at[i, "Sacks (D)"] = row["Sacks"] / row["Games"]
                df.at[i, "Fumbles (D)"] = (row["Rec FUM"] + row["Rush FUM"]) / row["Games"]
                df.at[i, "INT (D)"] = row["INT"] / row["Games"]
            # Need to handle WSH manually
            if r["Team"] == "Washington Football Team" and row["Team"] == "FootballTeam":
                df.at[i, "Sacks (D)"] = row["Sacks"] / row["Games"]
                df.at[i, "Fumbles (D)"] = (row["Rec FUM"] + row["Rush FUM"]) / row["Games"]
                df.at[i, "INT (D)"] = row["INT"] / row["Games"]
    # Sacks, Fumbles, INTs given up by offence they are playing
    # Iterate over Offence_Total.csv
    for index, row in off.iterrows():
        # Iterate over newly created dataframe 
        for i, r in df.iterrows():
            # Same team
            if row["Team"] in r["Opponent"]:
                df.at[i, "Sacks (O)"] = row["Sacks"] / row["Games"]
                df.at[i, "Fumbles (O)"] = (row["Rec FUM"] + row["Rush FUM"]) / row["Games"]
                df.at[i, "INT (O)"] = row["Pass INT"] / row["Games"]
            # Need to handle WSH manually
            if r["Opponent"] == "Washington Football Team" and row["Team"] == "FootballTeam":
                df.at[i, "Sacks (O)"] = row["Sacks"] / row["Games"]
                df.at[i, "Fumbles (O)"] = (row["Rec FUM"] + row["Rush FUM"]) / row["Games"]
                df.at[i, "INT (O)"] = row["Pass INT"] / row["Games"]

    # Add column with factor used to choose defence
    df["Defence Factor"] = c_DD["pass"]/((df["Pass Factor (D)"]*df["Pass Factor (O)"]) ** (0.5)) + c_DD["rush"]/((df["Rush Factor (D)"]*df["Rush Factor (O)"]) ** (0.5)) + c_DD["sacks"]*((df["Sacks (D)"]*df["Sacks (O)"]) ** (0.5))/stats["sacks"] + c_DD["fum"]*((df["Fumbles (D)"]*df["Fumbles (O)"]) ** (0.5))/stats["fumbles"] + c_DD["INT"]*((df["INT (D)"]*df["INT (O)"]) ** (0.5))/stats["INT"]

    # Only keep relevant columns
    df = df[["Team", "Defence Factor"]]

    # Now ensure mean of 'factor' column is 1.0
    df["Defence Factor"] = df["Defence Factor"]/df["Defence Factor"].mean()

    # Now take square root of each value
    df["Defence Factor"] = df["Defence Factor"] ** (0.5)
    
    # Save Defence with factors
    df.to_csv("Processed/Defence_Defence_Factors.csv")

    
# Add column based on games played
def games_played(defence):

    # Create dictionary of {NYG : New York Giants, etc.}
    ref = pd.read_csv('References/teams.csv')
    nfl_teams = pd.Series(ref.Name.values,index=ref.Abrev).to_dict()
    # Replace short Team name with full name (e.g. Giants with New York Giants)
    for index, row in defence.iterrows(): 
        for value in nfl_teams.values():
            if row["Team"] in value:
                defence.at[index, "Team"] = value
            if row["Team"] == "FootballTeam":
                defence.at[index, "Team"] = "Washington Football Team"

    # Open games_played.csv
    games = pd.read_csv("Scraped/Data_NFL/games_played.csv")
    games.columns = ["Team", "Games"]

    # Create dictionary {Team : Games played, ...}
    games_ = pd.Series(games.Games.values,index=games.Team).to_dict()

    # Add extra column to defence with games played
    defence.insert(loc=1, column = "Games", value="")

    for team, games_played in games_.items():
        defence.at[defence.index[defence["Team"] == team][0], "Games"] = games_played

    return defence

def define_depth_chart(upcoming_week):

    """
    Function that creates a depth chart for each team based on the number of receptions per game
    for wide recievers and tight ends, and number of rushing attempts per game for running backs.
    The injury status is then reviewed to check if any starters or number 2s are not playing and
    file written to suggest players that will recieve a boost.
    """

    # Define the rank of the players at the position by the number of rec/game, rush/game etc.
    # Check whether each player played for the given week by seeing if they have an entry
    #  

    # Calculate average plays per game

    # Initialise the output arrays and define stats for each position
    positions = ['QB', 'RB', 'WR', 'TE']
    stats = ['PASS ATT', 'RUSH ATT', 'REC', 'REC']
    pos_dicts = {
        position : pd.DataFrame(columns=['Name', 'Team', 'Total Stat', 'Games Played'])
        for position in positions
    }

    # Detail progress for depth chart
    bar = IncrementalBar('Defining Depth Chart', max = upcoming_week-1, suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')

    # Loop over each week to total the relevant stat
    for week in range(1, upcoming_week):

        # Read in all offence data
        offence_data = pd.read_csv(os.path.join('Processed', 'PaddyPoints', 'O_Week_' + str(week) + '.csv'))

        # Loop over each position and their corresponding stat
        for position, stat in zip(positions, stats):

            # Extract all rows specific to current position
            pos_data = offence_data[offence_data['Position'] == position]

            # Loop over each player in this position
            for index, row in pos_data.iterrows():

                # If the player has already played this season add to their information
                if row.Name in list(pos_dicts[position].Name):
                    ids = pos_dicts[position].Name == row.Name
                    pos_dicts[position].loc[ids, ('Total Stat')] += row[stat]
                    pos_dicts[position].loc[ids, ('Games Played')] += 1

                # If the player hasn't played yet, add their information
                else:
                    insert_dict = {
                        'Name' : row.Name,
                        'Team' : row.Team,
                        'Total Stat' : row[stat],
                        'Games Played' : 1
                    }
                    pos_dicts[position] = pos_dicts[position].append(insert_dict, ignore_index=True)

        # Update progress
        bar.next()

    # Finish progress
    bar.finish()

    # Find the average stat per player per position
    for position in positions:
        pos_dicts[position]['Average'] = pos_dicts[position]['Total Stat'] / pos_dicts[position]['Games Played']
        pos_dicts[position] = pos_dicts[position].sort_values(by=['Team', 'Average'], ascending = False)

    # Read in current injury status and report if the main or secondary player is not playing
    injuries = pd.read_csv(os.path.join('Scraped', 'Injury_Status.csv'))
    
    # Read in the schedule to determine defence boosts
    schedule = pd.read_csv(os.path.join('Scraped', 'Schedule', 'Schedule_Week_' + str(upcoming_week) + '.csv'))

    # Open the file for the depth chart report
    f = open("Depth_Chart_Report.txt", "w")

    # Loop over each team
    teams = list(pos_dicts['RB'].Team.unique())
    teams.reverse()
    for team in teams:

        # Skip if the team name isn't legit
        if team in [np.nan, '0']:
            continue

        # Print the team of relevance
        f.write('--------------------------------\n')
        f.write('Injury Report for ' + team + '\n')

        # Extract injuries just for specific team of interest
        team_injuries = injuries[injuries['Team'] == team]

        # Loop over each position
        for position in ['QB', 'WR', 'RB', 'TE']:

            # Initialise the injured players
            injured_players = dict()

            # Extract the depth chart for the current team and position
            pos_depth_chart = pos_dicts[position][pos_dicts[position].Team == team]
            
            # Extract the injuries for the position of the team, only look at players who aren't playing
            position_injuries = team_injuries[team_injuries['Position'] == position]
            position_injuries = position_injuries[position_injuries['Status'] != 'D']
            position_injuries = position_injuries[position_injuries['Status'] != 'Q']

            # Loop over each player in the injury list to check if they're in the depth chart for current team/position
            for player in list(position_injuries[position_injuries['Team'] == team].Name):
                if player in list(pos_depth_chart.Name):
                    injured_players[list(pos_depth_chart.Name).index(player)+1] = player

            if len(injured_players):
                for rank, player in injured_players.items():

                    # Inform when the starter and number 2 at the position are out and suggest number 3
                    if rank == 1 and (2 in injured_players.keys()):

                        f.write(position + str(1) + ' (' + player + ') and ' + position + str(2) + ' (' + injured_players[2] + ') are out. Consider ' + position + str(3) + ' (' + list(pos_depth_chart.Name)[2] + ').\n')

                    # Inform when the starter is out and suggest number 2
                    elif rank == 1 and (2 not in injured_players.keys()):

                        f.write(position + str(1) + ' (' + player + ') is out. Consider ' + position + str(2) + ' (' + list(pos_depth_chart.Name)[1] + ').\n')

                    # Inform when the number 2 is out and expect the starter to get more targets
                    elif rank == 2 and (1 not in injured_players.keys()):

                        f.write(position + str(2) + ' (' + player + ') is out. Consider ' + position + str(1) + ' (' + list(pos_depth_chart.Name)[0] + ') as they should have more attempts/targets.\n')
    
                    # If the QB is out suggest picking the defence
                    if position == 'QB' and rank == 1:
                        
                        if (schedule['Home'] == team).any():
                            opponent = schedule.loc[schedule['Home'] == team, ('Away')]
                        elif (schedule['Away'] == team).any():
                            opponent = schedule.loc[schedule['Away'] == team, ('Home')]
                        else:
                            continue
                        
                        f.write('QB1 (' + player + ') is out. The ' + str(opponent.values[0]) + ' defence will get a boost.\n')

    # Close the file
    f.close()