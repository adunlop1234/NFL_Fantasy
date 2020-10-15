'''
Appends Paddy Power Points column to scraped data
'''

import pandas as pd

# Read csv into a dataframe
defence = pd.read_csv('D_Week_1.csv')

# Replace '-' with 0
defence = defence.replace('-', 0)

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

# Calculate Paddy Power points and add column
#defence.assign(Paddy = defence.Sacks + defence.Saf)
#defence["Paddy"] = 1.0 * defence["Sacks"] + 2.0 * defence["Saf"]
print("HERE")
print(defence)