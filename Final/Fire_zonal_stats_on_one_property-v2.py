#!/usr/bin/env python

"""
Read in NAFI fire scap mapping rasters and polygon shapefile, perform classified zonal statstic analysis and return a csv of the results. I have added the ability to chose the band to run the zonal stats on. The default is band 2 pv
Author: Rob McGregor
Date: 01/10/2020
Modified 05/12/2018
"""


from __future__ import print_function, division
import pdb
import fiona
import rasterio
import pandas as pd 
import argparse
from rasterstats import zonal_stats 
#from rasterstats import point_query
import sys
import os
import shutil
import glob
import numpy as np

def getCmdargs():

    p = argparse.ArgumentParser(description="""Input a single or multiband raster to extracts the values from the input shapefile. """)

    p.add_argument("-i","--imlist", help="Input image to derive zonal stats from")
        
    p.add_argument("-n","--nodata", help="define the no data value for the input raster image")
    
    p.add_argument("-s","--shape", help="shape file contiaing the zones needs to have a field defined as id")
    
    p.add_argument("-u","--uid", help="input the column name for the unique id field in the shapefile") 
    
    p.add_argument("-o","--csv", help="name of the output csv file containing the results")
    
    p.add_argument("-b","--shapefilelist", help="list of property shapefile paths")
    
    
    cmdargs = p.parse_args()
    
    if cmdargs.imlist is None:

        p.print_help()

        sys.exit()

    return cmdargs



# def proplist (

'''-------------------------------------------------------------------------------------------------------------'''


def listdir(dirname,endfilename,scratchDir):

# this function will return a list of files in a directory for the given file extention "endfilename". 

list_img = []

for root, dirs, files in os.walk(dirname):
    for file in files:
        if file.endswith('MTH.tif'):
            img = (os.path.join(root, file))
            list_img.append(img)
            #print (img)
            shutil.copy(os.path.abspath(img), tempDir)
print("Fire raster files have been copied.")

return list_img

'''-----------------------------------------------------------------------------------------------------------'''

def applyZonalstats(imageS, nodata, shape, tempDir):

    # create empty lists to append values
    #image_name =[]
    #image_date =[]
    #site_li =[]
    #zoneclass =[]
    #zoneresults =[]
    total_uid_list = []
    laiskey_list = []
   

    with rasterio.open(imageS, nodata=nodata) as srci:
        affine = srci.transform #srci.transform is the new srci.affine
        array = srci.read(1)

        with fiona.open(shape) as src:
            # using "all_touched=True" will increase the number of pixels used to produce the stats "False" reduces the number

            cmap = {1: 'Jan', 2: 'Feb', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                    7: 'July', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            zs = zonal_stats(src, array, affine=affine, stats=['count'],
                             categorical=True, category_map=cmap, nodata = nodata, all_touched=False)
            #print("ZS: ", zs)
            #print("Array: ", array)
            
            # extract image name and append to list
            imgName = str(srci)[86:-11]
            #print("imgName: ", imgName)
            image_name.append(imgName)
            # extract image date and append to list
            imgDate = str(imgName)[2:6]
            #print("imgDate: ", imgDate)
            image_date.append(imgDate)

            df  = pd.DataFrame.from_records(zs)
            df.insert(0, 'image', imgName)
            df.insert(0, 'year', imgDate)
           
            # extract image name and append to list
            """print("imageS: ", imageS)
            imgName = imageS[-14:]
            print("imgName: ", imgName)
            image_name.append(imgName)
            # extract image date and append to list
            imgDate = str(imgName)[-12:-8]
            print("imgDate: ", imgDate)
            image_date.append(imgDate)

            finalresults = pd.DataFrame.from_records(zs)
            finalresults.insert(0, 'image', imgName)
            finalresults.insert(0, 'year', imgDate)"""
            
            for i in src:
                uid_list = []
                # extract shapefile records
                table_attributes = i['properties'] 

                laiskey_ = table_attributes["LAISKEY"]
                laiskey_string = str(laiskey_)
                laiskey_list.append(laiskey_string)
                total_laiskey_list.append(laiskey_string)
                #print("TOTAL_UID_LIST as it happens: ", total_uid_list)

                prop = table_attributes["PROP_NAME"]
                property_list.append(prop)
                #print("UID_LIST: ", uid_list)

                uid_ = table_attributes["uid"]
                uid_string = str(uid_)
                uid_list.append(uid_string)
                total_uid_list.append(uid_string)

        df['uid_final'] = total_uid_list
        df['Laiskey'] = laiskey_list
        print("TOTAL_UID_LIST: ", total_uid_list)

        df['band']= 1
        print("============================================================================")
        print(df)
        print("----------------------------------------------------------------------------")
        df.to_csv(tempDir + '//' + imageResults, index=False) 

        srci.close()

        # print out the file name of the processed image
        print (imgName + ' ' + imgDate +  ' ' + 'zone stats are complete')

        return(df)
            

        '''for i in src:
            # extract shapefile records
            table_attributes = i['properties']  

            prop = table_attributes["PROP_NAME"]
            finalresults.insert(0, 'property', prop)

            print("Final Results: ", finalresults)
            finalresults.to_csv(tempDir + '//' + imgName + '_' + imgDate + '.csv', index=False) 

            srci.close()

            # print out the file name of the processed image
            print (imgName + ' ' + imgDate +  ' ' + 'zone stats are complete')'''

            #return(finalresults)

            '''------------------------------------------------------------------------------------------------------------------'''

def mainRoutine():
        
    # read in the command arguments
    cmdargs = getCmdargs()
    imlist = cmdargs.imlist
    nodata= int(cmdargs.nodata)
    shape = cmdargs.shape 
    uid = cmdargs.uid
    shapefilelist = cmdargs.shapefile_list
    
    #dirname = cmdargs.dirname
    export_csv = cmdargs.csv
    
    for shape in shapefile_list:
        shape.strip()

        # check if the "temp_individual_bands" file already exists and delete it if it does.
        tempDir = 'temp_folder'       
        try:
            shutil.rmtree(tempDir)

        except:
            print("The following directory was deleted: ", tempDir)

        # create temporary folders
        tempDir = 'temp_folder'
        os.makedirs(tempDir)
    
        # Create a list of all of the annual fire raster’s.
        listdir(dirname,tempDir)
        
    
        with open(imlist, "r") as imagerylist:

            #Extract each image path from the image list
            for image in imagerylist:
                #print(image)

                # cleans the file pathway (Windows)
                '''imageS = image.rstrip()
                print("imageS: ", imageS)
                im_name = imageS[-14:]
                print(im_name)'''
                
                # cleans the file pathway (Windows)
                imageS = image.rstrip()
                #print("imageS: ", imageS)
                im_name = imageS[60:]
                #print("Im_Name: ", im_name)
                
                # loops through each image
                with rasterio.open(imageS, nodata= nodata) as srci:
                    imageResults = 'image_' + im_name + '.csv'
                    # runs the zonal stats function and outputs a csv in a band specific folder
                    finalresults = applyZonalstats(imageS, nodata, shape, tempDir)
                    #finalresults = applyZonalstats(imageS, nodata, band, shape, uid)
    
    property_name = shape.rstrip()
    print("Property name: ", property_name)
    clean_prop_name = property_name[98:-4]
    print("Clean_Prop_Name: ", clean_prop_name)
    
    # for loops through the band folders and concatenates zonal stat outputs into a complete band specific csv   
    band_files = glob.glob(os.path.join(tempDir, "*.csv")) # advisable to use os.path.join as this makes concatenation OS independent
    df_from_each_band_file = (pd.read_csv(f) for f in band_files)
    concat_band_df   = pd.concat(df_from_each_band_file,ignore_index=False, axis=0, sort=False)
    #concat_band_df = concat_band_df.insert(0, 'property', prop)
    # export the band specific results to a csv file (i.e. three outputs)
    concat_band_df.to_csv(export_csv + '\\' + clean_prop_name + "_fire_scar.csv",index=False)
                    
                    
    
    #os.chdir(r'temp_folder')    
    # for loops tempDir folders and concatenates .csv outputs into a property specific csv   
    '''prop_fire = glob.glob(os.path.join(tempDir, "*.csv")) # advisable to use os.path.join as this makes concatenation OS independent
    print(prop_fire)
    prop_fire_df = (pd.read_csv(f) for f in prop_fire)
    concat_prop_fire_df = pd.concat(prop_fire_df, ignore_index=False, axis=0, sort=False)
    # export the band specific results to a csv file (i.e. three outputs)
    concat_prop_fire_df.to_csv(tempDir +  "property_output.csv",index=False)''' 


    '''-----------------------------------------------Delete temporary files--------------------------------------------------'''
    # remove the temp dir and single band csv files
    #shutil.rmtree(tempDir)
    print("Script has finished")
            

if __name__ == "__main__":
    mainRoutine()   