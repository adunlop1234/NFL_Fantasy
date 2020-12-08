import sys
# Need this as process in difference file location
sys.path.insert(1,'C:\\Users\\benja\\OneDrive\\Documents\\GitHub\\NFL_Fantasy')
import pandas as pd 
import process


latest_week = 11

# Open summary files
defence, offence = process.open_summaries()

# As offence doesnt contain position, find each players position
positions = {'QB' : [], 'WR' : [], 'RB' : [], 'TE' : []}
latest_O = pd.read_csv('Scraped/Statistics/O_Week_' + str(7) + '.csv')
for index, row in latest_O.iterrows():
    positions[row.Position].append(row.Name)

# Only keep RBs
offence = offence.loc[offence["Name"].isin(positions['RB'])].reset_index(drop=True)

# Create dataframe to store all data for neural net
columns = ['Name', 'max', 'min', 'mean', 'std', 'D Pass Yds/Game', 'D Pass Yds/Att', 'D Pass TDs/Game', 'D Rush Yds/Game', 'D Rush YPC', 'D Rush TDs/Game', 'Label']

# Create list to store dataframe from each week
data = []

# Loop over weeks
for week in range(7, latest_week):

    # Transform offence for given 'week':
    # Add opponent for that week (ignore defence below)
    defence_week, offence_week = process.opponent(offence.copy(), defence.copy(), week+1)
    columns_week = ['Name', 'Team', 'Opp'] + ['Week ' + str(j) for j in range(1, week+2)]
    offence_week = offence_week[columns_week]
    
    # Rename Week+1 as Label
    offence_week = offence_week.rename(columns={'Week ' + str(week+1) : 'Label'})

    # Drop rows where players dont play following week
    offence_week = offence_week[offence_week["Label"].notna()]

    # Calculate statistics on the columns and add them as columns
    stats = offence_week.drop(['Name', 'Team', 'Opp', 'Label'], axis=1).apply(pd.DataFrame.describe, axis=1).drop(['25%', '50%', '75%'], axis=1)

    # Add stats columns to offence_week
    offence_week = pd.concat([offence_week, stats], axis=1)

    # Drop players played 3 or fewer games
    offence_week = offence_week.loc[offence_week['count'] > 3]



    # For current week, get defence stats up until this point
    D = pd.read_csv('Historic/D_tot_Week_' + str(week) + '.csv')

    # Calculate columns want
    D['D Pass Yds/Game'] = D['Pass Yds'] / D['Games Played']
    D['D Pass Yds/Att'] = D['Pass Yds/Att']
    D['D Pass TDs/Game'] = D['Pass TD'] / D['Games Played']
    D['D Rush Yds/Game'] = D['Rush Yds'] / D['Games Played']
    D['D Rush YPC'] = D['Rush YPC']
    D['D Rush TDs/Game'] = D['Rush TD'] / D['Games Played']

    # Rename Team as Opp to perform merge
    D = D.rename(columns={'Team' : 'Opp'})
    # Merge defence into offence_week
    offence_week = offence_week.merge(D, on='Opp')

    # Only keep relevant columns
    data.append(offence_week[columns].round(2))

# Combine all each week's data into one df
pd.concat(data).to_csv('Historic/Data.csv')


    






