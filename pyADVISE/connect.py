# Load packages
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import Table, MetaData, select, and_, or_
import wbdata
from os.path import dirname, join



#############################################################
#############################################################
############   Get WB Data                          #########
#############################################################
#############################################################


def get_WB_data(indicators={}, countries=[]):
    # access data
    df = wbdata.get_dataframe(indicators, country=countries, convert_date=False)
    # reset index for navigation
    df = df.reset_index()
    return df


#############################################################
#############################################################
####            Connect to Local Server             #########
#############################################################
#############################################################


def ConnectSQL(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object'''

    # We connect with the help of the PostgreSQL URL
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    engine = sqlalchemy.create_engine(url, client_encoding='utf8')

    ## Connections
    connection = engine.connect()

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=engine, reflect=True)

    return engine, connection, meta

def SET_login():
    #### select key input variables - to be set un documetn usually
    user = 'postgres'
    password = 'PetiteTigresse'
    db = 'ODI-dataportal'

    # Connect to engine
    engine, connection, meta = ConnectSQL(user, password, db)

    return engine, connection, meta

def get_set_data(table='odi-portal-april2018'):

    tablename= table
    schemaname = 'public'

    # Access SET data
    engine, connection, meta = SET_login()

    # get data
    data = pd.read_sql_table(tablename, con=engine, schema =schemaname)

    return data

def push_new_data(df, table_name, if_exists='fail'):
    schemaname = 'public'

    # Access SET data
    engine, connection, meta = SET_login()

    # send dataset to postgres
    df.to_sql(table_name, con=engine, schema='public', if_exists=if_exists)

    return



######################################################3
#######################################################
#######                   Query  Data             #####
#######################################################
#######################################################


def simple_query(df, variables=[],countries=[],years=(1,1)):
    year = years
    if years == (1,1):
        year = (man(df['year'].as_matrix()), man(df['year'].as_matrix()))

    # years of choice



###########################################################
###########################################################
############   ACCESS FINISHED DATA 
###########################################################
###########################################################

def get_sourcefinal(table_num ='', path='./'):
    '''This function will return a final dataset within a source update file. The user
    specifies only the table number (without the _) if the data is in the same folder in 
    typical ASVISE format.'''
    
    
    # define paths to data
    data_path = path +'Final data/_'+ table_num+'data.sas7bdat'
    country_path = path+'Mappings/mapping_countries.sas7bdat'
    series_path =  path+'Mappings/mapping_series.sas7bdat'
    
    
    
    # read dataset
    data = pd.read_sas(data_path)
    countries = pd.read_sas(country_path)
    series = pd.read_sas(series_path)
    
    # change country_id, year, periodicity_id source_id, and start_value to int. 
    for i in ['series_id', 'country_id', 'year', 'periodicity_id', 'source_id', 'value_start']: 
        data[i] = data[i].astype('int')
    
    # set list of variables which need to change from bytes to string
    country_change = ['scode', 'country']
    series_change = ['series', 'series_name']


    # change series vars from bytes to string
    for i in series_change: 
        series[i] = series[i].str.decode('UTF-8')


    # change countries from bytes    
    for i in country_change: 
        countries[i] = countries[i].str.decode('UTF-8')


    # change country_id to int 
    countries['country_id'] = countries['country_id'].astype('int')
    
    
    # merge in country and series on respect datasets 
    print('The length of the original dataset is '+str(len(data)))
    
    
    data1 = pd.merge(data, countries, on='country_id', how='inner')
    print('After merging countries: ' +str(len(data)))
    
    
    data2 = pd.merge(data1, series, on='series_id', how='inner')
    print('After merging series: ' +str(len(data)))
    
        
    return data2
