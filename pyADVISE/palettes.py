######################################
######################################
####   Set of Devtech Palettes 
######################################
######################################


def USAID_general(return_type='dict'): 
    
    dictionary = {'USAID Blue': '#002F6C', 'USAID Red': '#BA0C2F', 'Rich Black': '#212721', 'Medium Blue': '#0067B9',
    'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Medium Gray': '#8C8985', 
           'Light Gray': '#CFCDC9', 'White': 'white'}
    
    list_color = [dictionary[i] for i in list(dictionary.keys())]
    
    if return_type=='dict': 
        colors = dictionary
    else: 
        colors = list_color 
    
    return colors 

