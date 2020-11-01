'''
Set of scripts that scrapes all weekly offence, kicker and 
defence player data from https://www.nfl.com/players/
'''

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sys, os
from progress.bar import IncrementalBar 

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
    
        # Set the index of the dataframe to be each week and add player name/team/position 
        test_df = test_df.set_index('WK')
        test_df['Player Name'] = name
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
            week_df.to_csv(os.path.join("Data_NFL", "O_Week_" + str(i+1) + ".csv"))

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
    ret_dict['Player Name'] = name
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
    cols = {'passing' : {'Att' : 'Pass Att', 'Cmp' : 'Pass Cmp', 'Cmp %' : 'Pass Cmp %', 'Yds/Att' : 'Pass Yds/Att', 'Yds' : 'Pass Yds', 'TD' : 'Pass TD', 'Rate' : 'Pass Rate'},
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

    # Output the data 
    df.to_csv(os.path.join('Data_NFL', 'Defence_Total.csv'))


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

    # Output the data 
    df.to_csv(os.path.join('Data_NFL', 'Offence_Total.csv'))


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
        
        # Calculate number games played (sum W, L and T)
        games = 0
        for item in items[1:4]:
            games += int(item.getText().strip())

        # Add team to dictionary
        games_played[team] = games

    # Create dataframe to save games played
    df = pd.DataFrame.from_dict(games_played, orient='index')

    # Save as csv
    df.to_csv('Data_NFL/games_played.csv')


def main():

    ## Scrape all of the team defence stats
    scrape_defence_team()

    ## Scrape all of the team offence stats
    scrape_offence_team()

    ## Scrape all of the offence weekly player stats
    scrape_offence_players()

    ## Scrape games played
    games_played()
    

if __name__ == "__main__":
    main()
