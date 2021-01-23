'''
This script is just to investigate the features (previously did in terminal, but wanted record)
'''
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Open raw features
df = pd.read_csv(os.path.join('NeuralPassing','Data','qbPassingFeatures.csv'), index_col=0)
column_types = ['pass_cmp', 'pass_att', 'pass_yds', 'pass_td', 'pass_int', 'pass_sacked', 'rush_att', 'rush_yds', 'rush_td', 'home_game', 'Label_pass_yds']
# Get feature columns
columns = [column for column in df.columns.values if len([i for i in column_types if i in column]) > 0]
df = df[columns]

# Convert Home, Away, BYE to one-hot
df = pd.get_dummies(df)

# Fill any Nans with 0 (very rare occurence, just Jalen Hurts for 2 games)
df = df.fillna(0)

# Only keep games with Label_pass_yds > 50 (e.g. eliminate Taysom Hills and injuries)
df = df[df.Label_pass_yds >= 100]

# Remove QBs who have missed 3 or more of their last 6 games (or low scores)
pass_columns = [x for x in columns if ('pass_yds' in x) and ('P' in x)]
df_temp = df[pass_columns]
df = df[(df_temp <= 100).sum(axis=1) < 3]

# Linear Regression of passing yards vs historic mean
labels = np.array(list(df['Label_pass_yds']))

# Create dictionary to store regression results
regress = {'feature' : [], 'coef' : [], 'R2' : []}

for col in df.columns.values:

    x = np.array(list(df[col])).reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    regr.fit(x, labels)

    # Add to dictionary
    regress['feature'].append(col)
    regress['coef'].append(np.round(regr.coef_[0],decimals=3))
    regress['R2'].append(np.round(regr.score(x, labels),decimals=3))

df_reg = pd.DataFrame.from_dict(regress)
df_reg = df_reg[df_reg.R2 > 0.001]
df_reg = df_reg.sort_values(by=['coef'], ascending=False)

a=1
    

