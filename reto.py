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
client_attributes = pd.read_csv(
    client_attributes_file_path, encoding='latin-1')

print(sales)

active_promos.to_csv('test.csv', index=False)
