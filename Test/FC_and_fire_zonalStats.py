from __future__ import print_function, division
import pdb
import fiona
import rasterio
import pandas as pd 
import argparse
from rasterstats import zonal_stats 
from rasterstats import point_query
import sys
import os
import shutil
import glob
import numpy as np

def getCmdargs():

    p = argparse.ArgumentParser(description="""Input a single or multiband raster to extracts the values from the input shapefile. The script currently outputs a csv file containing the unique identifyer for each point, the value of the raster is returned.""")

    p.add_argument("-i","--imlist", help="Input image to derive zonal stats from")
        
    p.add_argument("-n","--nodata", help="define the no data value for the input raster image")
    
    p.add_argument("-s","--shape", help="shape file contiaing the zones needs to have a field defined as id")
    
    p.add_argument("-u","--uid", help="input the column name for the unique id field in the shapefile") 
    
    p.add_argument("-o","--csv", help="name of the output csv file containing the results")
    
    cmdargs = p.parse_args()
    
    if cmdargs.imlist is None:

        p.print_help()

        sys.exit()

    return cmdargs


def applyZonalstats(imageS, nodata, shape, uid):

    # create empty lists to append values
    zonestats = []
    site_li = []
    uid_li =[]
    image_name = []
    image_date = []
    #band_li = []
    nodata = nodata

    with rasterio.open(imageS, nodata=nodata) as srci:
        affine = srci.transform #srci.transform is the new srci.affine
        #array = srci.read(band)

        with fiona.open(shape) as src:
            # using "all_touched=True" will increase the number of pixels used to produce the stats "False" reduces the number
            # define the zonal stats being calculated
            
             # map the catagorical valeues
            cmap = {1: 'Jan', 2: 'Feb', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            
            zs = zonal_stats(src, affine=affine, nodata=nodata, stats=['count', 'min', 'max', 'mean','median', 'std'],all_touched=True) 
             
            # extract image name and append to list
            imgName = str(srci)[-25:-10]
            print("imgName: ", imgName)
            image_name.append(imgName)
            # extract image date and append to list
            imgDate = str(srci)[-23:-19]
            print("imgDate: ", imgDate)
            image_date.append(imgDate)

            for zone in zs:
                #bands = "b" + str(band)
                #band_li.append(bands)
                # extract "values" as a tuple from a dictonary
                keys, values = zip(*zone.items())
                # convert tuple to a list and append to zonestats
                result = list(values)
                zonestats.append(result)
                #print("Keys: ", keys)
                #print("Values: ", values)


            for i in src:
                # extract shapefile records
                table_attributes = i['properties']  

                uid_ = table_attributes[uid]  
                details = [uid_]
                uid_li.append(details)
                
                site = table_attributes["PROP_NAME"]
                site_ = [site]
                site_li.append(site_)

        # join the elements in each of the lists row by row 
        finalresults =  [uid_li + site_li + zonestats  for uid_li, site_li,  zonestats in zip(uid_li, site_li, zonestats)] 

        # close the vector and raster file 
        src.close() 
        srci.close() 

        # print out the file name of the processed image
        print (imgName + ' ' + 'zone stats are complete')
    
    return(finalresults)

'''def time_stamp(concatenated_df):
    
    #Convert the date to a time stamp
    time_stamp = pd.to_datetime(concatenated_df.date, format="%Y%m%d")
    concatenated_df.insert(4, "time_stamp", time_stamp)
    #concatenated_df.loc[:,~concatenated_df.columns.duplicated()].dropna(0)
    concatenated_df['year'] = concatenated_df['date'].map(lambda x: str(x)[:4])
    concatenated_df['month'] = concatenated_df['date'].map(lambda x: str(x)[4:6])
    concatenated_df['day'] = concatenated_df['date'].map(lambda x: str(x)[6:])
    
    return concatenated_df

def Landsat_correction(concatenated_df):
    # min imports a zero as a minimum
    concatenated_df['b1_min']=concatenated_df['b1_min'].replace(0, np.nan)
    concatenated_df['b2_min']=concatenated_df['b1_min'].replace(0, np.nan)
    concatenated_df['b3_min']=concatenated_df['b1_min'].replace(0, np.nan)
    # band 1
    #concatenated_df['b1_count'] = concatenated_df['b1_count'] -100
    concatenated_df['b1_min'] = concatenated_df['b1_min'] -100
    concatenated_df['b1_max'] = concatenated_df['b1_max'] -100
    concatenated_df['b1_mean'] = concatenated_df['b1_mean'] -100
    concatenated_df['b1_median'] = concatenated_df['b1_median'] -100

    # band 2
    #concatenated_df['b2_count'] = concatenated_df['b2_count'] -100
    concatenated_df['b2_min'] = concatenated_df['b2_min'] -100
    concatenated_df['b2_max'] = concatenated_df['b2_max'] -100
    concatenated_df['b2_mean'] = concatenated_df['b2_mean'] -100
    concatenated_df['b2_median'] = concatenated_df['b2_median'] -100
    
    # band 3
    #concatenated_df['b3_count'] = concatenated_df['b3_count'] -100
    concatenated_df['b3_min'] = concatenated_df['b3_min'] -100
    concatenated_df['b3_max'] = concatenated_df['b3_max'] -100
    concatenated_df['b3_mean'] = concatenated_df['b3_mean'] -100
    concatenated_df['b3_median'] = concatenated_df['b3_median'] -100
     
    return concatenated_df'''

def mainRoutine():
        
    # read in the command arguments
    cmdargs = getCmdargs()
    imlist = cmdargs.imlist
    nodata= int(cmdargs.nodata)
    shape = cmdargs.shape 
    uid = cmdargs.uid
    export_csv = cmdargs.csv  

    # check if the "temp_individual_bands" file already exists and delete it if it does.
    tempDir = 'temp_individual_bands'       
    try:
        shutil.rmtree(tempDir)
    
    except:
        print("The following directory was deleted: ", tempDir)
    
    # create temporary folders
    tempDir = 'temp_individual_bands'
    os.makedirs(tempDir)
    '''band1Dir = (tempDir + '//band1')
    os.makedirs(band1Dir)
    band2Dir = (tempDir + '//band2')
    os.makedirs(band2Dir)
    band3Dir = (tempDir + '//band3')
    os.makedirs(band3Dir)'''
    
    #specify the number of bands that zonal stats will be derived from (default is three -GDAL numbering)
    #num_bands = [1, 2, 3]

    #for band in num_bands:
    # open the list of imagery and read it into memory and call the applyZonalstats function
    with open(imlist, "r") as imagerylist:

        #Extract each image path from the image list
        for image in imagerylist:

            # cleans the file pathway (Windows)
            imageS = image.rstrip()
            im_name =imageS[-12:]
            print("Image name: ", im_name)
            im_date =imageS[-12:-8]
            print("im_date: ", im_date )

            # loops through each image
            with rasterio.open(imageS, nodata=nodata) as srci:
                imageResults = 'image_' + im_name + '.csv'

                # runs the zonal stats function and outputs a csv in a band specific folder
                finalresults = applyZonalstats(imageS, nodata, shape, uid)
                header = ['number', 'site', 'min', 'max', 'mean', 'count', 'std', 'median']

                df  = pd.DataFrame.from_records(finalresults, columns = header)
                #df['band']= band
                df['image']= im_name
                df['date']= im_date
                df.to_csv(tempDir + '//im_name'+ '//' + imageResults, index=False)
                
                        
                        
    '''---------------------------------------------------Concatenate csv-----------------------------------------------------'''
    # for loops through the band folders and concatenates zonal stat outputs into a complete band specific csv   
    '''for x in num_bands:
        output_loc = tempDir+'//band'+str(x)
        band_files = glob.glob(os.path.join(output_loc, "*.csv")) # advisable to use os.path.join as this makes concatenation OS independent
        df_from_each_band_file = (pd.read_csv(f) for f in band_files)
        concat_band_df   = pd.concat(df_from_each_band_file,ignore_index=False, axis=0, sort=False)
        # export the band specific results to a csv file (i.e. three outputs)
        concat_band_df.to_csv(tempDir + '//'+ "Band" + str(x)+ "_test.csv",index=False)'''
        
    
    '''-----------------------------------------Concatenate three bands together--------------------------------------------------'''
    
    #Concatenate Three bands
    '''header_all = ['ident', 'site', 'b1_min', 'b1_max', 'b1_mean', 'b1_count', 'b1_std', 'b1_median', 'band', 'image', 'date', 'b2_ident', 'b2_site', 'b2_min', 'b2_max', 'b2_mean', 'b2_count', 'b2_std', 'b2_median','band2', 'image2', 'date2', 'b3_number', 'b3_site',  'b3_min', 'b3_max', 'b3_mean', 'b3_count', 'b3_std', 'b3_median', 'band3', 'image3', 'date3']
    all_files = glob.glob(os.path.join(tempDir, "*.csv")) # advisable to use os.path.join as this makes concatenation OS independent
    df_from_each_file = (pd.read_csv(f) for f in all_files)
    concatenated_df = pd.concat(df_from_each_file,ignore_index=False, axis=1, sort=False)
    concatenated_df.columns = header_all'''
    
    
    '''--------------------------------------------------Clean dataframe--------------------------------------------------------'''
    
    #Convert the date to a time stamp
    #time_stamp(concatenated_df)
    
    # remove 100 from zonestats
    #Landsat_correction(concatenated_df)
    
    # reshape the final dataframe
    '''concatenated_df = concatenated_df[['ident', 'site', 'image', 'year', 'month', 'day', 'b1_min', 'b1_max', 'b1_mean', 'b1_count', 'b1_std', 'b1_median', 'b2_min', 'b2_max', 'b2_mean', 'b2_count', 'b2_std', 'b2_median', 'b3_min', 'b3_max', 'b3_mean', 'b3_count', 'b3_median', 'b3_std']]'''
    
    # export the results to a csv file
    #concatenated_df.to_csv(cmdargs.csv,index=False)

    '''-----------------------------------------------Delete temporary files--------------------------------------------------'''
    # remove the temp dir and single band csv files
    #shutil.rmtree(tempDir)
    print("Script has finished")
            

if __name__ == "__main__":
    mainRoutine()   