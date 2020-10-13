# Create a csv file for all offence for week specified in 'main'

import requests
from prettyprinter import pprint
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd


def scrape_data(week):

    # Set the week, season, position
    data_in = dict()
    data_in['position'] = 0
    data_in['week'] = week
    data_in['offset'] = 1

    # Initialise output variable
    list_out = list()

    # Initialise the pandas dataframe header
    columns = ["Name", "Position", "Team", "Pass Yds", "Pass TD", "Pass INT", "Rush Yds", "Rush TD",
               "Receptions", "Rec Yds", "Rec TD", "Ret TD", "Fumb TD", "2PT", "Fumb Lost", "Points Total"]

    # Loop over each page
    while True:

        # Create the request
        URL = 'https://fantasy.nfl.com/research/players?offset=' + str(data_in['offset']) + '&position=' + str(
            data_in['position']) + '&sort=pts&statCategory=stats&statSeason=2020&statType=weekStats&statWeek=' + str(data_in['week'])
        page = requests.get(URL, allow_redirects=True)

        # Parse the html using soup
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find the relevant section and rows
        results = soup.find(id='researchPlayers')
        rows = results.find_all('tr', class_=re.compile('player-'))

        # If total players % 25 = 0 (i.e. final page had exactly 25 players)
        if len(rows) == 0:
            break

        # Iterate against each player listed in the table
        for row in rows:

            # Store all player data in dictionary
            data_out = dict()

            # Name
            data_out['Name'] = row.find('a').getText()

            # Position and Team
            positionTeam = row.find('em').getText().split(' - ')
            if len(positionTeam) > 1:
                data_out['Position'] = positionTeam[0]
                data_out['Team'] = positionTeam[1]
            else:
                data_out['Position'] = positionTeam[0]
                data_out['Team'] = None

            # Opponent
            data_out['Opponent'] = row.find(class_='playerOpponent').getText()

            # Pass Yds
            data_out['Pass Yds'] = row.find(
                class_='stat stat_5 numeric').getText()

            # Pass TD
            data_out['Pass TD'] = row.find(
                class_='stat stat_6 numeric').getText()

            # Pass INT
            data_out['Pass INT'] = row.find(
                class_='stat stat_7 numeric').getText()

            # Rush Yds
            data_out['Rush Yds'] = row.find(
                class_='stat stat_14 numeric').getText()

            # Rush TD
            data_out['Rush TD'] = row.find(
                class_='stat stat_15 numeric').getText()

            # Rec Receptions
            data_out['Receptions'] = row.find(
                class_='stat stat_20 numeric').getText()

            # Rec Yds
            data_out['Rec Yds'] = row.find(
                class_='stat stat_21 numeric').getText()

            # Rec TD
            data_out['Rec TD'] = row.find(
                class_='stat stat_22 numeric').getText()

            # Ret TD
            data_out['Ret TD'] = row.find(
                class_='stat stat_28 numeric').getText()

            # Misc FumbTD
            data_out['Fumb TD'] = row.find(
                class_='stat stat_29 numeric').getText()

            # Misc 2PT
            data_out['2PT'] = row.find(class_='stat stat_32 numeric').getText()

            # Fum Lost
            data_out['Fum Lost'] = row.find(
                class_='stat stat_30 numeric').getText()

            # Points
            data_out['Points Total'] = row.find(
                class_=re.compile('last')).getText()

            # Add the information to the dataframe
            list_out.append(data_out)

        # Break if there are less than 25 table rows
        if len(rows) < 25:
            break
        else:
            data_in['offset'] += 25

        # Print progress
        print('Completed ' + str(round(data_in['offset']*100/1027, 1)) + '%')

    df = pd.DataFrame(list_out, columns=columns)
    df.to_csv('Week' + str(data_in['week']) + '.csv')


def main():
    # Set weeks to scrape
    week_start = 1
    week_end = 5
    # Scrape data
    for week in range(week_start, week_end+1):
        scrape_data(week)
        print('Completed Week ' + str(week))
    

if __name__ == "__main__":
    main()
