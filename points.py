'''
Appends Paddy Power Points column to scraped data
'''

import pandas as pd

# Read csv into a dataframe
defence = pd.read_csv('D_Week_1.csv')

# Replace '-' with 0
defence = defence.replace('-', 0)

# Ensure each column correct datatype (default object)
pd.to_numeric(defence, errors='ignore')

#defence = defence.astype({'Sacks': 'int64'}).dtypes
#defence["Sacks"].astype(str).astype(int).dtypes
#defence["Saf"].astype(str).astype(int).dtypes
print(defence.dtypes)

# Calculate Paddy Power points and add column
#defence.assign(Paddy = defence.Sacks + defence.Saf)
#defence["Paddy"] = 1.0 * defence["Sacks"] + 2.0 * defence["Saf"]
print("HERE")
print(defence)