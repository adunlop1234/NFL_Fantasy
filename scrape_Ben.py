''' 
Scrapes and sums W L and T from https://www.nfl.com/standings/ to give number games played
'''

import requests
from bs4 import BeautifulSoup


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
        except:
            continue
        
        # Calculate number games played (sum W, L and T)
        games = 0
        for item in items[1:4]:
            games += int(item.getText().strip())

        # Add team to dictionary
        games_played[team] = games
        
    return games_played    


def main():

    ## Scrape W L and T for games played
    games_played()
    

if __name__ == "__main__":
    main()