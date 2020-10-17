'''
Set of scripts that scrapes all weekly offence, kicker and 
defence player data from https://www.nfl.com/players/
'''

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrape_data(URL, player_type):

    # Create the request
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get all table entries and headers
    rows = soup.find_all('tr')
    headers = soup.find_all('th')

    # Create the columns header names
    columns = [header.getText() for header in headers]

    # Initialise dataframe with the column names
    df = pd.DataFrame(columns = columns)

    # Add the entries to the dataframe
    for row in rows[1:]:
        items = row.find_all('td')
        entries = [item.getText().strip() for item in items]
        entry_dict = {key:value for (key, value) in zip(columns, entries)}
        df = df.append(entry_dict, ignore_index=True)


    # Sort the entries by week order
    df = df.sort_values(by="WK", ascending=True)
    
    # Return the data frame
    return df


def acquire_names():

    # Create a list of letters in alphabet
    alphabet = [chr(i) for i in range(97, 123)]

    # Define the base URL
    URL_base = 'https://www.nfl.com/players/active/a?query=a'

    # Initialise the output
    all_names = list()

    # Define dict of the page number extensions to add on the end of the URL
    #page_no = {
    #'2': '&after=c2ltcGxlLWN1cnNvcjk5',
    #'3': '&after=c2ltcGxlLWN1cnNvcjE5OQ=='
    #}

    # Loop over each letter in alphabet to get all players
    for letter in alphabet:

        URL_current = URL_base.replace('a?query=a', 'a?query=a'.replace('a', letter))

        # Loop until 
        while True:

            # Create the request
            page = requests.get(URL_current)
        
            # Parse the html using soup
            soup = BeautifulSoup(page.content, 'html.parser')
        
            # Get names of all players for the url
            names = [name['href'].split('/')[-2] for name in soup.find_all('a', {'href' : re.compile(r'^/players/.*/$')})]
        
            # Append names to master list
            all_names += names

            # Check if the page has a hyperlink for next page
            extension = soup.find('a', title='Next')

            # Break if there isn't a next page otherwise go to next page
            if extension:
                URL_current = 'https://www.nfl.com' + soup.find('a', title='Next')['href']
            else:
                break

        print(str(letter) + " completed.")

    return all_names

def main():

    # Define the URL to be scraped
    URL = "https://www.nfl.com/players/lamar-jackson/stats/logs/"

    columns = {
    'offence': ['WK', 'Game Date', 'OPP', 'RESULT', 'COMP', 'ATT', 'YDS', 'AVG', 
                'TD', 'INT', 'SCK', 'SCKY', 'RATE', 'ATT', 'YDS', 'AVG', 'TD', 
                'FUM', 'LOST'],
    'defence': [''],
    'kicker': ['']
    }

    # Create dataframe for week and offence
    # Loop over each player
    # Add the dataframe to a master dataframe storing all players with name and position and team
    # Siphon off the overall dataframe into the number of dataframes per week

    # Return all of the names to search through
    all_names = acquire_names()

    # Scrape data
    df = scrape_data(URL, player_type='O')

if __name__ == "__main__":
    main()
