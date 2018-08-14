########################################################
####  This generages the pyADVISE visualize package
########################################################

# import packages
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
from scipy.interpolate import spline

import statsmodels.api as sm
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, Div, HoverTool, LabelSet, Label, Legend, LegendItem
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook
from bokeh.models import Range1d
from bokeh.io import show
from bokeh.models import LogColorMapper
from bokeh.palettes import Viridis6 as palette
from bokeh.tile_providers import CARTODBPOSITRON

import ast
from pyproj import Proj, transform
import pyproj

###### NEW 

from bokeh.palettes import cividis, Blues
from bokeh.models import ColumnDataSource, Div, HoverTool, LabelSet, Label, Legend, LegendItem, ColorBar, LinearColorMapper
from bokeh.models import BasicTicker, PrintfTickFormatter

# new packages for the pyADIVSE package 
from bokeh.transform import factor_cmap







##################################################################
##################################################################
#############        GENERAL FUNCTIONS
##################################################################
##################################################################



def create_Div(div, text_type ='text'): 
    from bokeh.models import Div
    
    # options for text: title, subtitle, text 
    if text_type == 'text': 
        a  = '<p>\n' + div + '\n</p>\n'
        
    if text_type == 'title': 
        a = '<h1>\n' + div + '\n</h1>\n'
    if text_type == 'subtitle': 
        a = '<h3>\n' + div + '\n</h3>\n' 
    
    doc = Div(text='<style>\nh1 { font-family: "Gill Sans", "Gill Sans MT", Calibri, sans-serif; font-size: 24px; font-style: normal; font-variant: normal; font-weight: 500; line-height: 26.4px; }\n h3 { font-family: "Gill Sans", "Gill Sans MT", Calibri, sans-serif; font-size: 14px; font-style: normal; font-variant: normal; font-weight: 500; line-height: 15.4px; }\n p {\n    font: Gill Sans", "Gill Sans MT", Calibri, sans-serif;\n    text-align: justify;\n    text-justify: inter-word;\n    max-width: 500;\n}\n\n\n\n</style>\n\n'+ a, width=500)
    
    
    return doc





# define the select data function for the ESDB database style
def select_data(data, countries=('countryname', ['Malawi', 'China']), years=('year', (1995,2015)), variables=['3'], variable_var='series'):
    '''Selects data in the format of the ESDB'''

                # countries
    data = data[data[countries[0]].isin(countries[1])
                # years
                & data[years[0]].between(years[1][0], years[1][1])
                # variables
                & data[variable_var].isin(variables)
               ]

    return data



def USAID_style(p): 

    
    #######################
    ###  title 
    #######################
    p.title.text_color = '#383951'
    p.title.text_font = "Work Sans"
    p.title.text_font_style = "bold"    
    p.title.text_font_size= '15pt' 
    
    #######################
    ### Grid options 
    #######################
    
    # grid lines 
    p.grid.grid_line_color='white'
    p.grid.grid_line_width=1.5
    p.grid.grid_line_alpha=0.2
    
    
    
    #######################
    #### Axis styles 
    #######################
    
    ### labels
    p.xaxis.axis_label = ''
    p.yaxis.axis_label = ''

    
    p.axis.axis_label_text_color = '#999999'
    p.axis.axis_label_text_font_style = 'normal'
    p.axis.axis_label_text_font = "Work Sans"
    p.axis.major_label_text_font_size = '8pt'
    p.axis.major_label_text_font = "Work Sans"
    p.axis.axis_label_text_font_size = '10pt'    
    
    ## axis colors 
    #p.axis.line_color = ''
    #p.yaxis.axis_label = ''
    
    # axis  line options 
    p.axis.axis_line_color = '#999999'
    p.axis.axis_line_alpha = .8
    p.axis.axis_line_width = 2

    
    
    ### axis visable
    #p.yaxis.visible = False  
    #p.xaxis.visible = False
    #p.axis.axis_line_color=None
    
    
    ### major ticks
    p.axis.major_label_text_color='#999999'
    p.axis.major_tick_line_color='#999999'
    
    ### minor ticks 
    p.xaxis.minor_tick_line_color = None # turn off x-axis minor ticks
    p.yaxis.minor_tick_line_color = None
    
    
    ######################
    #### Legend styles
    ######################
    
    p.legend.label_text_font =  "Work Sans"
    p.legend.label_text_font_size = '11pt'
    p.legend.background_fill_alpha = 0.3

    

    ####################
    # plot outline
    ####################
    
    p.outline_line_color = None
    
    
    return p





##################################################################
##################################################################
#############        MAP SHADING
##################################################################
##################################################################

def gen_map_shading(data,merge_on, cat_var, cat_names, alpha_list,shading_color='Light Blue', shade=True, colors='default', 
                    color=True, OSM=False, country_var = 'country',  variable_var='value_start',  title_name ='Map', hover=False, outline_color='Dark Gray', 
                   legend_option=False, color_mapper=True, number_colors='default'):

    ### List cat_names in order of importance
    

    # allows the plots to show up in the jupyter notebook.
    output_notebook()

    ###############################################
    #####         Set Up Map Data
    ################################################



    # read the file which was cleaned and exported in the 'Gen_Map.ipynb'
    final3 = pd.read_csv(os.path.join('pyADVISE', 'data', 'country_outlines.csv'))[['NAME', 'ISO3', 'y_coord', 'x_coord']]

    # clean the data - lists were stored as strings. 
    for i, row in final3.iterrows():

        # lat/long coordinates
        x = ast.literal_eval(row['x_coord'])
        y = ast.literal_eval(row['y_coord'])


        # transform to OSM coordinates if useful.
        if OSM ==True:
            x, y = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), x, y)


        final3.set_value(i,'x_coord', x)
        final3.set_value(i, 'y_coord', y)
    
    final3['ISO3']= final3['ISO3'].astype('int')
    
    
    len1 = len(final3)
    ############################################
    ####   Merge Category Data
    ############################################
    if shade==True or color==True:
        final3 = pd.merge(final3, data, left_on='ISO3', right_on=merge_on, how='left')
    
    
    
    len2 = len(final3)
    len_diff = len1-len2
    
    if len_diff != 0: 
        print(len_diff)
    ##############################################
    ####          USAID Colors
    ##############################################

    palette = {'USAID Blue': '#002F6C', 'USAID Red': '#BA0C2F', 'Rich Black': '#212721', 'Medium Blue': '#0067B9',
    'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Medium Gray': '#8C8985', 'Light Gray': '#CFCDC9'}



    # generate column - 1 to be replaced
    final3['color'] = '1'

    # generate default number of colors 
    if number_colors == 'default': 
        number_colors = len(list(data[cat_var].unique()))

    
    ###################################3
    ####### 
    #####################################
    
    
    if shade ==True: 
        # Loop over dataset to replace
        for index, row in final3.iterrows():

            # generate values based on type column
            if OSM ==True:
                color = 'white'
            else:
                color = palette['Light Gray']



            if color==True:
            # generate colors for other types.
                for i in range(1, len(cat_names)):
                    if row[cat_var]==cat_names[i]:
                        color =palette[shading_color]


            # update column value
            final3.set_value(index,'color', color)
    
    
    # generate a var for the number of categories to be used throughout the code. 
    num_cats =  len(list(data[cat_var].unique()))
    
    if shade==False:
        
        final3['color'] = none_color
        
        
        if colors == 'default': 
            colors = list(reversed(Blues[number_colors]))

        
        try: 
            mapper = LinearColorMapper(palette=colors, low=min(list(data[cat_var].unique())), high=max(list(data[cat_var].unique())))
            string_var = False
        except: 
            print('Color variable is string type. Make sure to specify the color list in colors parameter.')
            string_var = True
            
            for index, row in final3.iterrows():
                if color==True:
                # generate colors for other types.
                    for i in range(0, len(cat_names)):
                        if row[cat_var]==cat_names[i]:
                            color =colors[i]

                # update column value
                final3.set_value(index,'color', color)
                
            
    # generate column - 1 to be replaced
    final3['alpha'] = '1'
    # Loop over dataset to replace
    for index, row in final3.iterrows():

        # generate values based on type column
        a = .8
        
        alpha_list =[]
        num = 0.2
        for i in range(0, num_cats):
            num = num + (0.75/num_cats)
            alpha_list.append(num)
        if shade==True:
            for i in range(1, len(cat_names)):
                if row[cat_var]==cat_names[i]:
                    a= alpha_list[i]


        # update column value
        final3.set_value(index,'alpha', a)



    ###############################################
    ######      Generate Plot
    ###############################################

    # place data in format that bokehdef  easily reads
    if shade == True and color==True:
        source = ColumnDataSource(final3[['NAME', 'y_coord', 'x_coord', 'color', cat_var, 'alpha', country_var]])
    elif  color==True:
        source = ColumnDataSource(final3[['NAME', 'y_coord', 'x_coord', 'color', cat_var, 'alpha', country_var]])
    else:
        source = ColumnDataSource(final3[['NAME', 'y_coord', 'x_coord', 'color', 'alpha', country_var]])




    if OSM ==True:
        p = figure(
            title="Practice Map", plot_width=990, plot_height=500,
                x_range=(-13000000, 20500000), y_range=(-6000000, 7000000),
            x_axis_location=None, y_axis_location=None,
                x_axis_type="mercator", y_axis_type="mercator")
    else:
        p = figure(
        title="Practice Map", plot_width=990, plot_height=500,
        x_axis_location=None, y_axis_location=None,
            y_range=(-55,78), x_range=(-125,180))



    #### Plot data
    p.grid.grid_line_color = None


    if legend_option==True: 
        map = p.patches('x_coord', 'y_coord', source=source,
              fill_color='color',
              fill_alpha='alpha', line_color=palette[outline_color], line_width=0.55, legend=cat_var)

    else: 
        map = p.patches('x_coord', 'y_coord', source=source,
              fill_color={'field': cat_var, 'transform': mapper},
              fill_alpha='alpha', line_color=palette[outline_color], line_width=0.55)

    p.legend.location = "bottom_right"
    p.legend.orientation = "horizontal"

    if OSM == True:
        p.add_tile(CARTODBPOSITRON)

    # Generate color code
    if shade==False: 
        color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="15pt",
                         ticker=BasicTicker(desired_num_ticks=number_colors),
                         label_standoff=6, border_line_color=None, location=(0, 0))

    var = '@'+ cat_var
    cvar = '@'+country_var


    if hover ==True:
            hover_circle = HoverTool(
                renderers=[map],
                tooltips=[
                    ('Country', cvar),
                    ( 'Type',   var)
                ]
            )
            p.add_tools(hover_circle)

    #####################################################
    ############### Settings
    ##############s#######################################


    p.title.text = title_name
    p.title.text_font_size='30pt'
    p.title.text_font = 'Gill Sans MT'
    p.legend.label_text_font = 'Gill Sans MT'
    p.legend.label_text_font_size = '11pt'
    p.legend.background_fill_color = palette['Light Gray']
    p.legend.background_fill_alpha = .5

    p.grid.grid_line_color = None
    
    ### add color bar
    p.add_layout(color_bar, 'left')

    return p



########################################################################
#############   ADD CITIES
########################################################################


def gen_map_cities(data, lat_var, long_var, city_var, country_var, output_file_name = 'City Map', title_name = 'Map',
                   OSM=False, p ='None', dot_style='normal', type_var="None", label_washington = False, legend=True, hover = True):
    '''This function takes a dataset with city and country names and their repsective coordinates and returns
    a plot with the map or adds these plots to an already created map if p=None'''

    # define palette as a dictionary
    
    palette = {'USAID Blue': '#002F6C', 'USAID Red': '#BA0C2F', 'Rich Black': '#212721', 'Medium Blue': '#0067B9',
    'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Medium Gray': '#8C8985', 'Light Gray': '#CFCDC9', 'White': 'white', 
              'Light Red': '#dd88a1', }


    # transform to OSM coordinates if useful.
    for i, row in data.iterrows():

        # lat/long coordinates
        x = row[long_var]
        y = row[lat_var]
        # trasform to OSM coordinates
        if OSM ==True:
            x, y = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), x, y)

        data.set_value(i,long_var, x)
        data.set_value(i,lat_var , y)

    # if there is not a plot before, generate a plot.
    if p=='None':
        df_blank = pd.DataFrame()
        p = gen_map_shading(data=df_blank, merge_on='ISO3', cat_var ='type', cat_names=(''),
                           map_color = 'Light Gray', alpha_list = (1), title_name = '', OSM=False,
                            shade=False)



    #######################################
    ##### If just circles
    #######################################

    if dot_style=='normal':

        ### Add color choices (future addition)

        # plots which plain circles as city dots and
        # source the data
        source = ColumnDataSource(data)

        # add circle plot
        c = p.circle('long', 'lat', source=source, color='darkred', size = 10)

        # Define tooltip variables
        Tip1 = '@'+city_var
        Tip2 = '@'+country_var

        if type != 'None':
            Tip3 = '@'+type_var

        # define tooltips
        if type != 'None':
            TT=[
                ( 'City',   '@city'),
                ('Country', '@country')
            ]
        else:
            TT = [
                ( 'City',   '@city'),
                ('Country', '@country'),
                ( 'Office Type',   '@type')
            ]


        # add hover tool
        hover_circle = HoverTool(
            renderers=[c],
            tooltips=TT
        )

        p.add_tools(hover_circle)




    ##################################################
    # if dot types are specified
    #################################################
    else:



        # generate source IDs
        try:
            d = {}
            for i in data[type_var].unique():
                d[i] = ColumnDataSource(data[data[type_var]==i])
        except:
            print('Check if type_var is specified correctly.')


        # empty dictionary to place plot results in.
        plot_dictionary = {}

        # loop through the
        #plotn = 0
        for i in list(dot_style.keys()):
            if len(dot_style[i])==1:

                # depending on the choice of the circle, add visiual to the plot
                if dot_style[i][0][0] == 'circle':
                        if legend==True: 
                            plot_dictionary[i] = p.circle(x =long_var, y=lat_var, line_color = palette[dot_style[i][0][1]], fill_color=palette[dot_style[i][0][2]],  source = d[i],
                                                         size=dot_style[i][0][3], fill_alpha=dot_style[i][0][4], line_width=dot_style[i][0][5], legend=i)
                        elif dot_style[i][0][0] == 'square':
                            plot_dictionary[i] = p.square(x =long_var, y=lat_var, line_color = palette[dot_style[i][0][1]], fill_color=palette[dot_style[i][0][2]],  source = d[i],
                                                         size=dot_style[i][0][3], fill_alpha=dot_style[i][0][4], line_width=dot_style[i][0][5], legend=i)
                        elif dot_style[i][0][0] == 'asterisk':
                            plot_dictionary[i] = p.asterisk(x =long_var, y=lat_var, line_color = palette[dot_style[i][0][1]], fill_color=palette[dot_style[i][0][2]],  source = d[i],
                                                         size=dot_style[i][0][3], fill_alpha=dot_style[i][0][4], line_width=dot_style[i][0][5], legend=i)
                            
                            
                            
                        #### NO legend
                        if legend==False: 
                            plot_dictionary[i] = p.circle(x =long_var, y=lat_var, line_color = palette[dot_style[i][0][1]], fill_color=palette[dot_style[i][0][2]],  source = d[i],
                                                         size=dot_style[i][0][3], fill_alpha=dot_style[i][0][4], line_width=dot_style[i][0][5])
                        elif dot_style[i][0][0] == 'square':
                            plot_dictionary[i] = p.square(x =long_var, y=lat_var, line_color = palette[dot_style[i][0][1]], fill_color=palette[dot_style[i][0][2]],  source = d[i],
                                                         size=dot_style[i][0][3], fill_alpha=dot_style[i][0][4], line_width=dot_style[i][0][5])
                        elif dot_style[i][0][0] == 'asterisk':
                            plot_dictionary[i] = p.asterisk(x =long_var, y=lat_var, line_color = palette[dot_style[i][0][1]], fill_color=palette[dot_style[i][0][2]],  source = d[i],
                                                         size=dot_style[i][0][3], fill_alpha=dot_style[i][0][4], line_width=dot_style[i][0][5])                            
            else:


                # for each overlapping figure, plot the respective specifications.
                for l in dot_style[i]:
                    if legend == True: 
                        if l[0] == 'circle':
                            plot_dictionary[i] = p.circle(x =long_var, y=lat_var, line_color = palette[l[1]], fill_color=palette[l[2]], source = d[i],
                                                     size=l[3], fill_alpha=l[4], line_width=l[5], legend=i)
                        elif l[0] == 'square':
                            plot_dictionary[i] = p.square(x =long_var, y=lat_var, line_color = palette[l[1]], fill_color=palette[l[2]], source = d[i],
                                                     size=l[3], fill_alpha=l[4], line_width=l[5], legend=i)
                        elif l[0] == 'asterisk':
                            plot_dictionary[i] = p.asterisk(x =long_var, y=lat_var, line_color =palette[l[1]], fill_color=palette[l[2]], source = d[i],
                                                     size=l[3], fill_alpha=l[4], line_width=l[5], legend=i)

                    # if no legend 
                            plot_dictionary[i] = p.circle(x =long_var, y=lat_var, line_color = palette[l[1]], fill_color=palette[l[2]], source = d[i],
                                                     size=l[3], fill_alpha=l[4], line_width=l[5])
                        elif l[0] == 'square':
                            plot_dictionary[i] = p.square(x =long_var, y=lat_var, line_color = palette[l[1]], fill_color=palette[l[2]], source = d[i],
                                                     size=l[3], fill_alpha=l[4], line_width=l[5])
                        elif l[0] == 'asterisk':
                            plot_dictionary[i] = p.asterisk(x =long_var, y=lat_var, line_color =palette[l[1]], fill_color=palette[l[2]], source = d[i],
                                                     size=l[3], fill_alpha=l[4], line_width=l[5])
                            
                            
                            
                            
            if label_washington ==True:
                # Label washignton dc
                labels = LabelSet(x='long', y='lat', text='city', level='glyph',
                              x_offset=8, y_offset=8, source=d['Headquarters'], render_mode='canvas',
                              text_alpha=0.95, text_color=palette['Dark Gray'], text_font='Gill Sans MT')
                p.add_layout(labels)


            if hover==True: 
                # Define tooltip variables
                Tip1 = '@'+city_var
                Tip2 = '@'+country_var
                Tip3 = '@'+type_var

                # define tooltips
                TT = [
                    ( 'City',   Tip1),
                    ('Country', Tip2),
                    ( 'Office Type', Tip3)
                ]

                # get list of renderers
                list_renderers = [plot_dictionary[i] for i in list(plot_dictionary.keys())]

                # add hover tool
                hover_circle = HoverTool(
                    renderers=list_renderers,
                    tooltips=TT)

                p.add_tools(hover_circle)

    #####################################################
    ############### Settings
    #####################################################

    p.title.text = title_name
    p.title.text_font_size='20pt'
    p.title.text_font = 'Gill Sans MT'
    if legend==True:
        p.legend.label_text_font = 'Gill Sans MT'
        p.legend.label_text_font_size = '11pt'
        p.legend.background_fill_color = palette['Light Gray']
        p.legend.background_fill_alpha = .5
        p.legend.orientation='horizontal'
        p.legend.location = 'bottom_right'
        p.legend.background_fill_alpha= 0
        p.legend.border_line_alpha= 0
        
    
    return p










##################################################################
##################################################################
#############        LINE GRAPH
##################################################################
##################################################################



def gen_line(data, country_list=['Malawi', 'China'], var_list=['3'], var_labels=['FDI Growth'], year_tuple=(1995,2000), y_axis='Y-Axis', x_axis='X-Axis',
             title_text= 'Figure 3: Comparison of multiple countries ³', country_var='country', year_var = 'year', variable_var= 'series', value_var='value_start',
                smooth_line = False, line_width = 5,  line_pattern=['solid', 'dashed', 'solid', 'dashed'], dots=True):

    '''This function takes multiple countries, with one indicator variable and compares them accordingly. Or one country and
    multiple indicators. At the moment, the function does not support multiple selections of both countries and indicators. '''


    # colors
    palette = {'USAID Blue': '#002F6C', 'USAID Red': '#BA0C2F', 'Rich Black': '#212721', 'Medium Blue': '#0067B9',
    'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Medium Gray': '#8C8985', 'Light Gray': '#CFCDC9'}

    palette_names = list(palette.keys())


    line_style = line_pattern*(len(country_list)*len(var_list))

    #############################################
    ####  More than one country
    #############################################


    if len(country_list)>=1 & len(var_list)==1:
        data = select_data(data, countries=(country_var, country_list), years=(year_var, year_tuple), variables=var_list, variable_var=variable_var)
        

        d = {}
        for i in country_list:
            small = data[data[country_var]==i]


            circles = {}
            lines = {}
            if smooth_line == False:
                for v in var_list:
                    lines[v] = [small[value_var].values, small[year_var].values]
                    circles[v] = [small[value_var].values, small[year_var].values]
            else:
                print('Smooth options is still under construction.')
                values = small[value_var].values
                years = small[year_var].values
                # take code from ODI code

                # df['year'] = np.linspace(country_df['year'].min(), country_df['year'].max(), 180)
                # df[Var_Interest] = spline(country_df['year'], country_df[Var_Interest], df['year'])

                new_years = np.linspace(min(years), max(years), 180)

                # this is not working for some reason , not obvious.... says problem with interpolating floats...???
                new_values = spline(years, values, new_years)

                lines[v] = [new_values, new_years]
                circles[v] = [small[value_var].values, small[year_var].values]


            # return results
            d[i] = [lines, circles]
        print(d)



        ##################################################
        #########  Generate Plot
        ##################################################

        p = figure(plot_height=500, plot_width=800)


        plot_dictionary = {}
        source_dict = {}
        name_list = []
        labels = []
        n=0
        for i in country_list:
            for f in range(0, len(var_list)):


                if len(var_labels)>1:
                    name = i+': ' +var_labels[f]+'   '

                else:
                    name = i+ '   '
                name_list.append(name)

                # generate the lines - noted by the [0] pointing to the lines dictionary
                # this distinction is needed for the
                s = p.line(x=d[i][0][var_list[f]][1], y=d[i][0][var_list[f]][0],
                           color=palette[palette_names[n]], line_width=line_width,
                           line_dash=line_style[n], line_dash_offset=4)


                if dots == True:
                    source_dict[i+str(f)] = ColumnDataSource({'x': d[i][1][var_list[f]][1], 'y': d[i][1][var_list[f]][0], 'country': [i]*len(d[i][1][var_list[f]][1])})

                    r = plot_dictionary[i+str(f)] = p.circle('x', 'y', source = source_dict[i+str(f)], name=name, color=palette[palette_names[n]], size=(line_width*2))


                # legend outside the plot
                labels.append(LegendItem(label=dict(value=name), renderers=[s]))

                n+=1

        legend = Legend(items=labels, location=(0, 0), orientation='horizontal')
        p.add_layout(legend, 'above')




        # Define tooltips

        Tip2 = '@'+'country'
        Tip1 = '@'+'x'
        Tip3 = '@'+'y'

        # define tooltips
        TT = [
            ('Country', Tip2),
             ('Year',   Tip1),
            ( 'Value', Tip3)
        ]

        # get list of renderers
        list_renderers = [plot_dictionary[i] for i in list(plot_dictionary.keys())]

        # add hover tool
        hover_circle = HoverTool(
            names = name_list,
            #renderers=list_renderers,
            tooltips=TT)

        p.add_tools(hover_circle)




    ##################################################
    ####### More than one variable
    #################################################

    elif (len(country_list)==1) & (len(var_list)>=1):



        data = select_data(data, countries=(country_var, country_list), years=(year_var, year_tuple), variables=var_list, variable_var=variable_var)

        d = {}
        for i in range(0, len(var_list)):
            small = data[data[variable_var]==int(var_list[i])]


            if smooth_line == False:
                lines = [small[value_var].values, small[year_var].values]
                circles = [small[value_var].values, small[year_var].values]
            else:
                print('Smooth options is still under construction.')
                values = small[value_var].values
                years = small[year_var].values
                # take code from ODI code

                # df['year'] = np.linspace(country_df['year'].min(), country_df['year'].max(), 180)
                # df[Var_Interest] = spline(country_df['year'], country_df[Var_Interest], df['year'])

                new_years = np.linspace(min(years), max(years), 180)

                # this is not working for some reason , not obvious.... says problem with interpolating floats...???
                new_values = spline(years, values, new_years)

                lines[v] = [new_values, new_years]
                circles[v] = [small[value_var].values, small[year_var].values]


            # return results
            d[var_labels[i]] = [lines, circles]

        print(d)
        ##################################################
        #########  Generate Plot
        ##################################################

        p = figure(plot_height=500, plot_width=800)


        plot_dictionary = {}
        source_dict = {}
        name_list = []
        labels = []
        n=0


        for i in var_labels:

            # add spacing between labels
            name = i+ '   '
            name_list.append(name)

            # generate the lines - noted by the [0] pointing to the lines dictionary
            # this distinction is needed for the
            s = p.line(x=d[i][0][1], y=d[i][0][0],
                       color=palette[palette_names[n]], line_width=line_width,
                       line_dash=line_style[n], line_dash_offset=4)


            if dots == True:

                source_dict[i] = ColumnDataSource({'x': d[i][1][1], 'y': d[i][1][0], 'variable': [i]*len(d[i][1][1])})

                r = plot_dictionary[i] = p.circle('x', 'y', source = source_dict[i], name=name, color=palette[palette_names[n]], size=(line_width*2))


            # legend outside the plot
            labels.append(LegendItem(label=dict(value=name), renderers=[s]))

            n+=1


        legend = Legend(items=labels[0:], location=(0, 0), orientation='horizontal')
        p.add_layout(legend, 'above')

        #legend = Legend(items=[labels[1]], location=(0, 0), orientation='horizontal')
        #p.add_layout(legend, 'above')



        # Define tooltips

        Tip2 = '@'+'variable'
        Tip1 = '@'+'x'
        Tip3 = '@'+'y'

        # define tooltips
        TT = [
            ('Variable', Tip2),
             ('Year',   Tip1),
            ( 'Value', Tip3)
        ]

        # get list of renderers
        list_renderers = [plot_dictionary[i] for i in list(plot_dictionary.keys())]

        # add hover tool
        hover_circle = HoverTool(
            names = name_list,
            #renderers=list_renderers,
            tooltips=TT)

        p.add_tools(hover_circle)


    else:
        print('This function does not support multiple country and indicator selections. Please revisit the country and indicator selections.')






    p = USAID_style(p)

    p.title.text = title_text
    p.legend.background_fill_color = 'white'

    return p
	
	
	

##################################################################
##################################################################
#############       Histogram 
##################################################################
##################################################################



def histogram_kden(data, x_var, title_text='Histogram plot', note='', category='None', 
                   variable_var='series_id', value_var='value_start', num_bins=25, bars=False, 
                   legend_labels='None'): 

    # generate the color palette for the plot (USAID colors )
    palette = {'USAID Blue': '#002F6C', 'USAID Red': '#BA0C2F', 'Medium Blue': '#0067B9',
               'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Rich Black': '#212721', 'Medium Gray': '#8C8985', 
               'Light Gray': '#CFCDC9'} 
    
    colors = list(palette.keys())
    



    # change the dictionary values depending on category choice. 
    if category!='None': 
        # drop those values for which category var is missing 
        data = data[data[category].notnull()]
        # generate a list of group options 
        groups = list(data[category].unique())
        # create a dictionary for each group listed 
        dictionary = {}
        for i in groups: 
            d1 = data[data[variable_var]==x_var]
            d1 = d1[d1[category]==i]
            d1 = d1[d1[value_var]>0]
            dictionary[i] = d1[value_var].dropna().values
      

    
    # if a group var is not specified     
    else: 
        # only interate over the one variable of interest 
        groups = [x_var]
        # place the values of this variable in a dictionary (consistent with the rest of the code)
        dictionary = {x_var: data[data[variable_var]==x_var][value_var].dropna().values}

    
    # create plot
    p2 = figure(title="",tools="save", plot_height=350, plot_width = 780)
    
    # if the users want bars along iwth the distro. 
    if bars ==True: 
        for i in range(0, len(groups)): 

            # generate the plotting points for the hist
            hist, edges = np.histogram(dictionary[groups[i]],density=True, bins=num_bins)

            # drop the extreme bars for attractiveness 
            p2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
            color= palette[colors[i]], fill_alpha =0.3, line_width = 1.2 )     


    # I chose to inlcude only the area kernel density plots, rather than bins
    kdes = {}
    for i in groups: 
        kde = sm.nonparametric.KDEUnivariate(dictionary[i])
        kde.fit()
        kdes[i]= kde
    
    # if the user does not specify labels 
    if legend_labels=='None': 
        for i in range(0, len(groups)): 
             p2.patch(kdes[groups[i]].support,kdes[groups[i]].density, color=palette[colors[i]], 
                      line_width=5, fill_alpha=0.3, line_alpha=.75, legend=str(groups[i]))
    
    # if the user specifies labels (must be in list)
    else: 
        for i in range(0, len(groups)): 
             p2.patch(kdes[groups[i]].support,kdes[groups[i]].density, color=palette[colors[i]], 
                      line_width=5, fill_alpha=0.3,line_alpha=0.75, legend=legend_labels[i])       
                
    # plot formatting
    p2 = USAID_style(p2)
    #p2.xaxis.visible = False
    #p2.legend.location = "center_right"
    #p2.legend.background_fill_color = "darkgrey"
    p2.yaxis.axis_label = ''
    p2.xaxis.axis_label = ''
    p2.title.text = title_text
    p2.legend.label_text_font_size = '8pt'
    #p2.axis.major_label_text_font_size = '8pt'    

    
    
    return(p2)


##################################################################
##################################################################
#############       Stacked Area Plot 
##################################################################
##################################################################





def gen_area_stack(data, obs, variables, years=(2000,2017), value_var='start_value', 
                  prop=False, colors='default', title_text = 'Area Chart', 
                  label_texts = ['default']):
    
    
    ########################
    ### Set color scheme 
    palette = {'USAID Blue': '#002F6C', 'Medium Blue': '#0067B9','Light Blue': '#A7C6ED', 
               'Light Gray': '#CFCDC9', 'USAID Red': '#BA0C2F','Dark Red': '#651D32', 
               'Medium Gray': '#8C8985', 'Rich Black': '#212721',  
               'Dark Gray': '#6C6463', }


    
    if colors == 'default': 
        colors = list(palette.keys())
        
    ###############################
    ####   select observations (countries) and variables 
    
    data = data[data['country_id']==obs]
    data = data[data['series_id'].isin(variables)]
    
    ################################
    ###   Change data into panel 
    ################################
    
    # select only the data we need
    data = data[['country_id', 'year', 'value_start', 'series_id']]
    # shift data into panel format 
    data = data.pivot_table(values='value_start', index=['country_id', 'year'], 
                                        columns='series_id', aggfunc=np.sum).reset_index()

    data.drop('country_id', axis=1, inplace=True)

    data.set_index('year', inplace=True)
    
    
    #################################
    ##### Proportion or normal stack
    #################################
    
    if prop==True: 
        num = data[variables].sum(axis=1).to_frame()

        # generate a sum variable 
        data['total'] = data[variables].sum(axis=1)
        # replace variable values with the proportions 
        for i in variables:
            data[i] = data[i]/data['total']*100
        #drop total when finished 
        data.drop('total', inplace=True, axis=1)

        
    # change all variable names to an iterable (y0, y1, etc)
    ys = ['yy'+str(i) for i in range(0, len(variables))]
    data.columns = ys
    
    ####################################
    ##### Generate Area Plot 
    
    
    # generate the numeric basics of the plot for input into patches 
    areas = stacked(data)
    
    # generate a max value for the y axis position
    max_value = np.nanmax(areas.values)
    max_value = np.round(max_value, 0) 
    max_value = int(max_value)
    

    ### generate y_range if prop ==True
    if prop ==True: 
        p = figure(x_range=years,y_range=(0, 100), plot_height=675, plot_width=780)
    else: 
        p = figure(x_range=years, y_range=(0, max_value),  plot_height=675, plot_width=780) 
    

    ### generate the stack coordinates 
    x2 = np.hstack((data.index[::-1], data.index))
    
    # plot the patches 
    p.patches([x2] * areas.shape[1], [areas[c].values for c in areas],
              color=[palette[i] for i in colors], fill_alpha=0.15, line_width=3) 
    
    
    # generate the hover line 
    source = ColumnDataSource(data)
    p.line(x='year', y='yy0',source=source, color=palette['USAID Blue'], line_width=.2)
    
    #######################################
    ### Generate the Legend and Hover
    #######################################
    
    if label_texts == ['default']: 
        names = [str(i) for i in variables]
    else: 
        names = label_texts
    labels = []
    
    # iterate over the areas and plot the visual 
    for i, area in enumerate(areas):
        # save the meta data from each p in [r]
        r = p.patch(x2, areas[area], color=palette[colors[i]], alpha=0.8, line_color=None)
        # generate a seperate label based on the r meta data. 
        
        labels.append(LegendItem(label=dict(value=names[i]), renderers=[r]))
        
    # plot the legend on the right of the plot 
    legend = Legend(items=labels, location=(0, 10), orientation='horizontal')
    p.add_layout(legend, 'above')
    
    
    ########### Hover 
    tooltips1 = []
    for i in range(0, len(variables)): 
            tip = (names[i], '@'+'yy'+str(i)+'{0.00 a}')
            tooltips1.append(tip) 

    
    hover = HoverTool(
    tooltips=tooltips1,
    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline')
    
    p.add_tools(hover)
    
    p = USAID_style(p)
    
    p.title.text = title_text
    p.legend.background_fill_alpha = 0
    p.legend.border_line_color=None
    p.xgrid.visible = True
    p.legend.glyph_height = 30
    p.legend.glyph_width= 30
    return p
    

    


##################################################################
##################################################################
#############       Stacked Stacked Bar 
##################################################################
##################################################################





    
def gen_stacked_bar(data, cat_var, stacked_var, value_var, colors = 'default', title_text='stacked bar', orientation='x-axis', 
                   alpha=0.8): 
    '''This function generates a stacked bar given data and three variables in long form. The 
    user can also choose whether the stack is vertical or horizontal in orientation. '''
    
    palette = {'USAID Blue': '#002F6C', 'Medium Blue': '#0067B9',  'Light Blue': '#A7C6ED', 'Medium Gray': '#8C8985', 'Light Gray': '#CFCDC9', 'USAID Red': '#BA0C2F', 'Rich Black': '#212721', 'Medium Blue': '#0067B9',
    'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Medium Gray': '#8C8985', 'Light Gray': '#CFCDC9'}
    
    # generate the lists for labels 
    bars=list(data[cat_var].unique())
    stacks = [str(i) for i in list(data[stacked_var].unique())]
    colors = list(palette.values())[0:len(stacks)]
    
    # generate the dictionary of data points 
    d = {'bars': bars}
    
    for i in stacks: 
        d[i] = list(data[data[stacked_var]==int(i)][value_var].values)
    

    output_notebook()
  
    
    # generate the plot 
    p = figure(x_range=bars, plot_height=500,plot_width=800,  title=title_text,
           toolbar_location=None, tools="hover", 
               tooltips='''<div>
                            <div>
                                <span style="font-size: 13px; font-family: 'Gill Sans MT'; color: black;">$name, @bars: @$name</span>
                            </div>
                        </div>''')
    
    if orientation=='x-axis' : 
        p.vbar_stack(stacks, x='bars', width=0.9, color=colors, source=d, 
                   legend=[value(x) for x in stacks])
    
    p = new_style(p)
    
    p.yaxis.visible = True  
    p.xaxis.visible = True
    p.legend.orientation='horizontal'
    p.legend.location='top_left'
    
    length = len(bars)
    
    if length>4: 
        p.xaxis.major_label_orientation = pi / 2.5
        
    
    return p






##################################################################
##################################################################
#############        Grouped Bar 
##################################################################
##################################################################



def gen_grouped_bar(data, cat_var_member, cat_var_group, value_var ='value_start',
                    cat_var_member_name='series_name', cat_var_group_name='country_id', 
                   title_text='Grouped Bar - Example', plot_dim=(300, 800), fill_alpha=0.5, 
                   line_width=3): 
    ''' this function generated a group bar chart where the the cat_var_member data are 
    nested under the group variables, colored by group variables. Can change which varaibles refer to 
    the group var and the member by changing the (*name) varialbes'''
    
    
    ########################
    #### prep data 
    ########################
    
    # select the data of interest
    data = data[data[cat_var_member_name].isin(cat_var_member) &
               data[cat_var_group_name].isin(cat_var_group)]
    
    
    # make sure cat_vars are strings types (object)
    data[cat_var_member_name] = data[cat_var_member_name].astype(str)
    data[cat_var_group_name] = data[cat_var_group_name].astype(str)

    # generate groupby 
    group = data.groupby((cat_var_group_name, cat_var_member_name))

    ###### generate palette 
    palette = {'USAID Blue': '#002F6C', 'USAID Red': '#BA0C2F', 'Rich Black': '#212721', 'Medium Blue': '#0067B9',
    'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Medium Gray': '#8C8985', 'Light Gray': '#CFCDC9'}
    palette = [palette[i] for i in list(palette.keys())[0:len(cat_var_member)]]
    
    
    # generate factor_cmap based on the group member (the name can be anything - just referable)
    name = cat_var_group_name + '_'+ cat_var_member_name
    index_cmap = factor_cmap(name, palette=palette, factors=sorted(data[cat_var_group_name].unique()), end=1)
    
    name_tip= '@'+name
    value_tip = '@'+value_var+'_mean{0.0}'
    ##########################
    ##### Generate plot 
    ##########################
    
    
    # generate figure 
    p = figure(plot_width=plot_dim[1], plot_height=plot_dim[0],
           x_range=group, toolbar_location=None, tooltips=[('Category: ', name_tip), 
                                                           ('Value: ', value_tip)])
    
    
    # generate bar graph
    p.vbar(x=name, top=value_var+'_mean', width=.8, source=group,
           color=index_cmap, line_width=line_width,fill_alpha =fill_alpha)
    

    
    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    #p.xaxis.axis_label = "Manufacturer grouped by # Cylinders"
    p.xaxis.major_label_orientation = 1.2
    p.outline_line_color = None
    
    p = USAID_style(p)
    
    ## title 
    p.title.text_font_size= '140pt'
    p.title.text_color= 'black'
    p.title.text = title_text
    
    
    return p
    
    