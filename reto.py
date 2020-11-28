#!/usr/local/env python
import pandas as pd
import os
import configparser

pd.set_option("display.max_rows", 100)

config = configparser.ConfigParser()
config.read_file(open('config.ini'))

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
    sales_exec_promos['CodigoDC'].isnull() == False, 'ES_PROMO'] = 1


# This is the final dataframe we will analyze as part of the challenge
df = sales_exec_promos.merge(clients_attributes, how='left', on='Cliente')

del df['CodigoDC']
del df['FechaAltaCliente']

df = df.fillna({
    'ES_PROMO': 0,
    'SegmentoPrecio': df['SegmentoPrecio'].mode()[0],
    'Cupo': df['Cupo'].mode()[0]
})

df
