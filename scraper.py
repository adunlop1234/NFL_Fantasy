'''
Set of scripts that scrapes all weekly offence, kicker and 
defence player data from https://fantasy.nfl.com.
'''

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


def scrape_data(week, player_type):

    # Initialise the input data array with week and offset
    data_in = dict()
    data_in['week'] = week
    data_in['offset'] = 1

    # Define the input data for the URL for the position
    if player_type == 'O':
        data_in['position'] = 0
    elif player_type == 'K':
        data_in['position'] = 7
    elif player_type == 'D':
        data_in['position'] = 8


    # Initialise output variable
    list_out = list()

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

        # Find the number of table rows in total
        total_rows = int(results.find(
            'div', class_='paginationWrap').getText().split('of')[1].split(' ')[1])

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
            data_out['Opponent'] = row.find(
                class_='playerOpponent').getText()

            # Find stats that are specific to the player position
            data_out = return_stats(data_in, data_out, row)

            # Points Total
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
        print('Completed ' + str(round(data_in['offset']*100/total_rows, 1)) + '%')

    # Define the columns for the appropriate player type
    if data_in['position'] == 0:
        columns = ["Name", "Position", "Team", "Pass Yds", "Pass TD", "Pass INT", "Rush Yds", "Rush TD",
                   "Receptions", "Rec Yds", "Rec TD", "Ret TD", "Fumb TD", "2PT", "Fumb Lost", "Points Total"]
    
    elif data_in['position'] == 7:
        columns = ["Name", "Position", "Team", "PAT Made", "FG 0-19", "FG 20-29", "FG 30-39", "FG 40-49",
                   "FG 50+", "Points Total"]
    
    elif data_in['position'] == 8:
        columns = ["Team", "Position", 'Sacks', "Def INT", "Fum Rec", "Saf", "Def TD", "Def 2pt Ret", "Def Ret TD",
                   "Pts Allowed", "Points Total"]

    # Create data frame with the columns define and data for the specified week and player type
    df = pd.DataFrame(list_out, columns=columns)
    df.to_csv(str(player_type) + '_Week_' + str(data_in['week']) + '.csv')

# Function dedicated to returning the specific stats for each position
def return_stats(data_in, data_out, row):

    # Stats specific to all offence
    if data_in['position'] == 0:

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
        data_out['2PT'] = row.find(
            class_='stat stat_32 numeric').getText()

        # Fum Lost
        data_out['Fum Lost'] = row.find(
            class_='stat stat_30 numeric').getText()

        # Points
        data_out['Points Total'] = row.find(
            class_=re.compile('last')).getText()

    # Stats specific to kickers
    elif data_in['position'] == 7:

        # PAT Made
        data_out['PAT Made'] = row.find(
            class_='stat stat_33 numeric').getText()

        # FG 0-19
        data_out['FG 0-19'] = row.find(
            class_='stat stat_35 numeric').getText()

        # FG 20-29
        data_out['FG 20-29'] = row.find(
            class_='stat stat_36 numeric').getText()

        # FG 30-39
        data_out['FG 30-39'] = row.find(
            class_='stat stat_37 numeric').getText()

        # FG 40-49
        data_out['FG 40-49'] = row.find(
            class_='stat stat_38 numeric').getText()

        # FG 50-59
        data_out['FG 50+'] = row.find(
            class_='stat stat_39 numeric').getText()

    # Stats specific to defence
    elif data_in['position'] == 8:

        # Sacks
        data_out['Sacks'] = row.find(
            class_='stat stat_45 numeric').getText()

        # INT
        data_out['Def INT'] = row.find(
            class_='stat stat_46 numeric').getText()

        # Fumble Recoveries
        data_out['Fum Rec'] = row.find(
            class_='stat stat_47 numeric').getText()

        # Safeties
        data_out['Saf'] = row.find(
            class_='stat stat_49 numeric').getText()

        # TD
        data_out['Def TD'] = row.find(
            class_='stat stat_50 numeric').getText()

        # Def 2pt Ret
        data_out['Def 2pt Ret'] = row.find(
            class_='stat stat_93 numeric').getText()

        # Ret TD
        data_out['Def Ret TD'] = row.find(
            class_='stat stat_53 numeric').getText()

        # Pts Allowed
        data_out['Pts Allowed'] = row.find(
            class_='stat stat_54 numeric').getText()

    # Return the output data array now filled
    return data_out

def main():
    
    # Set weeks to scrape
    week_start = 1
    week_end = 5

    # Define what is to be scraped, Offence (O), Defence (D), Kicker (K)
    player_types = ["D", "O", "K"]

    # Scrape data
    for position in player_types:
        for week in range(week_start, week_end+1):
            scrape_data(week, position)
            print(str(position) + ' Data exported for week ' + str(week))
    

if __name__ == "__main__":
    main()
