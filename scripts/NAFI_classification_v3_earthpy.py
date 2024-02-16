# raster2array.py reads in the first band of geotif file and returns an array and associated 
# metadata dictionary

import numpy as np
import warnings
warnings.filterwarnings('ignore')
from osgeo import gdal
import numpy as np
import copy
#import matplotlib.colors as colors
import gdal, osr #ogr, os, osr
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap
import matplotlib.colors as colors
import seaborn as sns
import numpy as np
import rasterio as rio
from rasterio.plot import plotting_extent
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep

# prettier plotting with seaborn
sns.set(font_scale=1.5, style="whitegrid")

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
    
    # Get data and set working directory
    et.data.get_data(nafi_raster)


    print('----------------------\n script has finished \n ----------------')

if __name__ == "__main__":
    mainRoutine() 