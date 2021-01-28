import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder

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

# Get features and labels
X = df.loc[:, df.columns.get_level_values(0).isin(['QB','Offence','Defence_prev_mean','Defence_upcom_mean'])]
y = df['Label','pass_yds']

# Convert Home, Away, BYE to one-hot
OH_cols = list((X.dtypes == 'object')[(X.dtypes == 'object')].index)
OH_encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
X_OH_cols = pd.DataFrame(OH_encoder.fit_transform(X[OH_cols]))

# One-hot encoding removed index; put it back
X_OH_cols.index = X.index

# Replace columns with their one-hot versions
X = X.drop(OH_cols, axis=1)

# Add one-hot encoded columns to numerical features
X = pd.concat([X, X_OH_cols], axis=1)

# Split into training, validating and testing set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=random_state)

from sklearn.model_selection import learning_curve

fig, ax = plt.subplots(1, 1, figsize=(16, 6))
fig.subplots_adjust(left=0.0625, right=0.95, wspace=0.1)

i=1
N, train_lc, val_lc = learning_curve(XGBRegressor(n_estimators=2000, learning_rate=0.01),
                                        X_train, y_train, cv=7,
                                        train_sizes=np.linspace(0.3, 1, 5))

ax[i].plot(N, np.mean(train_lc, 1), color='blue', label='training score')
ax[i].plot(N, np.mean(val_lc, 1), color='red', label='validation score')
ax[i].hlines(np.mean([train_lc[-1], val_lc[-1]]), N[0], N[-1],
                color='gray', linestyle='dashed')

ax[i].set_ylim(0, 1)
ax[i].set_xlim(N[0], N[-1])
ax[i].set_xlabel('training size')
ax[i].set_ylabel('score')
ax[i].legend(loc='best')

"""
model = XGBRegressor(n_estimators=2000, learning_rate=0.01)
model.fit(X_train, y_train, 
             early_stopping_rounds=5, 
             eval_set=[(X_val, y_val)], 
             verbose=False)

y_predict = model.predict(X_train)
print(mean_absolute_error(y_train, y_predict))
fig, ax = plt.subplots(nrows=2, ncols=2)

ax[0,0].scatter(y_train, model.predict(X_train))
ax[0,1].scatter(y_val, model.predict(X_val))
ax[1,0].scatter(y_test, model.predict(X_test))
ax[0,0].plot(np.unique(y_train), np.poly1d(np.polyfit(y_train, model.predict(X_train), 1))(np.unique(y_train)))
ax[0,1].plot(np.unique(y_val), np.poly1d(np.polyfit(y_val, model.predict(X_val), 1))(np.unique(y_val)))
ax[1,0].plot(np.unique(y_test), np.poly1d(np.polyfit(y_test, model.predict(X_test), 1))(np.unique(y_test)))
ax[0,0].title.set_text('Train')
ax[0,1].title.set_text('Validate')
ax[1,0].title.set_text('Test')

for a in ax.flatten():
    a.set_xlabel('Actual')
    a.set_ylabel('Predict')
    a.plot([0, 500], [0, 500])
    a.set_xlim([0,500])
    a.set_ylim([0,500])

plt.show()
"""