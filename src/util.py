from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, Dense


def make_model():
    return Sequential([
        Input(3),
        Dense(7, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
