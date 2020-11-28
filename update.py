#!/usr/bin/python

'''
This script is designed for command-line use such that all the nfl data updates
'''
import sys, os
import scraper


# This function checks offence and defence (i.e. teams) player data is up-to-date
def update_player_data(upcoming_week):

    # Check if data already scraped, if not scrape it
    # Iterate over all previous weeks
    for week in range(1, upcoming_week):

        # Define what is to be scraped, Offence (O), Defence (D), Kicker (K)
        positions = ['O', 'D']
        for position in positions:

            # Scraped from NFL Fantasy website
            if position + "_Week_" + str(week) + ".csv" not in os.listdir("Scraped/NFL_Fantasy"):

                # Scrape missing week
                scraper.scrape_player_data(week, position)

    # Unfortunately scraped data from NFL Stats website must be completely scraped each time
    if "O_Week_" + str(upcoming_week-1) + ".csv" not in os.listdir("Scraped/NFL_Logs"):
        scraper.scrape_offence_players()


# Scrapes salary if not already 
def salary(upcoming_week):

    # Check not already been scraped
    if "FD_Salary_Week_" + str(upcoming_week) + ".csv" not in os.listdir("Scraped/Salary"):
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

    # Get weather
    scraper.scrape_weather(upcoming_week)

    # Update player data 
    update_player_data(upcoming_week)

    # Scrape all of the team defence stats
    scraper.scrape_defence_team()

    # Scrape all of the team offence stats
    scraper.scrape_offence_team()

    # Scrape depth chart and injuries
    scraper.scrape_depth_charts_injuries()

    # Scrape games played
    scraper.games_played()

    # Scrape salary data and schedule if not already
    salary(upcoming_week)
    schedule(upcoming_week)


if __name__ == "__main__":
    main()

