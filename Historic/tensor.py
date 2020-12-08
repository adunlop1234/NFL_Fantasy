import numpy as np
import os
import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt

EPOCHS = 100
TEST_SIZE = 0.4
features_columns = ['max', 'min', 'mean', 'std', 'D Pass Yds/Game', 'D Pass Yds/Att', 'D Pass TDs/Game', 'D Rush Yds/Game', 'D Rush YPC', 'D Rush TDs/Game']
LEARNING_RATE = .01

def main():

    # Get list of features and list of corresponding labels
    features, labels = load_data()

    # Split data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(features), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    history = model.fit(x_train, y_train, epochs=EPOCHS)

    # Gather the trained model's weight and bias.
    trained_weight = model.get_weights()[0]
    trained_bias = model.get_weights()[1]

    # Plot the linear regression
    plot_the_model(trained_weight, trained_bias, x_train, y_train)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    plot_the_loss_curve(history.epoch, history.history["root_mean_squared_error"])



def load_data():
    ''' 
    Returns tuple (features, labels) where:
        * features is a list of lists
        * labels is a list of corresponding labels
    '''

    # Read in data to train the model
    df = pd.read_csv(os.path.join('Historic', 'Data.csv'))

    # Get list of lists of features
    features = df[features_columns].values.tolist()

    # Get list of labels
    labels = list(df["Label"])

    avg = list(df['mean'])

    return (avg, labels)


def get_model():
    '''
    Returns a compiled model
    '''

    model = tf.keras.Sequential()

    model.add(tf.keras.layers.Dense(units=1, input_shape=(1,)))

    model.compile(optimizer=tf.keras.optimizers.RMSprop(lr=LEARNING_RATE),
                loss="mean_squared_error",
                metrics=[tf.keras.metrics.RootMeanSquaredError()])

    return model

def plot_the_loss_curve(epochs, mae_training):
    """Plot a curve of loss vs. epoch."""

    plt.figure()
    plt.xlabel("Epoch")
    plt.ylabel("Root Mean Squared Error")

    plt.plot(epochs[1:], mae_training[1:], label="Training Loss")
    plt.legend()

    plt.show()  


def plot_the_model(trained_weight, trained_bias, feature, label):
  """Plot the trained model against the training feature and label."""

  # Label the axes.
  plt.xlabel("feature")
  plt.ylabel("label")

  # Plot the feature values vs. label values.
  plt.scatter(feature, label)

  # Create a red line representing the model. The red line starts
  # at coordinates (x0, y0) and ends at coordinates (x1, y1).
  x0 = 0
  y0 = trained_bias
  x1 = feature.copy().sort()[-1]
  y1 = trained_bias + (trained_weight * x1)
  plt.plot([x0, x1], [y0, y1], c='r')

  # Render the scatter plot and the red line.
  plt.show()


if __name__ == '__main__':
    main()

