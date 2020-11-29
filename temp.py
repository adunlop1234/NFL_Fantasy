import pandas as pd
import re

# To ensure as much consistency as possible between datasets, strip offending characters      
def simplify(name):
    # Need to strip big to small (e.g. strip III before II otherwise doesnt work)
    name = name.replace('.','').replace('Jr','').replace('Sr','').replace('III','').replace('II','').replace('IV','').strip()
    # Need to be more carful with V (e.g. Vikings -> ikings)
    return re.sub('V$', '', name).strip()

for i in range(6,13):
    df = pd.read_csv('Scraped/Salary/FD_Salary_Week_' + str(i) + '.csv')

    for index, row in df.iterrows():
        df.at[index, "Name"] = simplify(row.Name)

    df.to_csv('Scraped/Salary/FD_Salary_Week_' + str(i) + '.csv')