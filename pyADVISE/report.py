###########################################
###########################################
####     Function to generate reports in Reportlab
###########################################
###########################################

# libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

## report lab
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# text options 
from textwrap import wrap


palette = {'USAID Blue': '#002F6C', 'USAID Red': '#BA0C2F', 'Rich Black': '#212721', 'Medium Blue': '#0067B9',
    'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Medium Gray': '#8C8985', 
           'Light Gray': '#CFCDC9', 'White': 'white'}




# split the notes at the bottom
def split(obs, n): 
    obs = "\n".join(wrap(obs, n)).split('\n')
    return obs


########################################
###### simple table 
#######################################


def table(c, df, line_width, column_w, split_num, height, margin, width, gap, text_font='something', table_ystart=9.19, enter=.28, 
              second_line=False, table_title='Table', fonts='default', ): 
    '''This function generates a table in the style of 
    the country reports. '''

    # general table settings
    c.setLineWidth(line_width)
        
    c.setFillColor(palette['Rich Black']) 
    c.setStrokeColor(palette['Rich Black'])

    # keys refer to the left hand side variable ids 
    keys = df.iloc[:,0].values
    keys = [split(keys[i], split_num) for i in range(0, len(keys))]


    # values are the 
    values = df.iloc[:,1].values
    values = [split(values[i], split_num) for i in range(0, len(values))]


    # because there is a header, I subtract one from the count
    table_gap = [len(values[i]) for i in range(0,len(values))]

    # adjust for the difference between gaps for line space and between lines of text. 
    for i in range(0, len(table_gap)): 
        a = table_gap[i]-1

        #make all gaps betweeen text only 65 percent of enter value
        if a>0: 
            gap = 1+(a*.45)
            table_gap[i] = gap

    #print(table_gap)

    ###############################################
    # starting point to be iterated on 
    ###############################################

    y = table_ystart


    # generate horizontal lines for table 
    for i in range(0, len(values)):
        c.line(inch(margin), inch(y), inch(margin+column_w), inch(y))
        #print(table_gap[i])
        y= y-(enter*table_gap[i])

    # final line outside of the loop
    c.line(inch(margin), inch(y), inch(margin+column_w), inch(y))


    # mark the end of the table => return w
    end_of_table = inch(y)

    ##############################################
    # generate text for the tables 
    ##############################################

    # set font 
    c.setFont('OpenSans-SemiBold', size=9, leading = None)
    # set indent for 
    indent=0.12

    # variable names 
    y_s = table_ystart -0.18

    # loop over each 
    for i in range(0, len(values)):

        # 
        lines = len(keys[i])

        if lines ==1: 

            c.drawString(inch(margin+indent),inch(y_s), keys[i][0])  

            y_s = y_s-(enter*table_gap[i])

        if lines>1:
            n = 0 
            for f in range(0, len(keys[i])):
                #print(dictionary[keys[i]][0])
                #c.drawString(inch(margin+indent),inch(y_s), dictionary[keys[i]][0][f])   
                c.drawString(inch(margin+indent),inch(y_s-(n*0.45*enter)), keys[i][f])  
                n +=1
            y_s = y_s-(enter*table_gap[i])

    ##############################
    # values for the table
    ##############################
    indent = [0, 1.1, 1.8, 2.5, 3.2]
    # add font_type_list = [normal, italics, etc.]




    for s in range(1, len(list(df))): 
        # iterate over a new set of values
        values = df.iloc[:,s].values
        values = [split(values[i], split_num) for i in range(0, len(values))]

        if s % 2 == 0:
            #even
            c.setFont('OpenSans-SemiBoldItalic', size=9, leading = None)
            c.setFillColor(palette['Medium Gray']) 
            c.setStrokeColor(palette['Medium Gray']) 
        else:
            # Odd
            #c.setFont('OpenSans-SemiBoldItalic', size=9, leading = None)
            c.setFont('OpenSans-SemiBold', size=9, leading = None)
            c.setFillColor(palette['Rich Black']) 
            c.setStrokeColor(palette['Rich Black']) 

        y_s = table_ystart-0.18
        for i in range(0, len(values)):

            # 
            lines = len(values)
            #print(lines)
            if lines==1: 
                n = 0 
                for g in values[i]:
                    #print(g)
                    c.drawString(inch(margin+indent[s]),inch(y_s-(n*0.65*enter)), g[0])  
                    n +=1
                y_s = y_s-(enter*table_gap[i])

            if lines>1:
                n = 0 
                for f in range(0, len(values[i])):
                    #print(dictionary[keys[i]][1][0])
                    #c.drawString(inch(margin+indent),inch(y_s), dictionary[keys[i]][0][f])   
                    c.drawString(inch(margin+indent[s]),inch(y_s-(n*0.45*enter)), values[i][f])  
                    n +=1
                y_s = y_s-(enter*table_gap[i])


    ########### draw column lines 
    column1 = 1.0
    c.setFillColor(palette['Rich Black']) 
    c.setStrokeColor(palette['Rich Black'])      
    c.line(inch(margin+column1), inch(table_ystart),inch(margin+column1), end_of_table)
    if second_line ==True: 
        c.line(inch(margin+column1+1.35), inch(table_ystart),inch(margin+column1+1.35), inch(table_ystart-(enter*4)))


    ########### draw title 
    c.setFont('OpenSans-Bold', size=14, leading = None)
    c.setFillColor(palette['Rich Black']) 
    c.setStrokeColor(palette['Rich Black']) 
    c.drawString(inch(1), inch(table_ystart+.15), table_title)


    # return end of the table for reference for next table or plot
    return c, end_of_table 


def inch(a): 
    a = a*72
    return a 
#####################################
######   USAID Header 
#####################################

def USAID_header(c, height, margin, column_w, gap, width, country='Malawi', date='July 2018',): 
    
    palette = {'USAID Blue': '#002F6C', 'USAID Red': '#BA0C2F', 'Rich Black': '#212721', 'Medium Blue': '#0067B9',
    'Light Blue': '#A7C6ED', 'Dark Red': '#651D32', 'Dark Gray': '#6C6463', 'Medium Gray': '#8C8985', 
           'Light Gray': '#CFCDC9', 'White': 'white'}


    # set current color, every fill color will be this color after this point until changed
    c.setFillColor(palette['Medium Blue']) 
    c.setStrokeColor(palette['Medium Blue'])
    
    # set the top of the box circle 
    top_box = height-0.7
    
    # blue top
    c.rect(0, inch(top_box), inch(9), inch(top_box), fill=1)
    
    #blue line
    c.setLineWidth(2)
    c.line(0, inch(top_box-.55), inch(9), inch(top_box-.55))
    c.setLineWidth(1)
    
    
    # grey box 
    c.setFillColor(palette['Light Gray']) 
    c.setStrokeColor(palette['Light Gray'])    
    c.rect(inch(margin), inch(9.7), inch(margin+column_w-0.5), inch(.6), fill=1)
    
    # title and country
    c.setFont('OpenSans-Light', size=30, leading = None)
    c.setFillColor(palette['White']) 
    c.setStrokeColor(palette['White']) 
    c.drawString(inch(margin+0.12), inch(top_box+.15), 'COUNTRY PROFILE')
    
    c.setFillColor(palette['White']) 
    c.setStrokeColor(palette['White']) 
    c.setFont('OpenSans-Light', size=12, leading = None)
    #c.drawString(inch(margin+0.12), inch(top_box+.15), 'COUNTRY PROFILE')
    c.drawRightString(inch(width-margin), inch(top_box+.15), 'USAID Data Services (EADS)')
    
    
    c.setFillColor(palette['Medium Blue']) 
    c.setStrokeColor(palette['Medium Blue'])
    c.setFont('OpenSans-Bold', size=24, leading = None)
    c.drawString(inch(margin+0.12), inch(top_box-.4), country.upper())
    
    
    c.setFillColor(palette['Medium Blue']) 
    c.setStrokeColor(palette['Medium Blue'])
    c.setFont('OpenSans-Bold', size=15, leading = None)
    c.drawRightString(inch(width-margin), inch(top_box-.4), date.upper())   

    return c


def USAID_footer_text(c, location=(150, 60), font='OpenSans-Light', size=8):
    
    palette = palettes.USAID_general()
    # begin the text object 
    textobject = c.beginText()
    # place the text object
    textobject.setTextOrigin(150, 60)
    # set font for the text options 
    textobject.setFont(font, size=size, leading = None)
    
    
    textobject.textLines('''
    Prepared by M/CIO’s Economic Analysis and Data Services (EADS) with data from the International Data and Economic 
    Analysis website (https://idea.usaid.gov/). DISCLAIMER: The views expressed in this publication do not necessarily refl-
    ect the views of the United States Agency for International Development (USAID) or the United States Government.
    ''')
    c.drawText(textobject)
    
    return c