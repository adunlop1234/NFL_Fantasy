import pandas as pd
import os
import numpy as np
#import tensorflow as tf
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt

#? Tutorial used: https://www.tensorflow.org/tutorials/keras/regression

# HYPERPARMETERS
random_state = 1
l1_regularisation = 1.5
learning_rate = 0.0007
epochs = 300
batch_size = 10

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

# Remove QBs who have missed 3 or more of their last 6 games
pass_columns = [x for x in columns if ('pass_yds' in x) and ('P' in x)]
df_temp = df[pass_columns]
df = df[(df_temp <= 100).sum(axis=1) < 3]

# Get features and labels
X = df[[column for column in df.columns.values if column != 'Label_pass_yds']].to_numpy()
y = np.array(df.Label_pass_yds)

# Split into training, validating and testing set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=random_state)

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error

print(X_train)
print(X_train.shape)
quit()
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


'''
# Use a normalisation layer to normalise the features
normalizer = tf.keras.layers.experimental.preprocessing.Normalization()
normalizer.adapt(np.array(X_train))


# Set up neural net
model = tf.keras.models.Sequential([
    # Normalisation layer
    normalizer,
    # Add a first hidden layer
    tf.keras.layers.Dense(40, activation="relu", kernel_regularizer=tf.keras.regularizers.l1(l1_regularisation)),
    # Add a second hidden layer
    tf.keras.layers.Dense(10, activation="relu", kernel_regularizer=tf.keras.regularizers.l1(l1_regularisation)),
    # Add an output layer
    tf.keras.layers.Dense(1)

])

# Compile neural network
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
    loss="mean_absolute_error"
)

# Fit model on training data
history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split = 0.2)

def plot_loss(history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.ylim([0,150])
    plt.legend()
    plt.show()

plot_loss(history)


# Evaluate neural network performance
y_predict = model.predict(X_test).flatten()
plt.scatter(y_test, y_predict)
plt.plot(np.unique(y_test), np.poly1d(np.polyfit(y_test, y_predict, 1))(np.unique(y_test)))
plt.plot([0, 500], [0, 500])
plt.xlabel('Actual')
plt.ylabel('Predict')
plt.xlim([0,500])
plt.ylim([0,500])
plt.show()
'''