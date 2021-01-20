import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os
from progress.bar import IncrementalBar

def scrape_weather(year, week, weather, nfl_teams):

    # Define the URL for NFL weather site
    URL = 'http://www.nflweather.com/en/week/' + str(year) + '/week-' + str(week)

    # Create the request
    page = requests.get(URL, allow_redirects=True)

    # Parse the html using soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get all table rows
    rows = soup.find_all('tr')

    # Iterate over each row 
    for row in rows[1:]:
        
        weather['Year'].append(year)
        weather['Week'].append(week)

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

        weather["Home"].append(home)
        weather["Away"].append(away)
        weather["Forecast"].append(forecast)
        weather["Temp (C)"].append(temp_c)
        weather["Wind (mph)"].append(wind)


# Create dictionary of {New York Giants : NYG, etc.} for reference in functions
ref = pd.read_csv(os.path.join('References','teams.csv'))
nfl_teams = pd.Series(ref.Abrev.values,index=ref.Name).to_dict()

# Define a dictionary to store weather data
weather = {'Year' : [], 'Week' : [], 'Home' : [], 'Away' : [], 'Temp (C)' : [], 'Forecast' : [], 'Wind (mph)' : []}

number_years = 6
bar = IncrementalBar('Getting Weather', max = number_years*17, suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')

for year in range(2021-number_years, 2021):
    for week in range(1,18):
        scrape_weather(year,week,weather,nfl_teams)
        bar.next()
bar.finish()

# Save weather
pd.DataFrame.from_dict(weather).to_csv(os.path.join('Static','staticDataScripts','staticData','weather.csv'))