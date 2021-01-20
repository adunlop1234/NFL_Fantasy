import requests
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar
import os

# Create progress bar
bar = IncrementalBar('Getting Player Names', max = 26, suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')


with open(os.path.join('Static', 'staticData','players.csv'),'w') as f:

    f.write('name,id,position,start,end\n')

    for letter in [chr(l) for l in range(65,91)]:

        URL = 'https://www.pro-football-reference.com/players/' + letter

        page = requests.get(URL, allow_redirects=True)

        # Parse the html using soup
        soup = BeautifulSoup(page.content, 'html.parser')

        soup = soup.find(id='div_players')


        for person in soup.find_all('p'):
            f.write(person.find('a').get_text().strip() + ',')
            f.write(person.find('a').get('href')[11:len(person.find('a').get('href'))-4] + ',')
            f.write(person.get_text()[person.get_text().index('(')+1:person.get_text().index(')')].replace(',','-') + ',')
            f.write(person.get_text()[len(person.get_text())-9:len(person.get_text())-5] + ',' + person.get_text()[len(person.get_text())-4:len(person.get_text())])
            f.write('\n')

        bar.next()

bar.finish()