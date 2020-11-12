#!/usr/bin/python

'''
This script is designed for command-line use such that all the nfl data updates
'''
import sys, os
import scraper_NFL, scraper


# This function checks offence and defence (i.e. teams) player data is up-to-date
def update_player_data(upcoming_week):

    # Check if data already scraped, if not scrape it
    # Define what is to be scraped, Offence (O), Defence (D), Kicker (K)
    positions = ['O', 'D']
    for position in positions:

        # Iterate over all previous weeks
        for week in range(1, upcoming_week):

            # Scraped from NFL Fantasy website
            if "O_Week_" + str(week) + ".csv" not in os.listdir("Scraped/Statistics"):

                # Scrape missing week
                scraper.scrape_player_data(week, position)

    # Unfortunately scraped data from NFL Stats website must be completely scraped each time
    if "O_Week_" + str(upcoming_week-1) + ".csv" not in os.listdir("Scraped/Data_NFL"):
        scraper_NFL.scrape_offence_players()

# This function updates data which the latest is always wanted
def latest_data():

    # Scrape all of the team defence stats
    scraper_NFL.scrape_defence_team()

    # Scrape all of the team offence stats
    scraper_NFL.scrape_offence_team()

    # Scrape depth chart and injuries
    scraper.scrape_depth_charts_injuries()

    # Scrape games played
    scraper_NFL.games_played()

# Scrapes salary if not already 
def salary(upcoming_week):

    # Check not already been scraped
    if "FD_Salary_Week_" + str(upcoming_week) + ".csv" not in os.listdir("Scraped/Statistics"):
        # Scrape the salary data for the upcoming week    
        scraper.scrape_salary()

# Scrapes schedule if not already
def schedule(upcoming_week):

    # Check not already been scraped
    if "Schedule_Week_" + str(upcoming_week) + ".csv" not in os.listdir("Scraped/Schedule"):
        # Scrape schedule data for the upcoming week
        scraper.scrape_schedule(upcoming_week)
    

def main():

    # Check correct command-line usuage
    if len(sys.argv) != 2:
        print("USUAGE: python update.py upcoming-week")
        exit(1)

    # Set upcoming_week
    upcoming_week = int(sys.argv[1])

    # Update player data 
    update_player_data(upcoming_week)

    # Update data where the latest is always wanted
    latest_data()

    # Scrape salary data and schedule if not already
    salary(upcoming_week)
    schedule(upcoming_week)


if __name__ == "__main__":
    main()

