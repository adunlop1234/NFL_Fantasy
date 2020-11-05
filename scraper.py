'''
Set of scripts that scrapes all weekly offence, kicker and 
defence player data from https://fantasy.nfl.com.
'''

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sys
import datetime


def scrape_player_data(week, player_type):

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
        columns = ["Name", "Position", 'Sacks', "Def INT", "Fum Rec", "Saf", "Def TD", "Def 2pt Ret", "Def Ret TD",
                   "Pts Allowed", "Points Total"]

    # Create data frame with the columns define and data for the specified week and player type
    df = pd.DataFrame(list_out, columns=columns)
    df.to_csv('Scraped/Statistics/' + str(player_type) + '_Week_' + str(data_in['week']) + '.csv')

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

# Function to return the schedule for a given week in the future. 
# Previous weeks don't work or weeks with undefined times.
def scrape_schedule(week):

    # Define the URL for the week in question
    URL = 'https://www.espn.co.uk/nfl/fixtures/_/week/1'.replace('week/1', 'week/' + str(week))

    # Get page
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Define the headings
    columns = ['Home', 'Away', 'Day', 'Time']

    # Initialise the dataframe
    df = pd.DataFrame(columns = columns)

    # Find the rows
    rows = soup.find_all('tr', class_=re.compile('^(even|odd)$'))

    # Scrape home, away, day, time, early, mid, late, mnf, tnf
    for row in rows[:-1]:
        
        # Find the home and away team abbreviation
        teams = [team.getText() for team in row.find_all('abbr')]
        home, away = teams
        
        # Identify the datatime and split into day and time - all in GMT
        try:
            date, time = row.find('td', {'data-behavior' : 'date_time'})['data-date'].split('T')
            year, month, day = date.split('-')
            day = datetime.date(int(year), int(month), int(day)).strftime("%a")
            time = time.split('Z')[0]
        except TypeError:
            print('WARNING: Scraping schedule after the initial game has been played.')
            day = 'N/A'
            time = 'N/A'

        # Pandas dict for entry
        new_dict = {'Home' : home,
                    'Away' : away,
                    'Day' : day,
                    'Time' : time}

        # Add to the pandas dataframe
        df = df.append(new_dict, ignore_index = True)

    # Write csv output file
    df.to_csv('Scraped/Schedule/Schedule_Week_' + str(week) + '.csv')

    return df

def scrape_injuries():

    # Initialise the dataframe
    columns = ['Name', 'Team','Position', 'Status']
    df = pd.DataFrame(columns=columns)

    # Define the URL for the week in question
    URL = 'https://www.cbssports.com/nfl/injuries/'

    # Get page
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get list of teams
    # Get all h4
    headings = soup.find_all('h4')
    teams = []
    for heading in headings:
        # Add team name (only keeping last word, e.g. Ram)
        teams.append([item for item in heading.find_all('a')][1].getText().split()[-1])

    # Tidy up team names with abreviation form
    # Create dictionary of {New York Giants : NYG, etc.}
    ref = pd.read_csv('References/teams.csv')
    nfl_teams = pd.Series(ref.Abrev.values,index=ref.Name).to_dict()

    # Convert the list of team names into the abreviation form
    teams_abrev = []
    for team in teams:
        for full in nfl_teams.keys():
            if team in full:
                teams_abrev.append(nfl_teams[full])    

    # Get all table rows
    rows = soup.find_all('tr')

    # Loop over rows
    count = 0
    team = teams_abrev[0]
    for row in rows:

        # Get list of table data in given row
        items = row.find_all('td')

        # Header row means next team
        if len(items) == 0:
            team = teams_abrev[count]
            count += 1
            continue

        # Get player name
        name = [item.find_all('a') for item in items][0][1].getText().strip()

        # Get position
        position = [item.getText().strip() for item in items][1]

        # Get Status
        status_text = [item.getText().strip() for item in items][4]
        status = status_text

        # Search Status comment for status
        if "IR" in status_text:
            status = "IR"
        elif "questionable" in status_text.lower():
            status = "Q"
        elif "inactive" in status_text.lower():
            status = "inactive"
        elif "doubtful" in status_text.lower():
            status = "D"
        elif "out" in status_text.lower():
            status = "O"

        # Set the input to the dataframe
        input_data = dict(zip(columns, [name, team, position, status]))

        # Add to the pandas dataframe
        df = df.append(input_data, ignore_index = True)

    # Write csv output file
    df.to_csv('Scraped/Injury_Status.csv')

    return df



def scrape_salary():

    # Initialise the dataframe
    columns = ['Name', 'Team', 'Position', 'Salary']
    df = pd.DataFrame(columns=columns)

    # Define the URL for the week in question
    URL = 'https://www.fantasypros.com/daily-fantasy/nfl/fanduel-salary-changes.php'

    # Get page
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get the week
    week = soup.find('h1').getText().split(' ')[-1]
    
    # Get all table rows
    rows = soup.find_all('tr', class_=re.compile(r'RB|QB|TE|WR|DST'))
    
    for row in rows:

        # Get all player info (name, team, position) from initial table entry
        player_info = row.find('td', style=re.compile(r'white-space'))
        name = player_info.find('a', href=re.compile(r'/nfl/')).getText()
        team = re.split(' |\)|\(', player_info.find('small').getText())[1]
        position = re.split(' |\)|\(', player_info.find('small').getText())[-2]

        # Get salary info
        salary = row.find('td', class_=re.compile('salary'))['data-salary']

        # Set the input to the dataframe
        input_data = dict(zip(columns, [name, team, position, salary]))

        # Add to the pandas dataframe
        df = df.append(input_data, ignore_index = True)


    # Sort by salary
    df['Salary'] = pd.to_numeric(df['Salary'], errors='ignore')
    df = df.sort_values(by='Salary', ascending=False)

    # Write csv output file
    df.to_csv('Scraped/Statistics/FD_Salary_Week_' + str(week) + '.csv')

    return df

def main():

    # Scrape the injuries for the current week
    scrape_injuries()
    
    # Scrape the salary data for the current week    
    scrape_salary()

    # Set weeks to scrape
    week_start = 8
    week_end = 8
    schedule_week = 9

    # Define what is to be scraped, Offence (O), Defence (D), Kicker (K)
    player_types = ['O', 'D']

    # Scrape schedule
    scrape_schedule(schedule_week)

    # Scrape data
    for position in player_types:
        for week in range(week_start, week_end+1):
            scrape_player_data(week, position)
            print(str(position) + ' Data exported for week ' + str(week))
    

if __name__ == "__main__":
    main()
