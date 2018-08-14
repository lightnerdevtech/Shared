
############################
#### Generate jupyter themes 
############################



def jupyter_theme(name='USAID'): 
    '''this function selects the theme of interest for the user. It refers to one folder a particular folder within the 
    pyADVISE package (jupyter_themes).'''
    
    # load pakag
    from IPython.display import display, HTML
    with open('./pyADVISE/jupyter_themes/' +name +'.css') as f:
        css = f.read().replace(';', ' !important;')
    display(HTML('<style type="text/css">%s</style>Customized changes loaded.'%css))
    
    
    