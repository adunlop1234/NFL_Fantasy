import pandas as pd
import os
from progress.bar import IncrementalBar

number_years = 6
print('Warning: progress bar is non-linear')
bar = IncrementalBar('Seperating Data', max = number_years*3, suffix = '%(percent).1f%% Complete - Estimated Time Remaining: %(eta)ds')


for item in ['defenceData', 'offenceData', 'playersGamelogs']:

    # Open as DataFrame and sort by date
    df = pd.read_csv(os.path.join('Static','staticData', item + '.csv'), index_col=0)
    df = df.sort_values(by=['game_date'])

    # Loop over rows
    year = None
    for index, row in df.iterrows():

        # Create new dataframe for new season and save previous
        if str(row.game_date)[:4] != year and row.week_num != 17:

            if year != None:
                if item != 'playersGamelogs':
                    season.sort_values(by=['team', 'week_num']).reset_index(drop=True).to_csv(os.path.join('PrimaryProcess', 'Data',year[2:] + item[0].upper() + '.csv'))
                    bar.next()
                else:
                    season.sort_values(by=['name', 'week_num']).reset_index(drop=True).to_csv(os.path.join('PrimaryProcess', 'Data',year[2:] + 'L.csv'))
                    bar.next()

            year = str(row.game_date)[:4]

            season = pd.DataFrame(columns=df.columns.values)

        season = season.append(row.to_dict(), ignore_index=True)

    # Save final season (as for loop will have ended)
    if item != 'playersGamelogs':
        season.sort_values(by=['team', 'week_num']).reset_index(drop=True).to_csv(os.path.join('PrimaryProcess', 'Data',year[2:] + item[0].upper() + '.csv'))
        bar.next()
    else:
        season.sort_values(by=['name', 'week_num']).reset_index(drop=True).to_csv(os.path.join('PrimaryProcess', 'Data',year[2:] + 'L.csv'))
        bar.next()


bar.finish()