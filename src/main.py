
import pandas as pd
import numpy as np
import tensorflow as tf
tf.compat.v1.disable_v2_behavior()
import pickle
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
import os
import shap
import src.data as data

data_set = "sepsis"  
n_hidden = 8
max_len = 100 
min_len = 3
min_size_prefix = 1
seed = False
num_repetitions = 1
mode = "complete"
val_size = 0.2
train_size = 0.7

hpo = True


def concatenate_tensor_matrix(x_seq, x_stat):
    x_train_seq_ = x_seq.reshape(-1, x_seq.shape[1] * x_seq.shape[2])
    x_concat = np.concatenate((x_train_seq_, x_stat), axis=1)

    return x_concat


def train_rf(x_train_seq, x_train_stat, y_train, x_val_seq, x_val_stat, y_val, hpos, hpo):
    x_concat_train = concatenate_tensor_matrix(x_train_seq, x_train_stat)
    x_concat_val = concatenate_tensor_matrix(x_val_seq, x_val_stat)

    if hpo:
        best_model = ""
        best_hpos = ""
        aucs = []

        for num_trees in hpos["rf"]["num_trees"]:
            for max_depth_trees in hpos["rf"]["max_depth_trees"]:
                for num_rand_vars in hpos["rf"]["num_rand_vars"]:

                    model = RandomForestClassifier(n_estimators=num_trees, max_depth=max_depth_trees,
                                                   max_features=num_rand_vars)
                    model.fit(x_concat_train, np.ravel(y_train))
                    preds_proba = model.predict_proba(x_concat_val)
                    preds_proba = [pred_proba[1] for pred_proba in preds_proba]
                    auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
                    aucs.append(auc)

                    if auc >= max(aucs):
                        best_model = model
                        best_hpos = {"num_trees": num_trees, "max_depth_trees": max_depth_trees,
                                     "num_rand_vars": num_rand_vars}

        f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
        f.write(str(best_hpos))
        f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
        f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
        f.write(f'Std,{np.std(aucs, ddof=1)}\n')
        f.close()

        return best_model, best_hpos

    else:
        x_concat = np.concatenate((x_concat_train, x_concat_val), axis=0)
        y = np.concatenate((y_train, y_val), axis=0)

        model = RandomForestClassifier()
        model.fit(x_concat, np.ravel(y))

        return model


def train_lr(x_train_seq, x_train_stat, y_train, x_val_seq, x_val_stat, y_val, hpos, hpo):
    x_concat_train = concatenate_tensor_matrix(x_train_seq, x_train_stat)
    x_concat_val = concatenate_tensor_matrix(x_val_seq, x_val_stat)

    if hpo:
        best_model = ""
        best_hpos = ""
        aucs = []

        for c in hpos["lr"]["reg_strength"]:
            for solver in hpos["lr"]["solver"]:

                model = LogisticRegression(C=c, solver=solver)
                model.fit(x_concat_train, np.ravel(y_train))
                preds_proba = model.predict_proba(x_concat_val)
                preds_proba = [pred_proba[1] for pred_proba in preds_proba]
                auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
                aucs.append(auc)

                if auc >= max(aucs):
                    best_model = model
                    best_hpos = {"c": c, "solver": solver}

        f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
        f.write(str(best_hpos))
        f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
        f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
        f.write(f'Std,{np.std(aucs, ddof=1)}\n')
        f.close()

        return best_model, best_hpos

    else:
        x_concat = np.concatenate((x_concat_train, x_concat_val), axis=0)
        y = np.concatenate((y_train, y_val), axis=0)

        model = LogisticRegression()
        model.fit(x_concat, np.ravel(y))

        return model


def train_svm(x_train_seq, x_train_stat, y_train, x_val_seq, x_val_stat, y_val, hpos, hpo):
    x_concat_train = concatenate_tensor_matrix(x_train_seq, x_train_stat)
    x_concat_val = concatenate_tensor_matrix(x_val_seq, x_val_stat)

    if hpo:
        best_model = ""
        best_hpos = ""
        aucs = []

        for kern_fkt in hpos["svm"]["kern_fkt"]:
            for cost in hpos["svm"]["cost"]:

                model = SVC(C=cost, kernel=kern_fkt, probability=True)
                model.fit(x_concat_train, np.ravel(y_train))
                preds_proba = model.predict_proba(x_concat_val)
                preds_proba = [pred_proba[1] for pred_proba in preds_proba]
                auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
                aucs.append(auc)

                if auc >= max(aucs):
                    best_model = model
                    best_hpos = {"cost": cost, "kernel": kern_fkt}

        f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
        f.write(str(best_hpos))
        f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
        f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
        f.write(f'Std,{np.std(aucs, ddof=1)}\n')
        f.close()

        return best_model, best_hpos

    else:
        x_concat = np.concatenate((x_concat_train, x_concat_val), axis=0)
        y = np.concatenate((y_train, y_val), axis=0)

        model = SVC(probability=True)
        model.fit(x_concat, np.ravel(y))

        return model


def train_gb(x_train_seq, x_train_stat, y_train, x_val_seq, x_val_stat, y_val, hpos, hpo):
    x_concat_train = concatenate_tensor_matrix(x_train_seq, x_train_stat)
    x_concat_val = concatenate_tensor_matrix(x_val_seq, x_val_stat)

    if hpo:
        best_model = ""
        best_hpos = ""
        aucs = []

        for n_estimators in hpos["gb"]["n_estimators"]:
            for learning_rate in hpos["gb"]["learning_rate"]:

                model = GradientBoostingClassifier(n_estimators=n_estimators, learning_rate=learning_rate)
                model.fit(x_concat_train, np.ravel(y_train))
                preds_proba = model.predict_proba(x_concat_val)
                preds_proba = [pred_proba[1] for pred_proba in preds_proba]
                auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
                aucs.append(auc)

                if auc >= max(aucs):
                    best_model = model
                    best_hpos = {"n_estimators": n_estimators, "learning_rate": learning_rate}

        f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
        f.write(str(best_hpos))
        f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
        f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
        f.write(f'Std,{np.std(aucs, ddof=1)}\n')
        f.close()

        return best_model, best_hpos

    else:
        x_concat = np.concatenate((x_concat_train, x_concat_val), axis=0)
        y = np.concatenate((y_train, y_val), axis=0)

        model = GradientBoostingClassifier()
        model.fit(x_concat, np.ravel(y))

        return model


def train_ada(x_train_seq, x_train_stat, y_train, x_val_seq, x_val_stat, y_val, hpos, hpo):
    x_concat_train = concatenate_tensor_matrix(x_train_seq, x_train_stat)
    x_concat_val = concatenate_tensor_matrix(x_val_seq, x_val_stat)

    if hpo:
        best_model = ""
        best_hpos = ""
        aucs = []

        for n_estimators in hpos["ada"]["n_estimators"]:
            for learning_rate in hpos["ada"]["learning_rate"]:

                model = AdaBoostClassifier(n_estimators=n_estimators, learning_rate=learning_rate)
                model.fit(x_concat_train, np.ravel(y_train))
                preds_proba = model.predict_proba(x_concat_val)
                preds_proba = [pred_proba[1] for pred_proba in preds_proba]
                auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
                aucs.append(auc)

                if auc >= max(aucs):
                    best_model = model
                    best_hpos = {"n_estimators": n_estimators, "learning_rate": learning_rate}

        f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
        f.write(str(best_hpos) + '\n')
        f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
        f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
        f.write(f'Std,{np.std(aucs, ddof=1)}\n')
        f.close()

        return best_model, best_hpos

    else:
        x_concat = np.concatenate((x_concat_train, x_concat_val), axis=0)
        y = np.concatenate((y_train, y_val), axis=0)

        model = AdaBoostClassifier()
        model.fit(x_concat, np.ravel(y))

        return model


def train_nb(x_train_seq, x_train_stat, y_train, x_val_seq, x_val_stat, y_val, hpos, hpo):
    x_concat_train = concatenate_tensor_matrix(x_train_seq, x_train_stat)
    x_concat_val = concatenate_tensor_matrix(x_val_seq, x_val_stat)

    if hpo:
        best_model = ""
        best_hpos = ""
        aucs = []

        for var_smoothing in hpos["nb"]["var_smoothing"]:

            model = GaussianNB(var_smoothing=var_smoothing)
            model.fit(x_concat_train, np.ravel(y_train))
            preds_proba = model.predict_proba(x_concat_val)
            preds_proba = [pred_proba[1] for pred_proba in preds_proba]
            auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
            aucs.append(auc)

            if auc >= max(aucs):
                best_model = model
                best_hpos = {"var_smoothing": var_smoothing}

        f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
        f.write(str(best_hpos) + '\n')
        f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
        f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
        f.write(f'Std,{np.std(aucs, ddof=1)}\n')
        f.close()

        return best_model, best_hpos

    else:
        x_concat = np.concatenate((x_concat_train, x_concat_val), axis=0)
        y = np.concatenate((y_train, y_val), axis=0)

        model = GaussianNB()
        model.fit(x_concat, np.ravel(y))

        return model


def train_knn(x_train_seq, x_train_stat, y_train, x_val_seq, x_val_stat, y_val, hpos, hpo):
    x_concat_train = concatenate_tensor_matrix(x_train_seq, x_train_stat)
    x_concat_val = concatenate_tensor_matrix(x_val_seq, x_val_stat)

    if hpo:
        best_model = ""
        best_hpos = ""
        aucs = []

        for n_neighbors in hpos["knn"]["n_neighbors"]:

            model = KNeighborsClassifier(n_neighbors=n_neighbors)
            model.fit(x_concat_train, np.ravel(y_train))
            preds_proba = model.predict_proba(x_concat_val)
            preds_proba = [pred_proba[1] for pred_proba in preds_proba]
            auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
            aucs.append(auc)

            if auc >= max(aucs):
                best_model = model
                best_hpos = {"n_eighbors": n_neighbors}

        f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
        f.write(str(best_hpos) + '\n')
        f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
        f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
        f.write(f'Std,{np.std(aucs, ddof=1)}\n')
        f.close()

        return best_model, best_hpos

    else:
        x_concat = np.concatenate((x_concat_train, x_concat_val), axis=0)
        y = np.concatenate((y_train, y_val), axis=0)

        model = KNeighborsClassifier()
        model.fit(x_concat, np.ravel(y))

        return model


def train_lstm(x_train_seq, x_train_stat, y_train, x_val_seq=False, x_val_stat=False, y_val=False, hpos=False,
               hpo=False, mode="complete"):
    max_case_len = x_train_seq.shape[1]
    num_features_seq = x_train_seq.shape[2]
    num_features_stat = x_train_stat.shape[1]

    if mode == "complete":

        if hpo:
            best_model = ""
            best_hpos = ""
            aucs = []

            for size in hpos["complete"]["size"]:
                for learning_rate in hpos["complete"]["learning_rate"]:
                    for batch_size in hpos["complete"]["batch_size"]:

                        input_layer_seq = tf.keras.layers.Input(shape=(max_case_len, num_features_seq),
                                                                name='seq_input_layer')
                        input_layer_static = tf.keras.layers.Input(shape=(num_features_stat), name='static_input_layer')

                        hidden_layer = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(
                            units=size,
                            return_sequences=False))(input_layer_seq)

                        concatenate_layer = tf.keras.layers.Concatenate(axis=1)([hidden_layer, input_layer_static])

                        output_layer = tf.keras.layers.Dense(1,
                                                             activation='sigmoid',
                                                             name='output_layer')(concatenate_layer)

                        model = tf.keras.models.Model(inputs=[input_layer_seq, input_layer_static],
                                                      outputs=[output_layer])

                        opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)

                        model.compile(loss='binary_crossentropy',
                                      optimizer=opt,
                                      metrics=['accuracy'])
                        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
                        model_checkpoint = tf.keras.callbacks.ModelCheckpoint('../model/model.ckpt',
                                                                              monitor='val_loss',
                                                                              verbose=0,
                                                                              save_best_only=True,
                                                                              save_weights_only=False,
                                                                              mode='auto')

                        lr_reducer = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
                                                                          factor=0.5,
                                                                          patience=10,
                                                                          verbose=0,
                                                                          mode='auto',
                                                                          min_delta=0.0001,
                                                                          cooldown=0,
                                                                          min_lr=0)

                        model.summary()
                        model.fit([x_train_seq, x_train_stat], y_train,
                                  validation_data=([x_val_seq, x_val_stat], y_val),
                                  verbose=1,
                                  callbacks=[early_stopping, model_checkpoint, lr_reducer],
                                  batch_size=batch_size,
                                  epochs=100)

                        preds_proba = model.predict([x_val_seq, x_val_stat])
                        preds_proba = [pred_proba[0] for pred_proba in preds_proba]

                        auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
                        aucs.append(auc)

                        if auc >= max(aucs):
                            best_model = model
                            best_hpos = {"size": size, "learning_rate": learning_rate, "batch_size": batch_size}

            f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
            f.write(str(best_hpos) + '\n')
            f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
            f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
            f.write(f'Std,{np.std(aucs, ddof=1)}\n')
            f.close()

            return best_model, best_hpos

        else:
            input_layer_seq = tf.keras.layers.Input(shape=(max_case_len, num_features_seq), name='seq_input_layer')
            input_layer_static = tf.keras.layers.Input(shape=(num_features_stat), name='static_input_layer')

            hidden_layer = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(
                units=hpos['size'],
                return_sequences=False))(input_layer_seq)

            concatenate_layer = tf.keras.layers.Concatenate(axis=1)([hidden_layer, input_layer_static])

            output_layer = tf.keras.layers.Dense(1,
                                                 activation='sigmoid',
                                                 name='output_layer')(concatenate_layer)

            model = tf.keras.models.Model(inputs=[input_layer_seq, input_layer_static],
                                          outputs=[output_layer])

            opt = tf.keras.optimizers.Adam(learning_rate=hpos['learning_rate'])
            model.compile(loss='binary_crossentropy',
                          optimizer=opt,
                          metrics=['accuracy'])
            early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
            model_checkpoint = tf.keras.callbacks.ModelCheckpoint('../model/model.ckpt',
                                                                  monitor='val_loss',
                                                                  verbose=0,
                                                                  save_best_only=True,
                                                                  save_weights_only=False,
                                                                  mode='auto')

            lr_reducer = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
                                                              factor=0.5,
                                                              patience=10,
                                                              verbose=0,
                                                              mode='auto',
                                                              min_delta=0.0001,
                                                              cooldown=0,
                                                              min_lr=0)

            model.summary()
            model.fit([x_train_seq, x_train_stat], y_train,
                      validation_data=([x_val_seq, x_val_stat], y_val),
                      verbose=1,
                      callbacks=[early_stopping, model_checkpoint, lr_reducer],
                      batch_size=hpos['batch_size'],
                      epochs=100)

            return model

    if mode == "static":

        if hpo:
            best_model = ""
            best_hpos = ""
            aucs = []

            for learning_rate in hpos["complete"]["learning_rate"]:
                for batch_size in hpos["complete"]["batch_size"]:

                    input_layer_static = tf.keras.layers.Input(shape=(num_features_stat), name='static_input_layer')

                    output_layer = tf.keras.layers.Dense(1,
                                                         activation='sigmoid',
                                                         name='output_layer')(input_layer_static)

                    model = tf.keras.models.Model(inputs=[input_layer_static],
                                                  outputs=[output_layer])

                    opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)

                    model.compile(loss='binary_crossentropy',
                                  optimizer=opt,
                                  metrics=['accuracy'])
                    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
                    model_checkpoint = tf.keras.callbacks.ModelCheckpoint('../model/model.ckpt',
                                                                          monitor='val_loss',
                                                                          verbose=0,
                                                                          save_best_only=True,
                                                                          save_weights_only=False,
                                                                          mode='auto')

                    lr_reducer = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
                                                                      factor=0.5,
                                                                      patience=10,
                                                                      verbose=0,
                                                                      mode='auto',
                                                                      min_delta=0.0001,
                                                                      cooldown=0,
                                                                      min_lr=0)

                    model.summary()
                    model.fit([x_train_stat], y_train,
                              validation_data=([x_val_stat], y_val),
                              verbose=1,
                              callbacks=[early_stopping, model_checkpoint, lr_reducer],
                              batch_size=batch_size,
                              epochs=100)

                    preds_proba = model.predict([x_val_stat])
                    preds_proba = [pred_proba[0] for pred_proba in preds_proba]

                    auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
                    aucs.append(auc)

                    if auc >= max(aucs):
                        best_model = model
                        best_hpos = {"learning_rate": learning_rate, "batch_size": batch_size}

            f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
            f.write(str(best_hpos) + '\n')
            f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
            f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
            f.write(f'Std,{np.std(aucs, ddof=1)}\n')
            f.close()

            return best_model, best_hpos

        else:
            input_layer_static = tf.keras.layers.Input(shape=(num_features_stat), name='static_input_layer')

            output_layer = tf.keras.layers.Dense(1,
                                                 activation='sigmoid',
                                                 name='output_layer')(input_layer_static)

            model = tf.keras.models.Model(inputs=[input_layer_static],
                                          outputs=[output_layer])

            opt = tf.keras.optimizers.Adam(learning_rate=0.001)
            model.compile(loss='binary_crossentropy',
                          optimizer=opt,
                          metrics=['accuracy'])
            early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
            model_checkpoint = tf.keras.callbacks.ModelCheckpoint('../model/model.ckpt',
                                                                  monitor='val_loss',
                                                                  verbose=0,
                                                                  save_best_only=True,
                                                                  save_weights_only=False,
                                                                  mode='auto')

            lr_reducer = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
                                                              factor=0.5,
                                                              patience=10,
                                                              verbose=0,
                                                              mode='auto',
                                                              min_delta=0.0001,
                                                              cooldown=0,
                                                              min_lr=0)

            model.summary()
            model.fit([x_train_stat], y_train,
                      validation_data=([x_val_seq, x_val_stat], y_val),
                      verbose=1,
                      callbacks=[early_stopping, model_checkpoint, lr_reducer],
                      batch_size=32,
                      epochs=100)

            return model

    if mode == "sequential":

        if hpo:
            best_model = ""
            best_hpos = ""
            aucs = []

            for size in hpos["complete"]["size"]:
                for learning_rate in hpos["complete"]["learning_rate"]:
                    for batch_size in hpos["complete"]["batch_size"]:

                        input_layer_seq = tf.keras.layers.Input(shape=(max_case_len, num_features_seq),
                                                                name='seq_input_layer')

                        hidden_layer = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(
                            units=size,
                            return_sequences=False))(input_layer_seq)

                        output_layer = tf.keras.layers.Dense(1,
                                                             activation='sigmoid',
                                                             name='output_layer')(hidden_layer)

                        model = tf.keras.models.Model(inputs=[input_layer_seq],
                                                      outputs=[output_layer])

                        opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)

                        model.compile(loss='binary_crossentropy',
                                      optimizer=opt,
                                      metrics=['accuracy'])

                        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
                        model_checkpoint = tf.keras.callbacks.ModelCheckpoint('../model/model.ckpt',
                                                                              monitor='val_loss',
                                                                              verbose=0,
                                                                              save_best_only=True,
                                                                              save_weights_only=False,
                                                                              mode='auto')

                        lr_reducer = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
                                                                          factor=0.5,
                                                                          patience=10,
                                                                          verbose=0,
                                                                          mode='auto',
                                                                          min_delta=0.0001,
                                                                          cooldown=0,
                                                                          min_lr=0)

                        model.summary()
                        model.fit([x_train_seq], y_train,
                                  validation_data=([x_val_seq, x_val_stat], y_val),
                                  verbose=1,
                                  callbacks=[early_stopping, model_checkpoint, lr_reducer],
                                  batch_size=batch_size,
                                  epochs=100)

                        preds_proba = model.predict([x_val_seq, x_val_stat])
                        preds_proba = [pred_proba[0] for pred_proba in preds_proba]

                        auc = metrics.roc_auc_score(y_true=y_val, y_score=preds_proba)
                        aucs.append(auc)

                        if auc >= max(aucs):
                            best_model = model
                            best_hpos = {"size": size, "learning_rate": learning_rate, "batch_size": batch_size}

            f = open(f'../output/{data_set}_{mode}_{target_activity}_hpos.txt', 'a+')
            f.write(str(best_hpos) + '\n')
            f.write("Validation aucs," + ",".join([str(x) for x in aucs]) + '\n')
            f.write(f'Avg,{sum(aucs) / len(aucs)}\n')
            f.write(f'Std,{np.std(aucs, ddof=1)}\n')
            f.close()

            return best_model, best_hpos

        else:

            input_layer_seq = tf.keras.layers.Input(shape=(max_case_len, num_features_seq), name='seq_input_layer')

            hidden_layer = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(
                units=4,
                return_sequences=False))(input_layer_seq)

            output_layer = tf.keras.layers.Dense(1,
                                                 activation='sigmoid',
                                                 name='output_layer')(hidden_layer)

            model = tf.keras.models.Model(inputs=[input_layer_seq],
                                          outputs=[output_layer])

            opt = tf.keras.optimizers.Adam(learning_rate=0.001)
            model.compile(loss='binary_crossentropy',
                          optimizer=opt,
                          metrics=['accuracy'])
            early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
            model_checkpoint = tf.keras.callbacks.ModelCheckpoint('../model/model.ckpt',
                                                                  monitor='val_loss',
                                                                  verbose=0,
                                                                  save_best_only=True,
                                                                  save_weights_only=False,
                                                                  mode='auto')

            lr_reducer = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
                                                              factor=0.5,
                                                              patience=10,
                                                              verbose=0,
                                                              mode='auto',
                                                              min_delta=0.0001,
                                                              cooldown=0,
                                                              min_lr=0)

            model.summary()
            model.fit([x_train_seq], y_train,
                      validation_data=([x_val_seq, x_val_stat], y_val),
                      verbose=1,
                      callbacks=[early_stopping, model_checkpoint, lr_reducer],
                      batch_size=32,
                      epochs=100)

            return model


def correct_static(seq, seqs_time, idx_sample, idx_time):

    features = seqs_time[0][0].index._values

    for idx, feature in enumerate(features):
        if feature == "age":
            seq[idx] = seqs_time[idx_sample][idx_time][feature]

        elif feature == "gender" or feature == "ethnicity":
            pass
        elif feature in ['admission_type', 'marital_status', 'language', 'religion', 'insurance']:
            seq[idx] = seqs_time[idx_sample][idx_time][feature]
        else:
            seq[idx] = seqs_time[idx_sample][idx_time][feature]
    return seq


def time_step_blow_up(X_seq, X_stat, y, max_len, ts_info=False, x_time=None, x_time_vals=None, x_statics_vals_corr=None):

    X_seq_prefix, X_stat_prefix, y_prefix, x_time_vals_prefix, ts = [], [], [], [], []

    for idx_seq in range(0, len(X_seq)):
        for idx_ts in range(min_size_prefix, len(X_seq[idx_seq]) + 1):
            X_seq_prefix.append(X_seq[idx_seq][0:idx_ts])
            X_stat_prefix.append(X_stat[idx_seq])
            y_prefix.append(y[idx_seq])
            if x_time is not None:
                x_time_vals_prefix.append(x_time_vals[idx_seq][0:idx_ts])
            ts.append(idx_ts)

    
    # Remove prefixes with future event from training set
    if x_time is not None:
        X_seq_prefix_temp, X_stat_prefix_temp, y_prefix_temp, ts_temp = [], [], [], []

        for idx_prefix in range(0, len(X_seq_prefix)):
            if x_time_vals_prefix[idx_prefix][-1].value <= x_time.value:
                X_seq_prefix_temp.append(X_seq_prefix[idx_prefix])
                X_stat_prefix_temp.append(X_stat_prefix[idx_prefix])
                y_prefix_temp.append(y_prefix[idx_prefix])
                ts_temp.append(ts[idx_prefix])

        X_seq_prefix, X_stat_prefix, y_prefix, ts = X_seq_prefix_temp, X_stat_prefix_temp, y_prefix_temp, ts_temp

    # Vectorization
    X_seq_final = np.zeros((len(X_seq_prefix), max_len, len(X_seq_prefix[0][0])), dtype=np.float32)
    X_stat_final = np.zeros((len(X_seq_prefix), len(X_stat_prefix[0])))
    for i, x in enumerate(X_seq_prefix):
        X_seq_final[i, :len(x), :] = np.array(x)
        X_stat_final[i, :] = np.array(X_stat_prefix[i])
    y_final = np.array(y_prefix).astype(np.int32)

    if ts_info:
        return X_seq_final, X_stat_final, y_final, ts
    else:
        return X_seq_final, X_stat_final, y_final


def evaluate_on_cut(x_seqs, x_statics, y, mode, target_activity, data_set, hpos, hpo, x_time=None, x_statics_vals_corr=None):
    data_index = list(range(0, len(y)))
    val_index = data_index[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))]
    test_index = data_index[int(train_size * len(y)):]

    if x_time is not None:
        time_start_val = x_time[val_index[0]][0]
        time_start_test = x_time[test_index[0]][0]
        x_time_train = x_time[0: int(train_size * (1 - val_size) * len(y))]
        x_time_val = x_time[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))]

    results = {}
    best_hpos_repetitions = ""

    for repetition in range(0, num_repetitions):

        # Timestamp exists
        if x_time is not None:
            if x_statics_vals_corr is not None:
                X_train_seq, X_train_stat, y_train = time_step_blow_up(x_seqs[0: int(train_size * (1 - val_size) * len(y))],
                                                                       x_statics[0: int(train_size * (1 - val_size) * len(y))],
                                                                       y[0: int(train_size * (1 - val_size) * len(y))],
                                                                       max_len,
                                                                       ts_info=False,
                                                                       x_time=time_start_val,
                                                                       x_time_vals=x_time_train,
                                                                       x_statics_vals_corr=x_statics_vals_corr[0: int(train_size * (1 - val_size) * len(y))])

                X_val_seq, X_val_stat, y_val = time_step_blow_up(
                    x_seqs[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                    x_statics[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                    y[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                    max_len,
                    ts_info=False,
                    x_time=time_start_test,
                    x_time_vals=x_time_val,
                    x_statics_vals_corr=x_statics_vals_corr[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))])

            else:
                X_train_seq, X_train_stat, y_train = time_step_blow_up(
                    x_seqs[0: int(train_size * (1 - val_size) * len(y))],
                    x_statics[0: int(train_size * (1 - val_size) * len(y))],
                    y[0: int(train_size * (1 - val_size) * len(y))],
                    max_len,
                    ts_info=False,
                    x_time=time_start_val,
                    x_time_vals=x_time_train,
                    x_statics_vals_corr=None)

                X_val_seq, X_val_stat, y_val = time_step_blow_up(
                    x_seqs[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                    x_statics[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                    y[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                    max_len,
                    ts_info=False,
                    x_time=time_start_test,
                    x_time_vals=x_time_val,
                    x_statics_vals_corr=None)

        # No timestamp exists
        else:
            X_train_seq, X_train_stat, y_train = time_step_blow_up(x_seqs[0: int(train_size * (1 - val_size) * len(y))],
                                                                   x_statics[
                                                                   0: int(train_size * (1 - val_size) * len(y))],
                                                                   y[0: int(train_size * (1 - val_size) * len(y))],
                                                                   max_len)

            X_val_seq, X_val_stat, y_val = time_step_blow_up(
                x_seqs[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                x_statics[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                y[int(train_size * (1 - val_size) * len(y)): int(train_size * len(y))],
                max_len)

        if x_statics_vals_corr is not None:
            X_test_seq, X_test_stat, y_test, ts = time_step_blow_up(x_seqs[int(train_size * len(y)):],
                                                                    x_statics[int(train_size * len(y)):],
                                                                    y[int(train_size * len(y)):],
                                                                    max_len,
                                                                    ts_info=True,
                                                                    x_statics_vals_corr=x_statics_vals_corr[int(train_size * len(y)):])
        else:
            X_test_seq, X_test_stat, y_test, ts = time_step_blow_up(x_seqs[int(train_size * len(y)):],
                                                                    x_statics[int(train_size * len(y)):],
                                                                    y[int(train_size * len(y)):],
                                                                    max_len,
                                                                    ts_info=True,
                                                                    x_statics_vals_corr=None)

        print(0)

        if mode == "complete":
            model, best_hpos = train_lstm(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                          y_val.reshape(-1, 1), hpos, hpo, mode)
            preds_proba = model.predict([X_test_seq, X_test_stat])
            results['preds'] = [int(round(pred[0])) for pred in preds_proba]
            results['preds_proba'] = [pred_proba[0] for pred_proba in preds_proba]

        elif mode == "static":
            model, best_hpos = train_lstm(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                          y_val.reshape(-1, 1), hpos, hpo, mode)
            preds_proba = model.predict([X_test_stat])
            results['preds'] = [int(round(pred[0])) for pred in preds_proba]
            results['preds_proba'] = [pred_proba[0] for pred_proba in preds_proba]

        elif mode == "sequential":
            model, best_hpos = train_lstm(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                          y_val.reshape(-1, 1), hpos, hpo, mode)
            preds_proba = model.predict([X_test_seq])
            results['preds'] = [int(round(pred[0])) for pred in preds_proba]
            results['preds_proba'] = [pred_proba[0] for pred_proba in preds_proba]

        elif mode == "rf":
            model, best_hpos = train_rf(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                        y_val.reshape(-1, 1), hpos, hpo)
            preds_proba = model.predict_proba(concatenate_tensor_matrix(X_test_seq, X_test_stat))
            results['preds'] = [np.argmax(pred_proba) for pred_proba in preds_proba]
            results['preds_proba'] = [pred_proba[1] for pred_proba in preds_proba]

        elif mode == "lr":
            model, best_hpos = train_lr(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                        y_val.reshape(-1, 1), hpos, hpo)
            preds_proba = model.predict_proba(concatenate_tensor_matrix(X_test_seq, X_test_stat))
            results['preds'] = [np.argmax(pred_proba) for pred_proba in preds_proba]
            results['preds_proba'] = [pred_proba[1] for pred_proba in preds_proba]

        elif mode == "svm":
            model, best_hpos = train_svm(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                         y_val.reshape(-1, 1), hpos, hpo)
            preds_proba = model.predict_proba(concatenate_tensor_matrix(X_test_seq, X_test_stat))
            results['preds'] = [np.argmax(pred_proba) for pred_proba in preds_proba]
            results['preds_proba'] = [pred_proba[1] for pred_proba in preds_proba]

        elif mode == "gb":
            model, best_hpos = train_gb(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                        y_val.reshape(-1, 1), hpos, hpo)
            preds_proba = model.predict_proba(concatenate_tensor_matrix(X_test_seq, X_test_stat))
            results['preds'] = [np.argmax(pred_proba) for pred_proba in preds_proba]
            results['preds_proba'] = [pred_proba[1] for pred_proba in preds_proba]

        elif mode == "ada":
            model, best_hpos = train_ada(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                         y_val.reshape(-1, 1), hpos, hpo)
            preds_proba = model.predict_proba(concatenate_tensor_matrix(X_test_seq, X_test_stat))
            results['preds'] = [np.argmax(pred_proba) for pred_proba in preds_proba]
            results['preds_proba'] = [pred_proba[1] for pred_proba in preds_proba]

        elif mode == "nb":
            model, best_hpos = train_nb(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                        y_val.reshape(-1, 1), hpos, hpo)
            preds_proba = model.predict_proba(concatenate_tensor_matrix(X_test_seq, X_test_stat))
            results['preds'] = [np.argmax(pred_proba) for pred_proba in preds_proba]
            results['preds_proba'] = [pred_proba[1] for pred_proba in preds_proba]


        elif mode == "knn":
            model, best_hpos = train_knn(X_train_seq, X_train_stat, y_train.reshape(-1, 1), X_val_seq, X_val_stat,
                                         y_val.reshape(-1, 1), hpos, hpo)
            preds_proba = model.predict_proba(concatenate_tensor_matrix(X_test_seq, X_test_stat))
            results['preds'] = [np.argmax(pred_proba) for pred_proba in preds_proba]
            results['preds_proba'] = [pred_proba[1] for pred_proba in preds_proba]

        results['gts'] = [int(y) for y in y_test]
        results['ts'] = ts

        results_temp = pd.DataFrame(
            list(zip(results['ts'],
                     results['preds'],
                     results['preds_proba'],
                     results['gts'])),
            columns=['ts', 'preds', 'preds_proba', 'gts'])

        cut_lengths = range(0, max_len - 1)

        # Init
        if cut_lengths[0] not in results:
            for cut_len in cut_lengths:
                results[cut_len] = {}
                results[cut_len]['acc'] = list()
                results[cut_len]['auc'] = list()
                results['all'] = {}
                results['all']['rep'] = list()
                results['all']['auc'] = list()

        # Metrics per cut
        for cut_len in cut_lengths:
            results_temp_cut = results_temp[results_temp.ts == cut_len]

            if not results_temp_cut.empty:  # if cut length is longer than max trace length
                results[cut_len]['acc'].append(
                    metrics.accuracy_score(y_true=results_temp_cut['gts'], y_pred=results_temp_cut['preds']))
                try:
                    results[cut_len]['auc'].append(
                        metrics.roc_auc_score(y_true=results_temp_cut['gts'], y_score=results_temp_cut['preds_proba']))
                except:
                    pass

        # Metrics across cuts
        results['all']['rep'].append(
            metrics.classification_report(y_true=results_temp['gts'], y_pred=results_temp['preds'], output_dict=True))

        try:
            auc = metrics.roc_auc_score(y_true=results_temp['gts'], y_score=results_temp['preds_proba'])
            results['all']['auc'].append(auc)

            if auc >= max(results['all']['auc']):
                best_hpos_repetitions = best_hpos

        except:
            pass

    # Save all results
    f = open(f'../output/{data_set}_{mode}_{target_activity}_summary.txt', 'w')
    results_ = results
    del results_['preds'], results_['preds_proba'], results_['gts'], results_['ts']
    f.write(str(results_))
    f.close()

    # print metrics
    metrics_ = ["auc", "precision", "recall", "f1-score", "support", "accuracy"]
    labels = ["0", "1"]

    for metric_ in metrics_:
        vals = []
        if metric_ == "auc":
            try:
                f = open(f'../output/{data_set}_{mode}_{target_activity}.txt', "a+")
                f.write(metric_ + '\n')
                print(metric_)
                for idx_ in range(0, num_repetitions):
                    vals.append(results['all']['auc'][idx_])
                    f.write(f'{idx_},{vals[-1]}\n')
                    print(f'{idx_},{vals[-1]}')
                f.write(f'Avg,{sum(vals) / len(vals)}\n')
                f.write(f'Std,{np.std(vals, ddof=1)}\n')
                print(f'Avg,{sum(vals) / len(vals)}')
                print(f'Std,{np.std(vals, ddof=1)}\n')
                f.close()

            except:
                pass

        elif metric_ == "accuracy":
            f = open(f'../output/{data_set}_{mode}_{target_activity}.txt', "a+")
            f.write(metric_ + '\n')
            print(metric_)
            for idx_ in range(0, num_repetitions):
                vals.append(results['all']['rep'][idx_][metric_])
                f.write(f'{idx_},{vals[-1]}\n')
                print(f'{idx_},{vals[-1]}')
            f.write(f'Avg,{sum(vals) / len(vals)}\n')
            f.write(f'Std,{np.std(vals, ddof=1)}\n')
            print(f'Avg,{sum(vals) / len(vals)}')
            print(f'Std,{np.std(vals, ddof=1)}\n')
            f.close()
        else:
            for label in labels:
                try:
                    f = open(f'../output/{data_set}_{mode}_{target_activity}.txt', "a+")
                    f.write(metric_ + f' ({label})\n')
                    print(metric_ + f' ({label})')
                    vals = []
                    for idx_ in range(0, num_repetitions):
                        vals.append(results['all']['rep'][idx_][label][metric_])
                        f.write(f'{idx_},{vals[-1]}\n')
                        print(f'{idx_},{vals[-1]}')
                    f.write(f'Avg,{sum(vals) / len(vals)}\n')
                    f.write(f'Std,{np.std(vals, ddof=1)}\n')
                    print(f'Avg,{sum(vals) / len(vals)}')
                    print(f'Std,{np.std(vals, ddof=1)}')
                    f.close()
                except:
                    pass

    return X_train_seq, X_train_stat, y_train, X_val_seq, X_val_stat, y_val, best_hpos_repetitions


def run_coefficient(x_seqs_train, x_statics_train, y_train, x_seqs_val, x_statics_val, y_val, target_activity,
                    static_features, best_hpos_repetitions):
    model = train_lstm(x_seqs_train, x_statics_train, y_train, x_seqs_val, x_statics_val, y_val, best_hpos_repetitions,
                       False, mode="complete")
    output_weights = model.get_layer(name='output_layer').get_weights()[0].flatten()[2 * best_hpos_repetitions['size']:]
    output_names = static_features

    f = open(f'../output/{data_set}_{mode}_{target_activity}_coef.txt', 'w')
    f.write(",".join([str(x) for x in output_names]) + '\n')
    f.write(",".join([str(x) for x in output_weights]))
    f.close()

    return model


#gpus = tf.config.experimental.list_physical_devices('GPU')
#for gpu in gpus:
#    tf.config.experimental.set_memory_growth(gpu, True)

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


hpos = {
    "complete": {"size": [8, 16], "learning_rate": [0.0005, 0.001], "batch_size": [128]},
    "sequential": {"size": [8, 16], "learning_rate": [0.0005, 0.001], "batch_size": [128]},
    "static": {"learning_rate": [0.0005, 0.001], "batch_size": [128]},
    "lr": {"reg_strength": [pow(10, -3), pow(10, -2), pow(10, -1), pow(10, 0), pow(10, 1), pow(10, 2), pow(10, 3)], "solver": ["lbfgs"]},
    "rf": {"num_trees": [100, 200, 500], "max_depth_trees": [2, 5, 10], "num_rand_vars": [1, 3, 5, 10]},
    # "svm": {"kern_fkt": ["linear", "rbf"], "cost": [pow(10, -3), pow(10, -2), pow(10, -1), pow(10, 0), pow(10, 1), pow(10, 2), pow(10, 3)]},
    "gb": {"n_estimators": [100, 200, 500], "learning_rate": [0.01, 0.05, 0.1]},
    "ada": {"n_estimators": [50, 100, 200], "learning_rate": [0.1, 0.5, 1.0]},
    "nb": {"var_smoothing": [pow(1, -9)]},
    "knn": {"n_neighbors": [3, 5, 10, 15]}
}

if data_set == "sepsis":

    for mode in ['complete']:  # 'complete', 'static', 'sequential', 'lr', 'rf', 'gb', 'ada', 'knn', 'nb'
        for target_activity in ['Admission IC']:

            x_seqs, x_statics, y, x_time_vals_final, seq_features, static_features = data.get_sepsis_data(
                target_activity, max_len, min_len)

            # Run eval on cuts to plot results --> Figure 1
            x_seqs_train, x_statics_train, y_train, x_seqs_val, x_statics_val, y_val, best_hpos_repetitions = evaluate_on_cut(
                x_seqs, x_statics, y, mode, target_activity,
                data_set, hpos, hpo, x_time=x_time_vals_final, x_statics_vals_corr=None)

            if mode == "complete":
                # Train model and plot linear coef
                model = run_coefficient(x_seqs_train, x_statics_train, y_train, x_seqs_val, x_statics_val, y_val,
                                        target_activity, static_features, best_hpos_repetitions)

                x_seqs_train = x_seqs_train[0:1000]
                x_statics_train = x_statics_train[0:1000]

                # Get Explanations for LSTM inputs
                explainer = shap.DeepExplainer(model, [x_seqs_train, x_statics_train])
                shap_values = explainer.shap_values([x_seqs_train, x_statics_train])

                seqs_df = pd.DataFrame(data=x_seqs_train.reshape(-1, len(seq_features)),
                                       columns=seq_features)
                seq_shaps = pd.DataFrame(data=shap_values[0][0].reshape(-1, len(seq_features)),
                                         columns=[f'SHAP {x}' for x in seq_features])
                seq_value_shape = pd.concat([seqs_df, seq_shaps], axis=1)

                with open(f'../output/{data_set}_{mode}_{target_activity}_shap.npy', 'wb') as f:
                    pickle.dump(seq_value_shape, f)

else:
    print("Data set not available!")
