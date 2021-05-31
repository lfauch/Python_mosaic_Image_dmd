# -*- coding: utf-8 -*-
"""
File: LF_Main_Read_dmd_File.py
Created on Fri Mar 26 20:34:00 2021

@author: laure
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage # Pour median filter


import Mdl_read_Mosaique_dmt as FTIR # Lire les image FTIR

#
path = 'E:/LUU_FTIR/test/LOS00001/'
fichier = 'LOS00001.dat'
FTIRdata = FTIR.mcla_AgilentFTIR(path,fichier) # Object creation 
print(FTIRdata.name)
FTIRdata.get_DataCubeMosaique()
datacube1 = FTIRdata.data
Wavenumber1 = FTIRdata.wavenumbers
#*
plt.figure()
plt.imshow(datacube1[:,:,945])
plt.title('Amide I with .dmd of mosaïque, Correct image')
plt.grid()
plt.colorbar()
#*

# Data processing by device ==> .dat
FTIRdata1 = FTIR.mcla_AgilentFTIR(path,fichier) # Object creation 
print(FTIRdata.name)
FTIRdata1.get_DataCubeSingle()
datacube1 = FTIRdata1.data
#*
plt.figure()
plt.imshow(datacube1[:,:,945])
plt.title('Amide I with .dat of mosaique, too small image')
plt.grid()
plt.colorbar()
#*

# Seond objet une seule image
path = 'E:/LUU_FTIR/test/LEOS00002/'
fichier = 'LOS00002.dat'   
FTIRdataSimple = FTIR. mcla_AgilentFTIR(path,fichier) # Object creation 
print(FTIRdataSimple.name)
FTIRdataSimple.get_DataCubeSingle()
datacubeSimple = FTIRdataSimple.data
#*
plt.figure()
plt.imshow(datacubeSimple[:,:,945])
plt.title('Amide I Simple with .dat')
plt.grid()
#*
