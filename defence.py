'''
This script produces multiplication factors for offence players, based on defence stats
'''

import pandas as pd


def defence_factors(c_pass_yds, c_pass_yds_att, c_pass_td, c_rush_yds, c_rush_yds_carry, c_rush_td, c_pass_yds_qb, c_pass_yds_att_qb, c_pass_td_qb, c_INT):

    # The stats will be normalised with the following 2019 values (from https://www.pro-football-reference.com/years/NFL/passing.htm)
    
    # Passing
    pass_yds = 235
    pass_yds_att = 7.2
    pass_td = 1.6

    # Rushing
    rush_yds = 113
    rush_yds_carry = 4.3
    rush_td = 0.9

    # QB
    INT = 0.9


    # Read in Defence_Total
    df = pd.read_csv("Scraped/Data_NFL/Defence_Total.csv")
    # Add games played column
    df = games_played(df)

    # Add passing factor column
    df["Passing Factor"] = (c_pass_yds*df["Pass Yds"]/pass_yds + c_pass_td*df["Pass TD"]/pass_td)/df["Games"] + c_pass_yds_att*df["Pass Yds/Att"]/pass_yds_att
    # Add rushing factor column
    df["Rushing Factor"] = (c_rush_yds*df["Rush Yds"]/rush_yds + c_rush_td*df["Rush TD"]/rush_td)/df["Games"] + c_rush_yds_carry*df["Rush YPC"]/rush_yds_carry
    # Add QB factor column
    df["QB Factor"] = (c_pass_yds_qb*df["Pass Yds"]/pass_yds + c_pass_td_qb*df["Pass TD"]/pass_td - c_INT*df["INT"]/INT)/df["Games"] + c_pass_yds_att_qb*df["Pass Yds/Att"]/pass_yds_att 

    # Now ensure mean of each 'factor' column is 1.0
    for factor in ["Passing Factor", "Rushing Factor", "QB Factor"]:
        df[factor] = df[factor]/df[factor].mean()

    # Keep only factors columns
    columns = ["Team", "Passing Factor", "Rushing Factor", "QB Factor"]
    df = df[columns]
    
    # Save defence with factors
    df.to_csv("Output/Processed/Defence_Factors.csv")
 
    
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
    
    # Pick coefficient values
    c_pass_yds = 0.25
    c_pass_yds_att = 0.4
    c_pass_td = 0.35
    c_rush_yds = 0.4
    c_rush_yds_carry = 0.3
    c_rush_td = 0.3
    c_pass_yds_qb = 0.4
    c_pass_yds_att_qb = 0.3
    c_pass_td_qb = 0.3
    c_INT = 0.1

    defence_factors(c_pass_yds, c_pass_yds_att, c_pass_td, c_rush_yds, c_rush_yds_carry, c_rush_td, c_pass_yds_qb, c_pass_yds_att_qb, c_pass_td_qb, c_INT)


if __name__ == "__main__":
    main()