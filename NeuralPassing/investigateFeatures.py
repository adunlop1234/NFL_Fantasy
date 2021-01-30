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

# HYPERPARMETERS
random_state = 1
l1_regularisation = 1.5
learning_rate = 0.0007
epochs = 300
batch_size = 10

# Open raw features
df = pd.read_csv(os.path.join('NeuralPassing','Data','qbPassingFeatures.csv'), index_col=0, header=[0,1])

# Only keep feature columns (i.e. not name, week, season)
df = df.loc[:,df.columns.get_level_values(0).isin(['QB','Offence','Defence_prev_mean','Defence_upcom_mean','Label'])]

# Only keep games with Label_pass_yds > 50 (e.g. eliminate Taysom Hills and injuries)
df = df[df['Label','pass_yds'] > 50]

# Remove QBs who have missed 3 or more of their last 6 games (defined by fewer than 50 pass yards)
pass_columns = [('QB', 'pass_yds_' + str(i)) for i in range(1,7)]
df = df[(df[pass_columns] <= 50).sum(axis=1) < 3]

# Drop non-numeric columns
OH_cols = list((df.dtypes == 'object')[(df.dtypes == 'object')].index)
df = df.drop(OH_cols, axis=1)

labels = np.array(df['Label','pass_yds'])

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

def plot1(regr, x, labels):

    plt.scatter(x, labels)
    plt.plot(x,regr.predict(x))
    plt.show()
