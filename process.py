'''
Adds useful metrics and sorts output data from filter.py
'''

import pandas as pd

# Add columns with average for season and past 3 weeks
def average_pts():

    # Open output files
    defence = pd.read_csv('Output/Defence_Summary.csv')
    offence = pd.read_csv('Output/Offence_Summary.csv')

    # Get list column names
    columns_D = list(defence)
    columns_O = list(offence)

    # Only keep 'Week i' columns 
    columns_D = sorted([s for s in columns_D if "Week " in s])
    columns_O = sorted([s for s in columns_O if "Week " in s])

    # Add average points column
    # Defence
    defence["Avg Points"] = defence.loc[:, columns_D].mean(axis=1).round(1)
    defence["Avg Points (3 weeks)"] = defence.loc[:, columns_D[-3:]].mean(axis=1).round(1)
    # Offence
    offence["Avg Points"] = offence.loc[:, columns_O].mean(axis=1).round(1)
    offence["Avg Points (3 weeks)"] = offence.loc[:, columns_O[-3:]].mean(axis=1).round(1)

    # Save processed output file
    defence.to_csv('Output/Defence_Summary_P.csv')
    offence.to_csv('Output/Offence_Summary_P.csv')




def main():
    average_pts()
    

if __name__ == "__main__":
    main()