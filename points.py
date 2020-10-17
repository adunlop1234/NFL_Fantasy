'''
Appends Paddy Power Points column to scraped data
'''

import pandas as pd

# Read csv into a dataframe
defence = pd.read_csv('D_Week_1.csv')

# Replace '-' with 0
defence = defence.replace('-', 0)

# Convert numbers to numeric data types
stats = ["Sacks", "Def INT", "Fum Rec", "Saf", "Def TD", "Def 2pt Ret", "Def Ret TD", "Pts Allowed", "Points Total"]
for stat in stats:
    defence[stat] = pd.to_numeric(defence[stat], errors='ignore')

# Calculate Paddy Power points and add column
print("WARNING: Incomplete data so 'Blocked Punts/Kicks' and 'Extra Point Return' cannot be included")
# Add Paddy Points column (all but Points Allowed points)
defence = defence.assign(Paddy = defence["Sacks"] + 2*defence["Saf"] + 2*defence["Fum Rec"] + 2*defence["Def INT"] + 6*defence["Def TD"])
#  Now add Points Allowed points
for i in range(0,len(defence.index)):
    if defence["Pts Allowed"][i] == 0:
        defence["Paddy"][i] = defence["Paddy"][i] + 10
    elif defence["Pts Allowed"][i] <= 6:
        defence["Paddy"][i] = defence["Paddy"][i] + 7
    elif defence["Pts Allowed"][i] <= 13:
        defence["Paddy"][i] = defence["Paddy"][i] + 4
    elif defence["Pts Allowed"][i] <= 20:
        defence["Paddy"][i] = defence["Paddy"][i] + 1
    elif defence["Pts Allowed"][i] <= 27:
        defence["Paddy"][i] = defence["Paddy"][i] + 0
    elif defence["Pts Allowed"][i] <= 34:
        defence["Paddy"][i] = defence["Paddy"][i] - 1
    else:
        defence["Paddy"][i] = defence["Paddy"][i] - 4


print(defence)


