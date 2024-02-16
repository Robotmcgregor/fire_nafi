#!/usr/bin/env python

"""
DRAFT - Read in cadasre and select properties by name from an excel sheet.
Add a unique id field (uid) and re-project the file.


Author: Rob McGregor
Date: 01/10/2020


"""


from __future__ import print_function, division
#import pdb
import fiona
import argparse
#import sys
import os
import shutil
#import glob
import geopandas as gdp


def getCmdargs():

    p = argparse.ArgumentParser(description="""Input a single or multiband raster to extracts the values from the input shapefile. """)

    p.add_argument("-c","--cadastre", help="Cadastre location")
        
    p.add_argument("-e","--excel", help="Read in the excel file with all property names in the first column")
    
    p.add_argument("-f","--file_path", help="Output shapefile directory")
    

    cmdargs = p.parse_args()
    
    if cmdargs.imlist is None:

        p.print_help()

        sys.exit()

    return cmdargs

def properties(cadastre, file_path):
    
    shapefile_list =[]

    # create individual property shapefiles from a list
    for i in prop_list:
        #To select rows whose column value equals a scalar, some_value, use ==:
        prop = cadastre[cadastre["PROP_NAME"]== i]
        prop.reset_index(drop=True, inplace=True)
        prop['uid']= prop.index + 1
        print (i)
        file_path = (file_path + str.lower(i) + "_GDA94.shp")
        shapefile_list.append(file_path)
        #print(prop.crs)
        prop.crs = {'init': 'EPSG:4283'}
        prop_gda94 = prop
        #print(prop_gda94.crs)
        #fig, ax = plt.subplots(figsize = (10,10))
        #prop_gda94.plot(ax=ax)
        #plt.show()
        prop_gda94.to_file(file_path, driver = 'ESRI Shapefile')
        print("--------------------------\n Export of " + i + " with " + prop.crs + " complete. \n ----------------------"
        
        return (prop_gda94)
    


def mainRoutine():
    
    # read in the command arguments
    cmdargs = getCmdargs()
    cadastre = cmdargs.cadastre
    excel= cmdargs.excel
    file_path = cmdargs.file_path 
    #uid = cmdargs.uid
    #shapefilelist = cmdargs.shapefile_list

    # Import in the cadastre and ensure the crs is set to GDA94
    cadastre = gpd.read_file(cadastre)
    #cadastre.head()
    print("Cadastre crs: ", cadastre.crs)


    #read in an excel sheet with all of the property names
    properties = pd.read_excel(excel)
    properties["Property"] = properties["Property"].str.upper()
    prop_list = properties.Property.unique().tolist()

    properties(cadastre, file_path)
              
if __name__ == "__main__":
    mainRoutine() 