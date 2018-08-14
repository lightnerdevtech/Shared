import pandas as pd


def merge_country_name(data, file='C:/Users/alightner/Documents/Source Updates/Gen data/'): 

    # read excel file, select vars of interest [[  ]]
    df_countries = pd.read_sas(file+'countries.sas7bdat')
    
    df = pd.merge(data, df_countries[['country_id', 'country_name', 'iso_alpha3']], on='country_id', how='left')
    
    for i in ['country_name', 'iso_alpha3']: 
        df[i] = df[i].str.decode('UTF-8')
    
    return df 

def merge_country_class(data, class_type='World Bank Income'):
    '''Provide data, the variable you would like to merge on, and the type of income 
    category the user would like to examine. Need to expand to other types of income groups.'''
    
    
    # set to shared file location in the future file = 
    file1 = 'C:/Users/alightner/Documents/Source Updates/Gen Data'
    
    
    # bring in relevant data sources
    codes = pd.read_sas(file1 + '/country_classification_values.sas7bdat')
    values = pd.read_sas(file1 + '/classification_values.sas7bdat')
    
    
    # change classification value name in values to UTU-08 
    values['classification_value_name'] = values['classification_value_name'].str.decode('UTF-8')
    
    
    # if class == 'World Bank Income' then just merge these codes 
    if class_type =='World Bank Income': 
        # keep only the WB codes (first 4 observations)
        values = values.iloc[0:4, :]
        # keep only the country code values where classif.. is bewteen 0 and 4. 
        codes = codes[codes['classification_value_id'].between(0,4)]
    
    
    # merge codes to dataset provided. 
    classif = pd.merge(codes, values, on='classification_value_id', how='left')
    # rename class_year to year to limit repetitiveness 
    classif.rename(index=str, columns={"classification_year": "year"}, inplace=True)
    
    # select only the max year
    max_year = max(list(classif['year'].unique()))
    
    # select the most recent year 
    classif = classif[classif['year']==max_year]
    
    # drop year
    classif.drop('year', axis=1, inplace=True)
    
    # merge datasets 
    df = pd.merge(data, classif, on=['country_id'], how='left')
    
    
    
    return df


def merge_series_names(data, include_vars=['series_name'], file='C:/Users/alightner/Documents/Source Updates/029 ILO/'): 

    # read excel file, select vars of interest [[  ]]
    df_series = pd.read_excel(file+'Mappings/mapping series.xlsx')
    
    df = pd.merge(data, df_series[['series_id']+include_vars], on='series_id', how='left')
    
    return df