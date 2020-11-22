#!/usr/bin/python

'''
This script is designed for command-line use to develop the scraped data into useful data
'''
import sys, os
import scraper, process

# Adds Paddy Points column if not already
def paddy_column(upcoming_week):
    
    print("WARNING: DEFENCE: Incomplete data so 'Blocked Punts/Kicks' and 'Extra Point Return' cannot be included")

    # Iterate over all past weeks
    for week in range(1, upcoming_week):

        # Check not already been added
        if "O_Week_" + str(week) + ".csv" not in os.listdir("Processed/PaddyPoints"):
            process.paddy_points(week)

# Collate player and team data, filtered by the eligable games
def collate(upcoming_week):

    # Grab eligable teams
    teams = process.eligable_teams(upcoming_week)

    # Output collated data
    process.collate_D(upcoming_week, teams)
    process.collate_O(upcoming_week, teams)

# Produce the output for each player type (QB WR RB TE DEF)
def players_output(upcoming_week):

    # Open summary files
    defence, offence = process.open_summaries()

    # Add opponent column
    defence, offence = process.opponent(offence, defence, upcoming_week)

    # Add average columns
    defence, offence = process.average_pts(defence, offence)

    # Add salary column
    defence, offence = process.salary(defence, offence, upcoming_week)

    # Add injury column
    offence = process.injury(offence)

    # Save seperate outputs for each position
    process.position(offence, upcoming_week)

    defence = process.predict_D(defence)

    # Save processed version of defence
    defence.to_csv(os.path.join('Output', 'DEF.csv'))




def main():

    # Check correct command-line usuage
    if len(sys.argv) != 2:
        print("USUAGE: python develop.py upcoming-week")
        exit(1)

    # Set upcoming_week
    upcoming_week = int(sys.argv[1])

    # Add Paddy Points column if not already
    paddy_column(upcoming_week)

    # Collate player and team data, filtered by the eligable games
    collate(upcoming_week)

    # Ensure injuries up-to-date
    scraper.scrape_depth_charts_injuries()

    # Get weather
    scraper.scrape_weather(upcoming_week)
    
    # Update Factors
    print("WARNING: Currenly using hard-coded coefficients for calculation of factors")
    c_D = {"pass_yds" : 0.25, "pass_yds_att" : 0.4, "pass_td" : 0.35, "rush_yds" : 0.4, "rush_yds_carry" : 0.3, "rush_td" : 0.3, "pass_yds_qb" : 0.4, "pass_yds_att_qb" : 0.3, "pass_td_qb" : 0.3, "INT" : 0.1}
    c_O = {"pass_yds" : 0.25, "pass_yds_att" : 0.3, "pass_td" : 0.45, "rush_yds" : 0.25, "rush_yds_carry" : 0.3, "rush_td" : 0.45}
    c_DD = {"pass" : 0.2, "rush" : 0.2, "fum" : 0.2, "INT" : 0.2, "sacks" : 0.2}
    process.defence_factors(c_D)
    process.offence_factors(c_O)
    process.defence_defence_factors(c_DD, upcoming_week)

    # Produce the output for each player type (QB WR RB TE DEF)
    players_output(upcoming_week)

    # Check depth chart
    process.define_depth_chart(upcoming_week)



if __name__ == "__main__":
    main()

