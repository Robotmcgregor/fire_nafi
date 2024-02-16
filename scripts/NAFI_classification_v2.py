# raster2array.py reads in the first band of geotif file and returns an array and associated 
# metadata dictionary

import numpy as np
import gdal
import matplotlib.pyplot as plt
%matplotlib inline
import warnings
warnings.filterwarnings('ignore')
from osgeo import gdal
import numpy as np
import copy
#import matplotlib.colors as colors
import gdal, osr #ogr, os, osr
import numpy as np

def getCmdargs():

    p = argparse.ArgumentParser(description="""Input a single or multiband raster to extracts the values from the input shapefile. """)

    p.add_argument("-n","--nafi_raster", help="NAFI raster that has not been classified")
        
    p.add_argument("-o","--output", help="Output location and name including file extension (.tif)")
    
    #p.add_argument("-f","--file_path", help="Output shapefile directory")
    

    cmdargs = p.parse_args()
    
    if cmdargs.nafi_raster is None:

        p.print_help()

        sys.exit()

    return cmdargs

def mainRoutine():        
           
    cmdargs = getCmdargs()
    nafi_raster = cmdargs.nafi_raster
    output = cmdargs.output

    def raster2array(geotif_file):
        metadata = {}
        dataset = gdal.Open(geotif_file)
        metadata['array_rows'] = dataset.RasterYSize
        metadata['array_cols'] = dataset.RasterXSize
        metadata['bands'] = dataset.RasterCount
        metadata['driver'] = dataset.GetDriver().LongName
        metadata['projection'] = dataset.GetProjection()
        metadata['geotransform'] = dataset.GetGeoTransform()

        mapinfo = dataset.GetGeoTransform()
        metadata['pixelWidth'] = mapinfo[1]
        metadata['pixelHeight'] = mapinfo[5]

        metadata['ext_dict'] = {}
        metadata['ext_dict']['xMin'] = mapinfo[0]
        metadata['ext_dict']['xMax'] = mapinfo[0] + dataset.RasterXSize/mapinfo[1]
        metadata['ext_dict']['yMin'] = mapinfo[3] + dataset.RasterYSize/mapinfo[5]
        metadata['ext_dict']['yMax'] = mapinfo[3]

        metadata['extent'] = (metadata['ext_dict']['xMin'],metadata['ext_dict']['xMax'],
                              metadata['ext_dict']['yMin'],metadata['ext_dict']['yMax'])

        if metadata['bands'] == 1:
            raster = dataset.GetRasterBand(1)
            metadata['noDataValue'] = raster.GetNoDataValue()
            metadata['scaleFactor'] = raster.GetScale()

            # band statistics
            metadata['bandstats'] = {} #make a nested dictionary to store band stats in same 
            stats = raster.GetStatistics(True,True)
            metadata['bandstats']['min'] = round(stats[0],2)
            metadata['bandstats']['max'] = round(stats[1],2)
            metadata['bandstats']['mean'] = round(stats[2],2)
            metadata['bandstats']['stdev'] = round(stats[3],2)

            array = dataset.GetRasterBand(1).ReadAsArray(0,0,metadata['array_cols'],metadata['array_rows']).astype(np.float)
            array[array==int(metadata['noDataValue'])]=np.nan
            array = array/metadata['scaleFactor']
            return array, metadata

        elif metadata['bands'] > 1:
            print('More than one band ... need to modify function for case of multiple bands')
        
        
    NAFI_array, NAFI_metadata = raster2array(r"Z:\Scratch\Zonal_Stats_Pipeline\Firescars\NAFI_fire_rasters_v2\fs2020.tif")

    print('NAFI_Array: ',NAFI_array)

    #print metadata in alphabetical order
    for item in sorted(NAFI_metadata):
    print(item + ':', NAFI_metadata[item])


    
    NAFI_reclass = copy.copy(NAFI_array)
    NAFI_reclass[np.where(NAFI_array== 0)] = 255 # Class No data
    NAFI_reclass[np.where((NAFI_array>=1) & (NAFI_array<=8))] = 1 #  Class Jan
    NAFI_reclass[np.where((NAFI_array>=8) & (NAFI_array<=16))] = 2 #  Class Feb
    NAFI_reclass[np.where((NAFI_array>=17) & (NAFI_array<=26))] = 3 # March
    NAFI_reclass[np.where((NAFI_array>=27) & (NAFI_array<=36))] = 4 #  April
    NAFI_reclass[np.where((NAFI_array>=37) & (NAFI_array<=55))] = 5 #  Class May
    NAFI_reclass[np.where((NAFI_array>=56) & (NAFI_array<=84))] = 6 #  Class June
    NAFI_reclass[np.where((NAFI_array>=85) & (NAFI_array<=115))] = 7 #  Class July
    NAFI_reclass[np.where((NAFI_array>=116) & (NAFI_array<=145))] = 8 #  Class August
    NAFI_reclass[np.where((NAFI_array>=146) & (NAFI_array<=175))] = 9 #  Class September
    NAFI_reclass[np.where((NAFI_array>=176) & (NAFI_array<=205))] = 10 #  Class October
    NAFI_reclass[np.where((NAFI_array>=206) & (NAFI_array<=231))] = 11 #  Class November
    NAFI_reclass[np.where((NAFI_array>=232) & (NAFI_array<=255))] = 12 #  Class December
    #NAFI_reclass[np.where(NAFI_array>=176)] = 255 #  Class No data
    """NAFI_reclass[np.where((NAFI_array>206) & (NAFI_array<=231))] = 11 #  Class November
    NAFI_reclass[np.where((NAFI_array>232) & (NAFI_array<=254))] = 12 #  Class December"""
    #NAFI_reclass[np.where(NAFI_array== 0)] = 10 # Class No data

    print('Min:',np.nanmin(NAFI_reclass))
    print('Max:',np.nanmax(NAFI_reclass))
    print('Mean:',round(np.nanmean(NAFI_reclass),2))


    #plt.figure(); #ax = plt.subplots()
    """cmapNAFI = colors.ListedColormap([
        'black',
        'peru',
        'peachpuff',
        'yellowgreen',
        'khaki',
        'red',
        'orange',
        'darkred',
        'red',
        'springgreen',
        'white'
    ])

    extents=[6000,1200,0,500]

    plt.imshow(NAFI_reclass,  cmap=cmapNAFI) #extent=extents,
    plt.title('NAFI month breakdown')
    ax=plt.gca(); ax.ticklabel_format(useOffset=False, style='plain') #do not use scientific notation 
    rotatexlabels = plt.setp(ax.get_xticklabels(),rotation=90) #rotate x tick labels 90 degrees
    # forceAspect(ax,aspect=1) # ax.set_aspect('auto')"""

    # Create custom legend to label the four canopy height classes:
    """import matplotlib.patches as mpatches
    class1_box = mpatches.Patch(color='peru', label='Jan')
    class2_box = mpatches.Patch(color='peachpuff', label='Feb')
    class3_box = mpatches.Patch(color='yellowgreen', label='Mar')
    class4_box = mpatches.Patch(color='khaki', label='April')
    class5_box = mpatches.Patch(color='red', label='May')
    class6_box = mpatches.Patch(color='orange', label='June')
    class7_box = mpatches.Patch(color='darkred', label='July')
    class8_box = mpatches.Patch(color='red', label='Aug')
    class9_box = mpatches.Patch(color='springgreen', label='Sep')
    class10_box = mpatches.Patch(color='blue', label='Oct')
    #class11_box = mpatches.Patch(color='tan', label='Nov')
    #class12_box = mpatches.Patch(color='maroon', label='Dec')
    #class13_box = mpatches.Patch(color='red', label='No data')
    #class14_box = mpatches.Patch(color='black', label='255')



    ax.legend(handles=[class1_box,class2_box,class3_box,class4_box, class5_box, class6_box,
                      class7_box,class8_box,class9_box],
              handlelength=0.7,bbox_to_anchor=(1.05, 0.4),loc='lower left',borderaxespad=0.)"""

    # %load ../hyperspectral_hdf5/array2raster.py
    """
    Array to Raster Function from https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html)
    """


    def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array,epsg):

        cols = array.shape[1]
        rows = array.shape[0]
        originX = rasterOrigin[0]
        originY = rasterOrigin[1]

        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(epsg)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()
    
    # array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array)
    epsg = 4283   # GDA94 
    rasterOrigin = (NAFI_metadata['ext_dict']['xMin'],NAFI_metadata['ext_dict']['yMax'])
    print('raster origin:',rasterOrigin)
    array2raster('NAFI_Classifiedtest2.tif',rasterOrigin,1,-1,NAFI_reclass,epsg)
    print('----------------------\n script has finished \n ----------------')

if __name__ == "__main__":
    mainRoutine() 