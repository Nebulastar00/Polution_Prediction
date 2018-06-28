
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
import keras.backend as K

import keras
from sklearn.metrics import confusion_matrix, recall_score, precision_score
from keras.models import Sequential,load_model
from keras.layers import Dense, Dropout, LSTM
from sklearn.model_selection import GridSearchCV
from keras.wrappers.scikit_learn import KerasRegressor

from keras.layers.core import Activation

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'



#changed all , by . in cvs files


salouel_raw_data = pd.read_csv("Moyennes_J_salouel_2005_2015.csv", header=None, sep=';', decimal=',')


creil_raw_data = pd.read_csv("Moyennes_J_creil_2005_2015.csv", header=None, sep=';', decimal=',')

cols = ['Date', 'NO2', 'O3', 'PM10', 'RR', 'TN', 'TX', 'TM',
                     'PMERM', 'FFM', 'DXY', 'UM', 'GLOT']

roth_raw_data = pd.read_csv("Moyennes_J_roth_2005_2015.csv", header=None, sep=';', decimal=',')


#print(salouel.info())

#def delete_missed_rows(nom_de_fichier):
    #df_raw = pd.read_csv(nom_de_fichier, header=None, sep=';', decimal=',')
    #columns = df_raw.columns
    #df = prepare_data(df_raw)



#Deleting dates column and making it all floats


def prepare_data(df):
    df = df.iloc[1:]
    df.columns = cols
    df = df.drop(["Date", 'NO2', 'O3'], axis=1)
    df = df.astype(float)
    return df

"""
TODO:
def prepare_data_ar(array_of_df)
"""

salouel_data = prepare_data(salouel_raw_data)
creil_data = prepare_data(creil_raw_data)
roth_data = prepare_data(roth_raw_data)



print("Before: ")

print(creil_data.info())

print("After: ")


creil_data = creil_data.dropna(axis=0, how="any")

salouel_data = salouel_data.dropna(axis=0, how="any")

roth_data = roth_data.dropna(axis=0, how="any")
print(salouel_data.info())


"""
REPLACE MISSING VALUES BY AVERAGE OF CORRESPONDING VALUES 


avg = np.nanmean([salouel_data.values, creil_data.values, roth_data.values], axis=0)

for df in [salouel_data, creil_data, roth_data]:
    df[df.isnull()] = avg



print("Salouel:")
print(salouel_data.head())
print("/*/*/*/*")

print("Creil:")
print(creil_data.head())
print("/*/*/*/*")

print("Roth:")
print(roth_data.head())
print("/*/*/*/*")


"""
#vdf
"""
SEPARATE DF INTO TRAIN AND TEST DATA
TRAIN IS 2005 - 2013
TEST IS 2014 AND 2015

RETURN CORTÉGE (TRAIN, TEST)
"""
#print("Number of columns: ")
#print(len(cols))

#print(salouel_raw_data.iloc[1:].head())

def separate_data(df, df_raw):

    df_raw = df_raw.iloc[1:]
    df_raw.columns = cols

    df["Date"] = pd.to_datetime(df_raw["Date"])
    train = df[df['Date'] < '31/12/2013'].drop("Date", axis=1)

    test = df[df['Date'] > '31/12/2013'].drop("Date", axis=1)
    return train, test




print("Train data: ")

"""
train_salouel, test_salouel = separate_data(salouel_data, salouel_raw_data)
label_array = np.array(train_salouel["PM10"])
train_salouel.drop("PM10", axis=1)

label_array = np.array(label_array)
print(test_salouel.head())


"""
label_array = np.array(salouel_data["PM10"])
salouel_data = salouel_data.drop("PM10", axis=1)


#label_array = np.array(label_array)




"""
NORMALISATION
"""
label_array = label_array.reshape(len(label_array), 1)


print("Label array goes here")

print(label_array)
min_max_scaler = preprocessing.MinMaxScaler()
#norm_train_df = pd.DataFrame(min_max_scaler.fit_transform(train_salouel), columns=train_salouel.columns)
#norm_test_df = pd.DataFrame(min_max_scaler.fit_transform(test_salouel), columns=test_salouel.columns)
norm_df = pd.DataFrame(min_max_scaler.fit_transform(salouel_data), columns=salouel_data.columns)
norm_label_array = pd.DataFrame(min_max_scaler.fit_transform(label_array))




sequence_length = 90


def gen_sequence(df):
    X_train = []
    for i in range(sequence_length, len(df)):
        X_train.append(df.iloc[i - sequence_length : i, :].values)
    return X_train

def  gen_y(df):
    Y_train = []
    for i in range(sequence_length, len(df)):
        Y_train.append(df[i - sequence_length : i])
    return Y_train

#seq_array = gen_sequence(norm_train_df)
#Y_train = np.array(gen_y(train_salouel["PM10"]))

seq_norm_df = gen_sequence(norm_df)
seq_y = gen_y(label_array)




"""


X_train = []
for i in range(sequence_length, len(norm_train_df) - sequence_length):
    X_train.append(norm_train_df[i - sequence_length:i, :])

"""

print("length: ")
#print(norm_train_df.head())
#seq_array = np.array(seq_array)

seq_norm_df = np.array(seq_norm_df)

seq_y = np.array(seq_y)


print("seq: ")
#print(seq_array[0])


def r2_keras(y_true, y_pred):
    """Coefficient of Determination
    """
    SS_res =  K.sum(K.square( y_true - y_pred ))
    SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()))

# metrics used to evaluate accuracy in GridSearch
def soft_acc(y_true, y_pred):
    return K.mean(K.equal(K.round(y_true), K.round(y_pred)))


"""

nb_features = seq_array.shape[2]

print("nb_features: ")
print(nb_features)

label_array = label_array.reshape(len(label_array), 1)

nb_out = label_array.shape[1]


print("label array : ")
print(label_array)

"""
label_array = label_array.reshape(len(label_array), 1)
nb_features = seq_norm_df.shape[2]


def create_model():
    model = Sequential()
    model.add(LSTM(
             input_shape=(sequence_length, nb_features),
             units=100,
             return_sequences=True))
    model.add(Dropout(0.25))
    model.add(LSTM(
              units=50,
              return_sequences=False))
    model.add(Dropout(0.25))
    model.add(Dense(units=1))
    model.add(Activation("linear"))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae', r2_keras])
    return model

model_path = './regression_model.h5'
label_array = label_array[sequence_length:len(label_array)]





#print(model.summary())


model_path = './regression_model.h5'

label_array = label_array[sequence_length:len(label_array)]

norm_label_array = norm_label_array[sequence_length:len(norm_label_array)]
"""

model = KerasRegressor(build_fn=create_model, verbose=0)

batch_size = [10, 20, 40, 60, 80, 100]
epochs = [10, 50, 100, 150, 200]

param_grid = dict(batch_size=batch_size, epochs=epochs)

grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1)

grid_result = grid.fit(seq_norm_df, norm_label_array)


print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))
"""
#for bs in batch_size_array:

model = create_model()

epochs = 100

batch_size = 100

history = model.fit(seq_norm_df, norm_label_array, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=2,
          callbacks = [#keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=0, mode='min'),
                       keras.callbacks.ModelCheckpoint(model_path, monitor='val_loss', save_best_only=True, mode='min', verbose=0)]
          )

"""
history = model.fit(seq_array, label_array, epochs=30, batch_size=200, validation_split=0.05, verbose=2,
          callbacks = [#keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=0, mode='min'),
                       keras.callbacks.ModelCheckpoint(model_path, monitor='val_loss', save_best_only=True, mode='min', verbose=0)]
          )

"""

print("it works!")
#print(history.history.keys())

# R2 plot



fig_acc = plt.figure(figsize=(10, 10))
plt.plot(history.history['r2_keras'])
plt.plot(history.history['val_r2_keras'])
plt.title('model r^2')
plt.ylabel('R^2')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
fig_acc.savefig("./model_r2.png")



# summarize history for MAE
fig_acc = plt.figure(figsize=(10, 10))
plt.plot(history.history['mean_absolute_error'])
plt.plot(history.history['val_mean_absolute_error'])
plt.title('model MAE')
plt.ylabel('MAE')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
fig_acc.savefig("./model_mae.png")

# summarize history for Loss
fig_acc = plt.figure(figsize=(10, 10))
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
fig_acc.savefig("./model_regression_loss.png")



#
#New file goes here
#


def add_new_data(df):
    train1, test1 = separate_data(roth_data, roth_raw_data)

train1, test1 = separate_data(roth_data, roth_raw_data)

test_array_y = np.array(test1["PM10"])
train_array_y = np.array(train1["PM10"])

test_array_x = test1.drop("PM10", axis=1)
train_array_x = train1.drop("PM10", axis=1)


test_array_y = test_array_y[sequence_length:len(test_array_y)]
train_array_y = train_array_y[sequence_length:len(train_array_y)]


#test1 = test1.drop("Date", axis=1)
#test1 = test1.drop("Date", axis=1)

#norm_train_df = pd.DataFrame(min_max_scaler.fit_transform(train_salouel), columns=train_salouel.columns)
#norm_test_df = pd.DataFrame(min_max_scaler.fit_transform(test_salouel), columns=test_salouel.columns)
reshaped_train_array_y = train_array_y.reshape(len(train_array_y), 1)
reshaped_test_array_y = test_array_y.reshape(len(test_array_y), 1)

norm_test_x = pd.DataFrame(min_max_scaler.fit_transform(test_array_x), columns=test_array_x.columns)
norm_test_y = pd.DataFrame(min_max_scaler.fit_transform(reshaped_test_array_y))

norm_train_x = pd.DataFrame(min_max_scaler.fit_transform(train_array_x), columns=test_array_x.columns)
norm_train_y = pd.DataFrame(min_max_scaler.fit_transform(reshaped_train_array_y))




seq_norm_train = gen_sequence(norm_train_x)
seq_norm_test = gen_sequence(norm_test_x)



#####
# Test drop of NaN values
#####



# if best iteration's model was saved then load and use it


import datetime
def write_results(text):
    file = open("results.txt", "w")

    now = datetime.datetime.now()

    with open("test.txt", "a") as file:
        text = now.strftime("%Y-%m-%d %H:%M:%S") + ": " + "\n" + text + "\n" + "\n"
        file.write(text)

if os.path.isfile(model_path):
    estimator = load_model(model_path, custom_objects={'r2_keras': r2_keras})

    # test metrics
    #inversed_train_y = min_max_scaler.inverse_transform(seq_norm_train)
    #inversed_train_x = min_max_scaler.inverse_transform(norm_train_x)
    #inversed_test_x = min_max_scaler.inverse_transform(seq_norm_test)
    #inversed_test_y = min_max_scaler.inverse_transform(norm_test_y) # IMPORTANT!!!


    scores_test = estimator.evaluate(np.array(seq_norm_train), np.array(norm_train_y), verbose=2)
    print('\nMAE: {}'.format(scores_test[1]))
    print('\nR^2: {}'.format(scores_test[2]))
    res = "Sequence length: " + str(sequence_length) + "\nNombre d'epochs: " + str(epochs) + "\nBatch_size: " + str(batch_size) + '\nMAE: {}'.format(scores_test[1]) + '\nR^2: {}'.format(scores_test[2])
    write_results(res)

    y_pred_test = estimator.predict(np.array(seq_norm_test))

    y_true_test = np.array(norm_test_y)

    y_pred_test_inv = min_max_scaler.inverse_transform(y_pred_test)

    y_true_test_inv = min_max_scaler.inverse_transform(y_true_test)


    test_set = pd.DataFrame(y_pred_test_inv)
    test_set.to_csv('./submit_test.csv', index = None)

    # Plot in blue color the predicted data and in green color the
    # actual data to verify visually the accuracy of the model.
    fig_verify = plt.figure(figsize=(100, 50))
    plt.plot(y_pred_test_inv, color="blue")
    plt.plot(y_true_test_inv, color="green")
    plt.title('prediction')
    plt.ylabel('value')
    plt.xlabel('row')
    plt.legend(['predicted', 'actual data'], loc='upper left')
    plt.show()
    fig_verify.savefig("./model_regression_verify.png")
    
    
def make_prediction(df):
        estimator = load_model(model_path, custom_objects={'r2_keras': r2_keras})
        # here goes separation data into X and Y, normalization, etc
        y_pred_test = estimator.predict(np.array(df_x))


