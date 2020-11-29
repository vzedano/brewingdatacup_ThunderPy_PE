#!/usr/local/env python
import tempfile
import pandas as pd
import os
import configparser

# For data split and imbalanced data
from sklearn.model_selection import train_test_split
from imblearn.combine import SMOTETomek
from sklearn import preprocessing

# For Random Forest testing
import h2o

import numpy as np

pd.set_option("display.max_rows", 100)
default_config_path = './config/config-vlad.ini'
input_config_path = input(
    'Please, specify a config path for the script ({}): '.format(default_config_path))
config_path = default_config_path if input_config_path == '' else input_config_path

config = configparser.ConfigParser()
config.read_file(open(config_path))

client_attributes_file_path = config['data-files']['clients_attributes']
active_promos_file_path = config['data-files']['active_promos']
executed_promos_file_path = config['data-files']['executed_promos']
sales_file_path = config['data-files']['sales']

sales = pd.read_csv(sales_file_path, encoding='latin-1')
executed_promos = pd.read_csv(executed_promos_file_path, encoding='latin-1')
active_promos = pd.read_csv(active_promos_file_path, encoding='latin-1')
clients_attributes = pd.read_csv(
    client_attributes_file_path, encoding='latin-1')

sanitized_executed_promos = executed_promos.drop_duplicates(
    subset=['Cliente', 'Marca', 'Cupo'])

sales_exec_promos = sales.merge(sanitized_executed_promos, how='left', on=[
                                'Cliente', 'Marca', 'Cupo'])

sales_exec_promos.loc[
    sales_exec_promos['CodigoDC'].isnull() == False, 'ES_PROMO'] = 'SI'


df = sales_exec_promos.merge(clients_attributes, how='left', on='Cliente')

# This is the final dataframe we will analyze as part of the challenge
final_df = df[['Cliente', 'Marca', 'Cupo', 'Region', 'Gerencia', 'SubCanal', 'TipoPoblacion', 'Estrato', 'EF', 'ES_PROMO']].fillna({
    'ES_PROMO': 'NO',
    'Cupo': df['Cupo'].mode()[0]
})

final_df

h2o.init(nthreads=-1)

trgt_index = final_df.columns.tolist().index('ES_PROMO')

x_to_split, y_to_split = final_df.iloc[:,
                                       0:trgt_index].values, final_df.iloc[:, trgt_index].values

# Split data to balance the target rows in the train data.
x_train_st, x_test, y_train_st, y_test = train_test_split(x_to_split,
                                                          y_to_split)


os_us = SMOTETomek(sampling_strategy=1)

print('Applying SMOTETomek balancing to the training data.')
x_train, y_train = os_us.fit_sample(x_train_st, y_train_st)

# We put together the train dataframe again with the balanced data.
cols = final_df.columns.tolist()
del cols[trgt_index]
x_train_df, y_train_df = pd.DataFrame(
    x_train, columns=cols), pd.DataFrame(y_train, columns=['ES_PROMO'])
df_train = pd.concat([x_train_df, y_train_df], axis=1)
df_train

# We put together the test dataframe again since it was split in a previous step.
x_test_df, y_test_df = pd.DataFrame(
    x_test, columns=cols), pd.DataFrame(y_test, columns=['ES_PROMO'])
df_test = pd.concat([x_test_df, y_test_df], axis=1)

# Create the train and test datasets
h2o_train = h2o.H2OFrame(df_train)
h2o_test = h2o.H2OFrame(df_test)

m = h2o.estimators.H2ORandomForestEstimator(nfolds=10,
                                            max_depth=20,
                                            ntrees=50)

predictor_cols = ['Marca', 'Cupo', 'Region', 'Gerencia',
                  'SubCanal', 'TipoPoblacion', 'Estrato', 'EF']
target_col = 'ES_PROMO'
m.train(training_frame=h2o_train,
        x=predictor_cols,
        y=target_col)

print("\nTHIS IS THE MODEL PERFORMANCE")
print(m.model_performance(h2o_test))


cli_active_promo = active_promos.merge(
    clients_attributes, how='left', on='Cliente')
columns = final_df.columns.tolist()
index_target = columns.index('ES_PROMO')
del columns[index_target]

cli_active_promo = cli_active_promo[columns]
cli_active_promo.head(1)

# Now we try to predict what TARGET values will the CLIENTS and ACTIVE PROMOS have.
h2o_predict_df = h2o.H2OFrame(cli_active_promo)

p = m.predict(h2o_predict_df)

predicted_df = h2o.as_list(p)
predicted_df = predicted_df.rename(columns={'SI': 'Ejecuto_Promo'})

pred_merged_df = pd.concat([active_promos, predicted_df], axis=1)

# resultado_final
pred_no_dupes_df = pred_merged_df.drop_duplicates(
    subset=['Cliente', 'Marca', 'Cupo'])
pred_no_dupes_df
result = pred_no_dupes_df[['Cliente', 'Marca',
                           'Cupo', 'Ejecuto_Promo']].set_index('Cliente')


print("\nTHIS IS THE PREDICTED RESULT")
print(result)

output_filename = "{}/{}".format(tempfile.gettempdir(),
                                 "random_forest_balanced.csv")

print("SAVING OUTPUT IN {} ...".format(output_filename))

result.to_csv(output_filename)
