'''
This script produces multiplication factors for offence players, based on defence stats
'''

import pandas as pd
from filter import eligable_teams

# The stats will be normalised with the following 2019 values (from https://www.pro-football-reference.com/years/NFL/passing.htm)
stats = {"pass_yds" : 235, "pass_yds_att" : 7.2, "pass_td" : 1.6, "rush_yds" : 113, "rush_yds_carry" : 4.3, "rush_td" : 0.9, "INT" : 0.9}


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

    # Replace list of teams with their opponents
    for index, row in off_f.iterrows():
        for game in sched:
            if row["Team"] == game[0]:
                off_f.at[index, "Team"] = game[1]
            elif row["Team"] == game[1]:
                off_f.at[index, "Team"] = game[0]
    

    # Create new dataframe 
    df = pd.merge(off_f, defe_f, on="Team")
    # Keep only relevant columns
    df = df[["Team", "Pass Factor (O)", "Rush Factor (O)", "Pass Factor (D)", "Rush Factor (D)"]]
    
    # Add column with factor used to choose defence
    df["Defence Factor"] = c_DD["pass"]/(df["Pass Factor (D)"]*df["Pass Factor (O)"]) + c_DD["rush"]/(df["Rush Factor (D)"]*df["Rush Factor (O)"])

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
        for key, value in nfl_teams.items():
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

def main():
    
    print("ERROR: The factors functions should be called from process.py. The main function is only here for debugging")
    
    # Pick coefficient values
    c_D = {"pass_yds" : 0.25, "pass_yds_att" : 0.4, "pass_td" : 0.35, "rush_yds" : 0.4, "rush_yds_carry" : 0.3, "rush_td" : 0.3, "pass_yds_qb" : 0.3, "pass_yds_att_qb" : 0.3, "pass_td_qb" : 0.4, "INT" : 0.1}
    c_O = {"pass_yds" : 0.25, "pass_yds_att" : 0.3, "pass_td" : 0.45, "rush_yds" : 0.25, "rush_yds_carry" : 0.3, "rush_td" : 0.45}
    c_DD = {"pass" : 0.5, "rush" : 0.5, "fum" : 0, "INT" : 0, "sacks" : 0}
    schedule_week = 9

    defence_factors(c_D)
    offence_factors(c_O)
    defence_defence_factors(c_DD, schedule_week)

if __name__ == "__main__":
    main()