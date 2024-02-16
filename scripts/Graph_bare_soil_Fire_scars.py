#!/usr/bin/env python

"""
Read in the Spring and Autumn seasonal composite image with 4 bands and a polygon shapefile with areas burnt and unburnt and perform zonal statstic analysis and return a csv file with the results.
It then produces bar graphs showing the average bare soil value for burnt and unburnt regions for each pastoral property.  

Author: Grant Staben
Date: 01/06/2016

"""
import os
import numpy as np
import matplotlib.pyplot as plt
import fiona
import rasterio
import itertools
import pandas as pd 
import argparse
from rasterstats import zonal_stats
import pdb

def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("-a","--inAimage", help="Input Autumn seasonal composite image to derive zonal stats from")
    
    p.add_argument("-e","--inSimage", help="Input Spring seasonal image to derive zonal stats from")
                   
    p.add_argument("-s","--shape", help="shape file contiaing the zones needs to have a field defined as id")
    
    p.add_argument("-u","--uid", help="input the column name for the unique id field in the shapefile") 
    
    p.add_argument("-f","--fcsv", help="directory to store the csv file containing the combined results")
    
    
    cmdargs = p.parse_args()
    
    if cmdargs.inAimage is None:

        p.print_help()

        sys.exit()

    return cmdargs



def graphs(direc,outcsv,s,a):
    
    '''
    function to read in the output of the zonal stats and create a plot for each station. 
    '''
    
    
    df = pd.read_csv(direc + outcsv, header=0)
    df = df.fillna(0) # fill all the nan cells with zero
    
    property = pd.unique(df.Property.ravel())
    
          
    for i in property:
        
        print i
        prop  = df[(df.Property == i)]
    
        # get the fire scar year and make the season year string for the plot labels
    
        # select out the precentage area for each year and class from the df 
        s_b = prop.Spr_burnt.values    
        s_bv =  "%.1f" % s_b # get the value, format it to two decimal places to put at the top of the bar
    
        a_b = prop.Au_burnt.values
        a_bv = "%.1f" % a_b 
        
        s_ub = prop.Spr_unburnt.values
        s_ubv = "%.1f" % s_ub
    
        a_ub = prop.Au_unburnt.values
        a_ubv = "%.1f" % a_ub
        
        
    
        # gets all the % values and finds the maximum value and adds 4, this is used in the padding settings
        values = [s_b,s_ub,a_b, a_ub]
        maxValue = (np.max(values) + 4)
        
        # create the two variable pairs
        burnt = s_b, a_b
        unburnt = s_ub, a_ub 
    
               
        # set up the plot format
        n_groups = 2 
        fig, ax = plt.subplots()

        index = np.arange(n_groups)
        bar_width =0.28

        
        opacity = 0.8

    
        rects1 = plt.bar(index + 0.38, burnt, bar_width,alpha=opacity,color='grey',align='center',label='burnt after April '+ s) 
        rects2 = plt.bar(index + -0.15 ,unburnt,bar_width, alpha=opacity,color='white',label='not burnt '+ s) #
    

        plt.xlabel('Image Date')
        plt.ylabel('Average Bare Soil(%)')  
        #plt.title('add something meaningfull in here if requried') 
        plt.xticks(index + 0.18, ('Sep-Nov ' + s, 'Mar-May '+ a)) # need to extract the year from the csv file 
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
        padding = [-0.4, 1.8, 0, maxValue] # [xmin. xmax, ymin, ymax]
        plt.axis(padding)
    
        # Now make some labels
        labels1 = [s_bv, a_bv,]
        labels2 = [s_ubv, a_ubv]
    
        # add the average bare soil values at the top of each bar
        
        for rect, label in zip(rects1, labels1):
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2, height + 1, label, ha='center', va='bottom')
    
        for rect, label in zip(rects2, labels2):
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2, height + 1, label, ha='center', va='bottom')   
    
        plt.tight_layout()
        
    
        # this is how to save out your figure with a station name taken from the for loop
        fig.savefig(direc + "BareSoil_BurntUnburnt_{i}.png".format(i=i),bbox_inches='tight',dpi=600)
        
        


def mainRoutine():
    
    cmdargs = getCmdargs()
    # read in the command arguments
    rast_Aimage = cmdargs.inAimage # name and directory path to the raster imagery
    rast_Simage = cmdargs.inSimage # name and directory path to the raster imagery
    shp = cmdargs.shape # name and directroy path to the shape file contiaing the zones
    uid = cmdargs.uid
    
    
    # create an empty lists to write the results 

    zonestats_A = []
    siteID_A = []
    image_NameA = []
    
        
    
    with rasterio.open(rast_Aimage, nodata = 0) as srci:
        affine = srci.affine
        array = srci.read(1) # reads in band one the autumn bare fraction
    
        
    
        with fiona.open(shp) as src:
            zs = zonal_stats(src, array, nodata= 0, affine=affine,stats=['count', 'min', 'max', 'mean','median', 'std'],all_touched=True) # using "all_touched=True" will increase the number of pixels used to produce the stat
            
                    # extract the image name from the opened file from the input file read in by rasterio
            imgName1 = str(srci)[:-11]
            imgName = imgName1[-33:] # might need to modify this once a command args is implemented. 
            imgYear = imgName[11:15]      
            imgSeason = imgName[11:23] 

            for zone in zs:
                zone_stats = zone
                count = zone_stats["count"]
                mean = zone_stats["mean"]
                Min = zone_stats["min"]
                Max = zone_stats['max']
                med = zone_stats['median']
                std = zone_stats['std']
            
                # put the individual results in a list and append them to the zonestats list
                result = [mean,std, med, Min, Max, count]
                zonestats_A.append(result)
            
            # extract out the site number for the polygon
            
        
            for i in src:
            
                table_attributes = i['properties'] # reads in the attribute table for each record in the attribute table with are polygons in this example
                uid = table_attributes[cmdargs.uid] # reads in the id field from the attribute table and prints out the selected record 
                b_ub = table_attributes['FID_fs_sel'] # takes the burnt unburt identifer from the attribute table and prints it out the the selected records
                prop = table_attributes['PROP_NAME'] # takes the property name from the attribute table and saves it out the csv file.
                details = [uid,prop,b_ub,imgSeason,imgYear]
                siteID_A.append(details)
                imageUsed = [imgName]
                image_NameA.append(imageUsed)

    # join the elements in each of the lists row by rowlists row by row             
    finalresults =  [siteid + zoneR + imU for siteid, zoneR, imU in zip(siteID_A, zonestats_A,image_NameA)]  

    # convert the finalresults list to a pandas df, define the headers and read out the results to a csv file.
    df = pd.DataFrame.from_dict(finalresults , orient='columns', dtype=None)
    df.columns = ['uid','prop_name','Au_b_ub','season','year','mean','std', 'median', 'Min', 'Max', 'count','imName']
    
    df.to_csv('autumn.csv') # tempory csv file
	
     
    # close the vector and raster file 
    src.close() 
    srci.close() 


    zonestats_S = []
    siteID_S = []
    image_NameS = []


    with rasterio.open(rast_Simage, nodata = 0) as srci:
        
        affine = srci.affine
        
        array = srci.read(1) # reads in band one the autumn bare fraction
            
        with fiona.open(shp) as src:
            
            zs = zonal_stats(src, array, affine=affine, nodata= 0, stats=['count', 'min', 'max', 'mean','median', 'std'],all_touched=True) # using "all_touched=True" will increase the number of pixels used to produce the stat
                
            # extract the image name from the opened file from the input file read in by rasterio
            imgName1 = str(srci)[:-11]
            imgName = imgName1[-33:] # might need to modify this once a command args is implemented. 
            imgYearS = imgName[11:15]      
            imgSeason = imgName[11:23] 

            for zone in zs:
                zone_stats = zone
                count = zone_stats["count"]
                mean = zone_stats["mean"]
                Min = zone_stats["min"]
                Max = zone_stats['max']
                med = zone_stats['median']
                std = zone_stats['std']
            
                # put the individual results in a list and append them to the zonestats list
                result = [mean,std, med, Min, Max, count]
                zonestats_S.append(result)
                            
            # extract out the site number for the polygon
            for i in src:
                
                table_attributes = i['properties'] # reads in the attribute table for each record in the attribute table with are polygons in this example
                uid = table_attributes[cmdargs.uid] # reads in the id field from the attribute table and prints out the selected record 
                b_ub = table_attributes['FID_fs_sel'] # takes the burnt unburt identifer from the attribute table and prints it out the the selected records
                prop = table_attributes['PROP_NAME'] # takes the property name from the attribute table and saves it out the csv file.
                details = [uid,prop,b_ub,imgSeason,imgYearS]
                siteID_S.append(details)
                imageUsed = [imgName]
                image_NameS.append(imageUsed)

    # join the elements in each of the lists row by rowlists row by row             
    finalresults =  [siteid + zoneR + imU for siteid, zoneR, imU in zip(siteID_S, zonestats_S,image_NameS)]  

    # convert the finalresults list to a pandas df, define the headers and read out the results to a csv file.
    dfs = pd.DataFrame.from_dict(finalresults , orient='columns', dtype=None)
    dfs.columns = ['uid','prop_name','Spr_b_ub','season','year','mean','std', 'median', 'Min', 'Max', 'count','imName']
    
    dfs.to_csv('spring.csv') # tempory csv file

     
    # close the vector and raster file 
    src.close() 
    srci.close() 
    
    # read in the zonal stats with the results 

    df2 = pd.read_csv('autumn.csv', header=0)
    df = pd.read_csv('spring.csv', header=0)
    
    # produce pivot tables from the zonal statistics
    
    pivot = pd.pivot_table(df, values='mean',index =['prop_name'],columns=['Spr_b_ub'])
    pivot2 = pd.pivot_table(df2, values='mean',index =['prop_name'],columns=['Au_b_ub'])
    
    
    df2 = pd.DataFrame(pivot)
    df2.columns = [['Au_unburnt','Au_burnt']]
    
    df = pd.DataFrame(pivot2)
    df.columns = [['Spr_unburnt','Spr_burnt']]
    
    # get the columns out of the pivot tables and take 100 of the mean bare fractional cover vales
    station = df2.index.values
    autB = df2.Au_burnt.values - 100
    autUB = df2.Au_unburnt.values - 100
    sprB = df.Spr_burnt.values - 100
    sprUB = df.Spr_unburnt.values - 100
    
    # put the results back into a pandas df and replace the nan values with zero  
    
    data = np.vstack((station, autB, autUB, sprB, sprUB)).T # numpy array with all the columns station2 column is a check 
    
    df = pd.DataFrame(data)
    df.columns = [['Property','Spr_burnt','Spr_unburnt','Au_burnt','Au_unburnt']]
    df.fillna(0)
    
    s = str(imgYearS)
    a = str(imgYear)
    
    outcsv = 'Summary_'+ s + '_' + a + '_Burnt_unburnt.csv'
    
    direc = cmdargs.fcsv
    
    df.to_csv(direc + outcsv)
    
    graphs(direc,outcsv,s,a)
    
    os.remove('autumn.csv') # delete the temp autumn csv file
    os.remove('spring.csv') # delete the temp spring csv file

if __name__ == "__main__":
    mainRoutine()