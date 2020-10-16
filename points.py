'''
Appends Paddy Power Points column to scraped data
'''

import pandas as pd

# Read csv into a dataframe
defence = pd.read_csv('D_Week_1.csv')

# Replace '-' with 0
defence = defence.replace('-', 0)

# Convert numbers to numeric data types
defence["Sacks"] = pd.to_numeric(defence["Sacks"], errors='ignore')
defence["Def INT"] = pd.to_numeric(defence["Def INT"], errors='ignore')
defence["Fum Rec"] = pd.to_numeric(defence["Fum Rec"], errors='ignore')
defence["Saf"] = pd.to_numeric(defence["Saf"], errors='ignore')
defence["Def TD"] = pd.to_numeric(defence["Def TD"], errors='ignore')
defence["Def 2pt Ret"] = pd.to_numeric(defence["Def 2pt Ret"], errors='ignore')
defence["Def Ret TD"] = pd.to_numeric(defence["Def Ret TD"], errors='ignore')
defence["Pts Allowed"] = pd.to_numeric(defence["Pts Allowed"], errors='ignore')
defence["Points Total"] = pd.to_numeric(defence["Points Total"], errors='ignore')

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


'''
Arthur's Solution to Datatype
# Ensure each column correct datatype (default object)
defence.apply(pd.to_numeric, errors='ignore')

# Create dict of datatypes to reformat the column datatypes
data_types = {
	'Name': 'str',
	'Position': 'str',
	'Sacks': 'int64',
	'Def INT': 'int64',
	'Fum Rec': 'int64',
	'Saf': 'int64',
	'Def TD': 'int64',
	'Def 2pt Ret': 'int64',
	'Def Ret TD': 'int64',
	'Pts Allowed': 'int64',
	'Points Total': 'float64'
}

# By setting defence = defence.astype.dtypes it set the data frame to be a list of datatypes rather than update the datatype of each column.
# The other thing to note is that the "object" datatype is a string of unlimited size. Otherwise you need to specify the max number of bytes in the string:
# https://stackoverflow.com/questions/33957720/how-to-convert-column-with-dtype-as-object-to-string-in-pandas-dataframe
print(defence.dtypes)
defence = defence.astype(data_types)
#defence["Sacks"].astype(str).astype(int).dtypes
#defence["Saf"].astype(str).astype(int).dtypes
print(defence.dtypes)
'''