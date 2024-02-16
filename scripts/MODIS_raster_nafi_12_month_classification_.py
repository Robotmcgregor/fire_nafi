#!/usr/bin/env python

"""
This script will reclassify MODIS derived NAFI fire scars so that the pixel vaules represtent months (i.e. 1-12).

Author: Rob McGregor
email: Robert.McGregor@ntg.gov.au
Date:15/10/2020
"""

# import the modules
import sys
import os
import argparse
import pdb
import numpy as np 
from rios import applier, fileinfo


def getCmdargs():

    p = argparse.ArgumentParser()

    
    p.add_argument("-i","--inimage", help="input unclassified NAFI firescar image to process")
    
    p.add_argument("-o","--output", help="directory path and name of the output image")
    
    p.add_argument("-b","--band", default= 0 ,help="input band to produce density slice from. options;0 = bare soil this is default, 1 = pv fraction, 2 = npv fraction (default is %(default)s)")
    
    cmdargs = p.parse_args()
    
    if cmdargs.inimage is None:

        p.print_help()

        sys.exit()

    return cmdargs



def mainRoutine():
    
    cmdargs = getCmdargs()
    
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    otherargs = applier.OtherInputs()
    
    infiles.seasComp = cmdargs.inimage
    outfiles.ds = cmdargs.output
    otherargs.b = cmdargs.band
   
    controls = applier.ApplierControls()
    controls.setOutputDriverName('GTiff')
    options = ['COMPRESS=LZW', 'BIGTIFF=YES', 'TILED=YES', 'INTERLEAVE=BAND','BLOCKXSIZE=256','BLOCKYSIZE=256']
    controls.setCreationOptions(options)
    controls.setWindowXsize(256)
    controls.setWindowYsize(256)
    #controls.setStatsIgnore(0)
    #controls.setReferenceImage(infiles.seasComp)
    
    

    applier.apply(densitySlice, infiles, outfiles, otherargs,controls=controls)  



def densitySlice(info, inputs, outputs, otherargs):
    
    """
    
    function to convert values below 0.52m and above 50m in the lidar canopy height value to nodata  
    
    """
    NAFI_reclass = np.array(inputs.seasComp[otherargs.b])
    #sc10[sc10 <= 0] = 0.0
    #sc10[sc10 >= 10.000001] = 0
    
    NAFI_reclass[np.where(NAFI_array== 0)] = 0.0 # No fire
    NAFI_reclass[np.where((NAFI_array>=1) & (NAFI_array<=8))] = 1.0 #  Class Jan
    NAFI_reclass[np.where((NAFI_array>=9) & (NAFI_array<=16))] = 2.0 #  Class Feb
    NAFI_reclass[np.where((NAFI_array>=17) & (NAFI_array<=26))] = 3.0 # March
    NAFI_reclass[np.where((NAFI_array>=27) & (NAFI_array<=36))] = 4.0 #  April
    NAFI_reclass[np.where((NAFI_array>=37) & (NAFI_array<=55))] = 5.0 #  Class May
    NAFI_reclass[np.where((NAFI_array>=56) & (NAFI_array<=84))] = 6.0 #  Class June
    NAFI_reclass[np.where((NAFI_array>=85) & (NAFI_array<=115))] = 7.0 #  Class July
    NAFI_reclass[np.where((NAFI_array>=116) & (NAFI_array<=145))] = 8.0 #  Class August
    NAFI_reclass[np.where((NAFI_array>=146) & (NAFI_array<=175))] = 9.0 #  Class September
    NAFI_reclass[np.where((NAFI_array>=176) & (NAFI_array<=205))] = 10.0 #  Class October
    NAFI_reclass[np.where((NAFI_array>=206) & (NAFI_array<=231))] = 11.0 #  Class November
    NAFI_reclass[np.where((NAFI_array>=232) & (NAFI_array<255))] = 12.0 #  Class December
    NAFI_reclass[np.where(NAFI_array>=255)] = 255.0 #  Class No data
    
    
    
    # for defining the srtm dem and derived products nodata value
    #sc10[sc10 == np.nan] = -9999.0
        
    output = np.array([NAFI_reclass],dtype=np.float32)
    
        
    outputs.ds = output


    
if __name__ == "__main__":
    mainRoutine()