'''
Set of scripts that scrapes all weekly offence, kicker and 
defence player data from https://fantasy.nfl.com.
'''

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sys, os
import datetime
import json
from progress.bar import IncrementalBar 

# Create dictionary of {New York Giants : NYG, etc.} for reference in functions
ref = pd.read_csv('References/teams.csv')
nfl_teams = pd.Series(ref.Abrev.values,index=ref.Name).to_dict()


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
            if player_type == 'D':
                # Convert to abrev form
                data_out['Name'] = nfl_teams[row.find('a').getText()]
            else:
                data_out['Name'] = simplify(row.find('a').getText())

            # Position and Team
            positionTeam = row.find('em').getText().split(' - ')
            if len(positionTeam) > 1:
                data_out['Position'] = positionTeam[0]
                # Replace LA with LAR and WAS with WSH
                if positionTeam[1] == "LA":
                    data_out['Team'] = "LAR"
                elif positionTeam[1] == "WAS":
                    data_out['Team'] = "WSH"
                else:
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
    df.to_csv(os.path.join('Scraped', 'NFL_Fantasy', str(player_type) + '_Week_' + str(data_in['week']) + '.csv'))

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
    df.to_csv(os.path.join('Scraped', 'Schedule', 'Schedule_Week_' + str(week) + '.csv'))

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
        name = simplify(player_info.find('a', href=re.compile(r'/nfl/')).getText())
        team = re.split(' |\)|\(', player_info.find('small').getText())[1]
        position = re.split(' |\)|\(', player_info.find('small').getText())[-2]

        # Replace WAS with WSH
        if team == "WAS":
            team = "WSH"

        elif team == "JAC":
            team = "JAX"

        # If name is a team (e.g. New York Giants), replace with abreviation which is in team column
        if name in nfl_teams.keys():
            name = team

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
    df.to_csv(os.path.join('Scraped', 'Salary', 'FD_Salary_Week_' + str(week) + '.csv'))

    return df

def scrape_injuries():
    # Scrape injuries from depth chart for each team

    # Define the URL for the team in question
    URL = 'https://www.espn.com/nfl/team/depth/_/name/ari'

    # Get page
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Links for all teams
    attrs = {'class' : re.compile('dropdown__option'), 'data-url' : re.compile('/nfl/team/depth/_/name/')}
    urls = [team['data-url'] for team in soup.find_all('option', attrs)]
    urls.insert(0, '/nfl/team/depth/_/name/ari')

    # Define the output offence depth chart 
    #! Outdated data-structure (as no longer scraping depth chart) but avoiding a re-write
    o_positions = ['QB', 'RB', 'WR1', 'WR2', 'WR3', 'TE']
    depth_chart = {
        position : {
            1 : '',
            2 : '',
            3 : '',
            4 : ''
        }
        for position in o_positions
    }

    # Create injury list
    injuries = pd.DataFrame(columns = ['Name', 'Status', 'Team'])

    # Loop over each page and therefore team
    for url in urls:

        # Get the current url
        page = requests.get(URL.replace('/nfl/team/depth/_/name/ari', url))
        team = url.split('/')[-1].upper()

        # Parse the html using soup
        soup = BeautifulSoup(page.content, 'html.parser')

        # Create a list to loop over the number of data-idx for each row in table of depth chart
        data_range = range(6)
 
        # Loop over each position
        for data_id in data_range:

            # Get all rows for the current position
            rows = soup.find_all('tr', {'class' : 'Table__TR Table__TR--sm Table__even', 'data-idx' : str(data_id)})
            for row in rows:

                # Find all the entries
                items = row.find_all('td')

                # Position determined by data-idx
                position = o_positions[data_id]

                # If len == 4 then it's the player names, only get offence so break after allocation
                if len(items) == 4:
                    for i in range(0, 4):
                        
                        if re.search(r'( O| D| IR| Q| SUSP)\b', items[i].getText()):
                            status = items[i].getText().split(' ')[-1]
                            name = ' '.join(items[i].getText().split(' ')[0:-1])
                            injuries = injuries.append({'Name' : simplify(name), 'Team' : team, 'Position': o_positions[data_id][0:2], 'Status' : status}, ignore_index=True)

                        # Strip injury status from the end of the name
                        name = re.sub(r'( O| D| IR| Q| SUSP)\b', '', items[i].getText())

                    break


    # Write the csv output
    injuries.to_csv(os.path.join('Scraped', 'Injury_Status.csv'))


def scrape_offence_players():

    # Define the URL to be scraped
    URL = "https://www.nfl.com/players/lamar-jackson/stats/logs/"

    columns = ['Player Name', 'Team', 'Position', 'WK', 'Game Date', 'OPP', 'RESULT', 
               'PASS COMP', 'PASS ATT', 'PASS YDS', 'PASS AVG', 'PASS TD', 'PASS INT', 'SCK', 'SCKY', 'PASS RATE', 
               'RUSH ATT', 'RUSH YDS', 'RUSH AVG', 'RUSH LONG', 'RUSH TD', 
               'REC', 'REC YDS', 'REC AVG', 'REC LONG', 'REC TD',
               'FUM', 'FUM LOST']

    # Return all of the names to search through
    [offence_names, kicker_names] = acquire_player_names()

    # Create the list of dataframes to return for all weeks
    df = pd.DataFrame(columns = columns)
    week_dfs = dict()
    for i in range(1, 18):
        week_dfs[str(i)] = df

    # Create progress bar
    bar = IncrementalBar('Acquiring Player Data', max = len(offence_names), suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')

    for counter, player_name in enumerate(offence_names):

        test_data = scrape_offence_player_stats(URL.replace('lamar-jackson', player_name))
        name, team, position, test_df = test_data['Player Name'], test_data['Team'], test_data['Position'], test_data['Stats']

        # Replace long team name with abrevation
        if team in nfl_teams.keys():
            team = nfl_teams[team]
    
        # Set the index of the dataframe to be each week and add player name/team/position 
        test_df = test_df.set_index('WK')
        test_df['Player Name'] = simplify(name)
        test_df['Position'] = position
        test_df['Team'] = team
    
        # Loop over all of the weeks this player has played
        for i, week in enumerate(test_df.index.values):
    
            # Add the row of data for the current week
            week_dfs[week] = week_dfs[week].append(test_df.iloc[[i]], ignore_index = True, sort=True)

        bar.next()

    # End progress bar
    bar.finish()

    # Write the output files
    for i, week_df in enumerate(week_dfs.values()):
        week_df = week_df[columns]
        week_df = week_df.sort_values('Player Name', ascending=True)

        # Only write file if there is data in it
        if len(week_df) > 2:
            week_df.to_csv(os.path.join("Scraped", "NFL_Logs", "O_Week_" + str(i+1) + ".csv"))

def scrape_offence_player_stats(URL):

    # Create the request
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')
    
    # Get name and position
    name = soup.find('h1', class_=re.compile('nfl-c-player-header__title')).getText()
    position = soup.find('span', class_=re.compile('nfl-c-player-header__position')).getText().strip()
    try:
        team = soup.find('div', class_=re.compile('nfl-c-player-header__team nfl-u-hide-empty')).getText()
    except:
        team = None

    # Define columns in data table from their position
    if position in 'QB':
        columns = ['WK', 'Game Date', 'OPP', 'RESULT', 'PASS COMP', 'PASS ATT', 'PASS YDS', 'PASS AVG', 
                   'PASS TD', 'PASS INT', 'SCK', 'SCKY', 'PASS RATE', 'RUSH ATT', 'RUSH YDS', 'RUSH AVG', 
                   'RUSH TD', 'FUM', 'FUM LOST']
    elif position in 'RB':
        columns = ['WK', 'Game Date', 'OPP', 'RESULT', 'RUSH ATT', 'RUSH YDS', 'RUSH AVG', 'RUSH LONG',
                   'RUSH TD', 'REC', 'REC YDS', 'REC AVG', 'REC LONG', 'REC TD', 'FUM', 'FUM LOST']
    elif position in ['WR', 'TE']:
        columns = ['WK', 'Game Date', 'OPP', 'RESULT', 'REC', 'REC YDS', 'REC AVG', 'REC LONG', 'REC TD', 
                   'RUSH ATT', 'RUSH YDS', 'RUSH AVG', 'RUSH LONG', 'RUSH TD', 'FUM', 'FUM LOST']
    else:
        print("Ineligible player asked to be scraped of position " + str(position))
        sys.exit()

    # Get all table entries and headers
    rows = soup.find_all('tr')

    # Initialise dataframe with the column names
    df = pd.DataFrame(columns = columns)

    # Add the entries to the dataframe
    for row in rows[1:]:
        items = row.find_all('td')
        entries = [item.getText().strip() for item in items]
        entry_dict = dict(zip(columns, entries))
        df = df.append(entry_dict, ignore_index=True)

    # Sort the entries by week order
    df = df.sort_values(by="WK", ascending=True)

    # Create a return dictionary
    ret_dict = dict()
    ret_dict['Player Name'] = simplify(name)
    ret_dict['Team'] = team
    ret_dict['Position'] = position
    ret_dict['Stats'] = df
    
    # Return the data frame
    return ret_dict

def scrape_defence_team():

    # Create master df
    df = pd.DataFrame()

    # Define base URL
    URL_base = 'https://www.nfl.com/stats/team-stats/defense/passing/2020/reg/all'
    
    # Define the stats to acquire
    genres = ['passing', 'rushing', 'receiving', 'scoring', 'fumbles', 'interceptions']

    # Create progress bar
    bar = IncrementalBar('Acquiring Defence Data', max = len(genres), suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')

    # Get all stats
    genre_dfs = dict()
    for genre in genres:
        genre_dfs[genre] = scrape_defence_team_stats(URL_base.replace('passing', genre))
        bar.next()

    # Close progress bar
    bar.finish()

    # Strip relevant columns from each data frame
    cols = {'passing' : {'Att' : 'Pass Att', 'Cmp' : 'Pass Cmp', 'Cmp %' : 'Pass Cmp %', 'Yds/Att' : 'Pass Yds/Att', 'Yds' : 'Pass Yds', 'TD' : 'Pass TD', 'Rate' : 'Pass Rate', 'Sck' : 'Sacks'},
            'rushing' : {'Att' : 'Rush Att', 'Rush Yds' : 'Rush Yds', 'YPC' : 'Rush YPC', 'TD' : 'Rush TD'},
            'receiving' : {'Rec' : 'Rec', 'Yds' : 'Rec Yds', 'Yds/Rec' : 'Rec Yds/Rec', 'TD' : 'Rec TD'},
            'scoring' : {'FR TD' : 'FR TD', 'SFTY' : 'SFTY'},
            'fumbles' : {'FF' : 'FF', 'FR' : 'FR', 'Rec FUM' : 'Rec FUM', 'Rush FUM' : 'Rush FUM'},
            'interceptions' : {'INT' : 'INT', 'INT TD' : 'INT TD'}
            }

    # Strip relevant data from genres and put into master
    for genre in genres:
        for key, value in cols[genre].items():
            df[value] = genre_dfs[genre][key]

    # Replace team names with abbreviation (e.g. Giants -> NYG)
    # Add Team column (N.B. currently short version of team name is index)
    df.insert(loc=0, column='Team', value="")
    for index, row in df.iterrows():

        # Loop over team names
        for team in nfl_teams.keys():
            if index in team:
                df.at[index, "Team"] = nfl_teams[team]
                continue

        # Need to deal with Washington seperately
        if index == "FootballTeam":
            df.at[index, "Team"] = "WSH"

    # Reset index to numbers
    df = df.reset_index(drop=True)

    # Output the data 
    df.to_csv(os.path.join('Scraped', 'NFL_Logs', 'Defence_Total.csv'))


def scrape_defence_team_stats(URL):

    # Create the request
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get all table entries and headers
    rows = soup.find_all('tr')
    headers_entries = soup.find_all('th')

    # Collate headers
    headers = [header.getText() for header in headers_entries]
    df = pd.DataFrame(columns = headers)

    # Loop over each row and store data
    for row in rows[1:]:
        entries = [item.getText().replace('\n', ' ').replace(' ', '') for item in row.find_all('td')]
        entries[0] = entries[0][:int(len(entries[0])/2)]
        df = df.append(dict(zip(headers, entries)), ignore_index=True)

    # Set the index and sort
    df = df.set_index('Team')
    df = df.sort_values('Team', ascending=True)

    return df

def scrape_offence_team():

    # Create master df
    df = pd.DataFrame()

    # Define base URL
    URL_base = 'https://www.nfl.com/stats/team-stats/offense/passing/2020/reg/all'
    
    # Define the stats to acquire
    genres = ['passing', 'rushing', 'receiving', 'scoring']

    # Create progress bar
    bar = IncrementalBar('Acquiring Offence Team Data', max = len(genres), suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')

    # Get all stats
    genre_dfs = dict()
    for genre in genres:
        genre_dfs[genre] = scrape_offence_team_stats(URL_base.replace('passing', genre))
        bar.next()

    # Close progress bar
    bar.finish()

    # Strip relevant columns from each data frame
    cols = {'passing' : {'Att' : 'Pass Att', 'Cmp' : 'Pass Cmp', 'Cmp %' : 'Pass Cmp %', 'Yds/Att' : 'Pass Yds/Att', 'Pass Yds' : 'Pass Yds', 'TD' : 'Pass TD', 'INT' : 'Pass INT', 'Rate' : 'Pass Rate', 'Sck' : 'Sacks'},
            'rushing' : {'Att' : 'Rush Att', 'Rush Yds' : 'Rush Yds', 'YPC' : 'Rush YPC', 'TD' : 'Rush TD', 'Rush FUM' : 'Rush FUM'},
            'receiving' : {'Rec' : 'Rec', 'Yds' : 'Rec Yds', 'Yds/Rec' : 'Rec Yds/Rec', 'TD' : 'Rec TD', 'Rec FUM' : 'Rec FUM'},
            'scoring' : {'Rsh TD' : 'Rush TD', 'Rec TD' : 'Rec TD', 'Tot TD' : 'Tot TD', '2-PT' : '2PT'}
            }

    # Strip relevant data from genres and put into master
    for genre in genres:
        for key, value in cols[genre].items():
            df[value] = genre_dfs[genre][key]

    # Replace team names with abbreviation (e.g. Giants -> NYG)
    # Add Team column (N.B. currently short version of team name is index)
    df.insert(loc=0, column='Team', value="")
    for index, row in df.iterrows():

        # Loop over team names
        for team in nfl_teams.keys():
            if index in team:
                df.at[index, "Team"] = nfl_teams[team]
                continue

        # Need to deal with Washington seperately
        if index == "FootballTeam":
            df.at[index, "Team"] = "WSH"

    # Reset index to numbers
    df = df.reset_index(drop=True)

    # Output the data 
    df.to_csv(os.path.join('Scraped', 'NFL_Logs', 'Offence_Total.csv'))


def scrape_offence_team_stats(URL):

    # Create the request
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get all table entries and headers
    rows = soup.find_all('tr')
    headers_entries = soup.find_all('th')

    # Collate headers
    headers = [header.getText() for header in headers_entries]
    df = pd.DataFrame(columns = headers)

    # Loop over each row and store data
    for row in rows[1:]:
        entries = [item.getText().replace('\n', ' ').replace(' ', '') for item in row.find_all('td')]
        entries[0] = entries[0][:int(len(entries[0])/2)]
        df = df.append(dict(zip(headers, entries)), ignore_index=True)

    # Set the index and sort
    df = df.set_index('Team')
    df = df.sort_values('Team', ascending=True)

    return df



def acquire_player_names():

    # Create a list of letters in alphabet
    alphabet = [chr(i) for i in range(97, 123)]

    # Define the base URL
    URL_base = 'https://www.nfl.com/players/active/a?query=a'

    # Initialise the outputs
    offence_names = list()
    kicker_names = list()

    # Create progress bar
    bar = IncrementalBar('Acquiring Player Names', max = len(alphabet), suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')

    # Loop over each letter in alphabet to get all players
    for letter in alphabet:

        URL_current = URL_base.replace('a?query=a', 'a?query=a'.replace('a', letter))

        # Loop until 
        while True:

            # Create the request
            page = requests.get(URL_current)
        
            # Parse the html using soup
            soup = BeautifulSoup(page.content, 'html.parser')
        
            # Check the player position and only add kickers and offence to separate lists
            rows = soup.find_all('tr')
            for row in rows:
                entries = row.find_all('td')
                for entry in entries:
                    if re.search(r'QB|WR|RB|TE', entry.getText()) and row.find('a', {'href' : re.compile(r'^/players/.*/$')}):
                        offence_names.append(row.find('a', {'href' : re.compile(r'^/players/.*/$')})['href'].split('/')[-2])
                    elif 'K' in entry.getText().split() and row.find('a', {'href' : re.compile(r'^/players/.*/$')}):
                        kicker_names.append(row.find('a', {'href' : re.compile(r'^/players/.*/$')})['href'].split('/')[-2])

            # Check if the page has a hyperlink for next page
            extension = soup.find('a', title='Next')

            # Break if there isn't a next page otherwise go to next page
            if extension:
                URL_current = 'https://www.nfl.com' + soup.find('a', title='Next')['href']
            else:
                break

        bar.next()

    # Finish progress bar
    bar.finish()

    return offence_names, kicker_names


# Scrape W L and T from standings to calculate games played 
def games_played():

    # Pass URL
    URL = 'https://www.nfl.com/standings/'

    # Create the request
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Create dict to store {NYG : 7, WSH : 6 .... etc.}
    games_played = {}

    # Get all table rows
    rows = soup.find_all('tr')

    # Iterate over each row 
    for row in rows:

        # Get list of table data in given row
        items = row.find_all('td')
        # Check a 'team row' (e.g. not header row)
        try:
            team = items[0].find("div", class_="d3-o-club-fullname").getText().strip()
        except IndexError:
            continue

        # Replace full team name with abbreviation
        team = nfl_teams[team]
        
        # Calculate number games played (sum W, L and T)
        games = 0
        for item in items[1:4]:
            games += int(item.getText().strip())

        # Add team to dictionary
        games_played[team] = games

    # Create dataframe to save games played
    df = pd.DataFrame.from_dict(games_played, orient='index')

    # Save as csv
    df.to_csv(os.path.join('Scraped','NFL_Logs','games_played.csv'))


def scrape_weather(week):

    # Define the URL for NFL weather site
    URL = 'http://www.nflweather.com/en/week/2020/week-' + str(week)

    # Create the request
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get all table rows
    rows = soup.find_all('tr')

    # Create list to store Dict of weather data
    weather = []
    weather_row = {
        "Home" : "",
        "Away" : "",
        "Temp (C)" : "",
        "Forecast" : "",
        "Wind (mph)" : ""
    }


    # Iterate over each row 
    for row in rows[1:]:

        # Get list of table data in given row
        items = row.find_all('td', class_="text-center")

        # Get home and away teams
        home = items[1].getText().strip() if items[1].getText().strip() != "Redskins" else "Washington"
        away = items[0].getText().strip() if items[0].getText().strip() != "Redskins" else "Washington"
        
        # Replace with short version team name
        for key in nfl_teams.keys():
            if home in key:
                home = nfl_teams[key]
            if away in key:
                away = nfl_teams[key]
            
        # Get forecast
        forecast = items[5].getText().strip()
        temp_c = "n/a"
        if forecast != "DOME":
            # Get temperature in farenheit
            temp_f = int(re.findall('[0-9]+', forecast)[0])
            # Convert to celsius
            temp_c = round((temp_f - 32) * 5/9, 1)

            # Remove temperature from forecast
            forecast = re.sub(r'^\W*\w+\W*', '', forecast)
            
        # Get wind
        wind = items[6].getText().strip()
        # Keep only wind speed
        wind = re.findall('[0-9]+', wind)[0]

        weather_row["Home"] = home
        weather_row["Away"] = away
        weather_row["Forecast"] = forecast
        weather_row["Temp (C)"] = temp_c
        weather_row["Wind (mph)"] = wind

        weather.append(weather_row.copy())


    # Now write weather report
    df = pd.DataFrame(columns=weather[0].keys())
    for w in weather:
        df = df.append(w, ignore_index=True)

    # Save entire weather data 
    df.to_csv(os.path.join('Scraped', 'Weather', 'Weather_' + str(week) + '.csv'))

# To ensure as much consistency as possible between datasets, strip offending characters      
def simplify(name):
    # Need to strip big to small (e.g. strip III before II otherwise doesnt work)
    name = name.replace('.','').replace('Jr','').replace('Sr','').replace('III','').replace('II','').replace('IV','').strip()
    # Need to be more carful with V (e.g. Vikings -> ikings)
    return re.sub('V$', '', name).strip()
    

