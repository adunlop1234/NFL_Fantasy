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

def scrape_data(URL):

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
                   'RUSH TD', 'REC YDS', 'REC AVG', 'REC LONG', 'REC TD' 'FUM', 'FUM LOST']
    elif position in ['WR', 'TE']:
        columns = ['WK', 'Game Date', 'OPP', 'RESULT', 'REC YDS', 'REC AVG', 'REC LONG', 'REC TD', 
                   'RUSH ATT', 'RUSH YDS', 'RUSH AVG', 'RUSH LONG','RUSH TD',  'FUM', 'FUM LOST']
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

def main():

    # Define the URL to be scraped
    URL = "https://www.nfl.com/players/lamar-jackson/stats/logs/"

    columns = ['Player Name', 'Team', 'Position', 'WK', 'Game Date', 'OPP', 'RESULT', 
               'PASS COMP', 'PASS ATT', 'PASS YDS', 'PASS AVG', 'PASS TD', 'PASS INT', 'SCK', 'SCKY', 'PASS RATE', 
               'RUSH ATT', 'RUSH YDS', 'RUSH AVG', 'RUSH LONG', 'RUSH TD', 
               'REC YDS', 'REC AVG', 'REC LONG', 'REC TD',
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

        test_data = scrape_data(URL.replace('lamar-jackson', player_name))
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
        week_df.to_csv(os.path.join("Data_NFL", "O_Week_" + str(i+1) + ".csv"))

if __name__ == "__main__":
    main()
