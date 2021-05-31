# -*- coding: utf-8 -*-
"""
File: Mdl_read_Mosaique_dmt.py
Created on Thu Mar 25 08:53:40 2021

Class name : mcla_AgilentFTIR:
    Attibuts : 
        path : the data-folder path
        fichier : the name of the file .dat with its extension
        name: base of file name : file.dat without extension
        wavenumbers : column array of wavenumbers
        tiles_in_x : numbers of tiles in horizontal
        tiles_in_y: numbers of tiles in vertical
        data: FTIR datacube
    Methods:
        private:
        __get_ExtractBaseName(): get the filename base of .dat file
        __get_Wavenumbers(): get an column array of wavenumbers
        __get_WavenumbersMosaique(): get an column array of wavenumbers
        __get_CalculTileNumber(): get the number of tile in x and y directions
        __get_LoadDataCubeMosaique(): Load the datacube for mosaique
        __get_LoadDataCubeSingle(): Load the datacube for single tile acquisition
        public:
        get_DataCubeMosaique(): Get the dataCube for mosaïque
        get_DataCubeSingle(): for a single tile acquisition
INPUT : 
    Path: Path of datafolder with / at the end
    File: Name of .dat file with the extension .dat
OUTPUT:
    wavenumbers : array of wavenumbers
    data : raw datacube
    
@author: laure
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
from matplotlib import mlab
import pandas as pd
import scipy.io
import array
from pathlib import Path as fexiste

import os, sys
#from __future__ import unicode_literals # pour l'encodage uniform

#path = 'D:/Mes/071109_140319/'
#fichier = '071109_140319.dat'

path = 'E:/LUU_FTIR/test/LUU71212_p6/'
fichier = 'LUU71212_p6.dat'

class mcla_AgilentFTIR:
    # attribut
    def __init__(self,path='1',fichier='1'):
        self.path,self.fichier = path, fichier
        self.filename = self.path + self.fichier
        self.__get_ExtractBaseName()
    def __get_ExtractBaseName(self):
        pathstr,nameExt = os.path.split(self.filename)
        self.name = os.path.splitext(nameExt)[0]
        self.name = self.name.lower() # Put the file name in small letters
    def __get_WavenumbersMosaique(self):
        dmtfilename = self.path + self.name+'.dmt'  # Attach the path and the basename to the extention .dmt
        try :
            with open(dmtfilename, "r", encoding="Latin-1") as fid: 
                status = fid.seek(2228, 0)
                dt = np.int32
                nelements = 1
                startwavelength = np.fromfile(fid, dt, nelements)
                startwavelength.shape = (nelements, 1)
                #startwavelength = np.double(startwavelength)
                print('Start wave:',startwavelength) # 777
                status = fid.seek(2236, 0)
                nelements = 1
                numberofpoints = np.fromfile(fid, dt, nelements)
                numberofpoints.shape = (nelements, 1)
                print('Number of point:',numberofpoints)
                #numberofpoints = np.double(numberofpoints)
                status = fid.seek(2216, 0) # 0
                dt = np.double
                nelements = 1        
                wavenumberstep = np.fromfile(fid, dt, nelements)
                wavenumberstep.shape = (nelements, 1) 
                print('step:',wavenumberstep)
        except FileNotFoundError:
            sys.exit('File ' + str(dmtfilename)+' does not exist')
        #wavenumbers = np.linspace(startwavelength,numberofpoints+startwavelength,np.int32(numberofpoints))
        #wavenumbers = wavenumbers * wavenumberstep
        #self.wavenumbers = wavenumbers[0]
        wavenumbers = np.linspace(startwavelength[0,0],numberofpoints[0,0]+startwavelength[0,0],np.int32(numberofpoints[0,0]))
        self.wavenumbers = wavenumbers * wavenumberstep[0,0] 
        #wavenumbers = np.linspace(0,numberofpoints[0,0]-1,np.int32(numberofpoints[0,0]))
        #self.wavenumbers = (wavenumbers * wavenumberstep[0,0]) + startwavelength[0,0]
    def __get_CalculTileNumber(self):
        basefilename = self.path + self.name # POUR TILE
        # Test there is .dmd file
        try: 
            with open(basefilename+"_0000_0000.dmd", "r", encoding="Latin-1") as fid:
                status = fid.seek(0, 0)
        except FileNotFoundError:
            sys.exit('File ' + str(basefilename+"_0000_0000.dmd")+' does not exist')
        # If it exists do:   
        tiles_in_x = 1    
        finished = False
        counter = 0
        while finished != True:
            current_extn = "_%04d_0000.dmd" % (counter) 
            tempfilename = basefilename+current_extn        
            my_file = fexiste(tempfilename)
            if my_file.is_file():
                counter += 1
            else :
                tiles_in_x = counter
                finished = True
        self.tiles_in_x = tiles_in_x 
        # return tiles_in_x_    
        tiles_in_y = 1
        finished = False
        counter = 0
        while finished != True:
            current_extn = "_0000_%04d.dmd" % (counter) 
            tempfilename = basefilename+current_extn 
            my_file = fexiste(tempfilename)
            if my_file.is_file():
                counter += 1
            else :
                tiles_in_y= counter
                finished = True
        # return tiles_in_y
        self.tiles_in_y = tiles_in_y 
    def __get_LoadDataCubeMosaique(self):      
        # number of pixels per tiles in X and Y
        tilefilename = self.path + self.name +'_0000_0000.dmd'  # attach the path and the basename to the file .dmd 
        fileAttribue = os.stat(tilefilename) # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        le_bytes = np.double(fileAttribue[6]) # file size en octet
        le_bytes = le_bytes/4
        le_bytes = le_bytes -255
        le_bytes = le_bytes /len(self.wavenumbers)
        pixelNumber = int( np.sqrt(le_bytes))
        # création du datacube
        data = np.zeros((pixelNumber*(self.tiles_in_y), (pixelNumber*(self.tiles_in_x)),len(self.wavenumbers)))
        #x = 1
        #y = 1
        for  y1 in range(self.tiles_in_y): # (tiles_in_y-1)
            for x1 in range(self.tiles_in_x): # (tiles_in_x-1)
                x = x1 +1
                y = y1 +1
                current_extn = "_%04d_%04d.dmd" % (x-1,y-1) 
                tempfilename = self.path + self.name + current_extn            
                # file OPEN ----------
                with open(tempfilename, "r", encoding="Latin-1") as fid: 
                    status = fid.seek(255*4, 0)
                    tempdata = np.fromfile(fid, dtype='<f4')
                    tempdata = tempdata.reshape(-1,pixelNumber,pixelNumber)
                    tempdata= np.swapaxes(tempdata,0,2)
                    tempdata = np.swapaxes(tempdata,1,0)
                    tempdata= np.flip(tempdata,0)
                # insert this tile into the image
                data[(y-1)*pixelNumber : (y*pixelNumber),(x-1)*pixelNumber:(x*pixelNumber),:] = tempdata
        self.data = np.double(data)
    def get_DataCubeMosaique(self):
        self.__get_WavenumbersMosaique()
        self.__get_CalculTileNumber()
        self.__get_LoadDataCubeMosaique()
    def __get_LoadDataCubePart(self,tile_debx, tile_deby, tile_endx, tile_endy):      
        # number of pixels per tiles in X and Y
        tilefilename = self.path + self.name +'_0000_0000.dmd'  # attach the path and the basename to the file .dmd 
        fileAttribue = os.stat(tilefilename) # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        le_bytes = np.double(fileAttribue[6]) # file size en octet
        le_bytes = le_bytes/4
        le_bytes = le_bytes -255
        le_bytes = le_bytes /len(self.wavenumbers)
        pixelNumber = int( np.sqrt(le_bytes))
        # création du datacube
        data = np.zeros((pixelNumber*(tile_endy-tile_deby +1), (pixelNumber*(tile_endx-tile_debx+1)),len(self.wavenumbers)))
        #x = 1
        #y = 1
        for  y1 in range(tile_endy-tile_deby +1): # (tiles_in_y-1)
            for x1 in range(tile_endx-tile_debx+1): # (tiles_in_x-1)
                x = x1 +tile_debx
                y = y1 +tile_deby
                current_extn = "_%04d_%04d.dmd" % (x-1,y-1) 
                tempfilename = self.path + self.name + current_extn            
                # file OPEN ----------
                with open(tempfilename, "r", encoding="Latin-1") as fid: 
                    status = fid.seek(255*4, 0)
                    tempdata = np.fromfile(fid, dtype='<f4')
                    tempdata = tempdata.reshape(-1,pixelNumber,pixelNumber)
                    tempdata= np.swapaxes(tempdata,0,2)
                    tempdata = np.swapaxes(tempdata,1,0)
                    tempdata= np.flip(tempdata,0)
                # insert this tile into the image
                data[(y-tile_deby)*pixelNumber : ((y-tile_deby+1)*pixelNumber),(x-tile_debx)*pixelNumber:((x-tile_debx+1)*pixelNumber),:] = np.copy(tempdata)
        self.data = np.double(data)
    def get_DataCubePart(self, tile_debx, tile_deby, tile_endx, tile_endy):
        if hasattr(self, "wavenumbers")!= True :
            self.__get_WavenumbersMosaique()
            print('The wavenumbers is not created')
        else:
            pass
        if hasattr(self, "tiles_in_x")!= True:
            self.__get_CalculTileNumber()
            print('The Number of Tiles were not defined')
        else:
            pass
        if tile_debx > self.tiles_in_x:
            tile_debx = self.tiles_in_x
        else: 
            pass
        if tile_endx > self.tiles_in_x:
            tile_endx = self.tiles_in_x
        else:
            pass
        if tile_deby > self.tiles_in_y:
            tile_deby = self.tiles_in_y
        else:
            pass
        if tile_endy > self.tiles_in_y:
            tile_endy = self.tiles_in_y
        else:
            pass
        self.__get_LoadDataCubePart(tile_debx, tile_deby, tile_endx, tile_endy)
            
            
    def __get_Wavenumbers(self):
        # the wavenumbers for non mosaique data
        bspfile = self.path + self.name + '.bsp'
        # Test there is .dmd file
        try: 
            with open(bspfile, "r", encoding="Latin-1") as fid:
                status = fid.seek(0, 0)
        except FileNotFoundError:
            sys.exit('File ' + str(bspfile)+' does not exist')
        # If it exists do: 
        my_file = fexiste(bspfile)
        if my_file.is_file():
            with open(bspfile, "r", encoding="Latin-1") as fid: 
                status = fid.seek(2228, 0)
                dt = '<i4'
                nelements = 1
                startwavenumber = np.fromfile(fid, dt, nelements)
                startwavenumber.shape = (nelements, 1)
                status = fid.seek(2236, 0)
                dt = np.int32
                nelements = 1
                numberofpoints = np.fromfile(fid, dt, nelements) 
                numberofpoints.shape = (nelements, 1)
                status = fid.seek(2216, 0)
                dt = np.double
                nelements = 1
                wavenumberstep = np.fromfile(fid, dt, nelements) 
                wavenumberstep.shape = (nelements, 1)
            
            wavenumbers = np.linspace(startwavenumber[0,0],numberofpoints[0,0]+startwavenumber[0,0],np.int32(numberofpoints[0,0]))
            self.wavenumbers = wavenumbers * wavenumberstep[0,0] 
            #wavenumbers = np.linspace(0,numberofpoints[0,0]-1,np.int32(numberofpoints[0,0]))
            #self.wavenumbers = (wavenumbers * wavenumberstep[0,0]) + startwavenumber[0,0]
        else :
            print ('Error: the file doesn''t existe')
    def __get_LoadDataCubeSingle(self):        
        datfile = self.path + self.name + '.dat'
        # Test there is .dmd file
        try: 
            with open(datfile, "r", encoding="Latin-1") as fid:
                status = fid.seek(0, 0)
        except FileNotFoundError:
            sys.exit('File ' + str(datfile)+' does not exist')
        # If it exists do:         
        my_file = fexiste(datfile)
        if my_file.is_file():
            with open(datfile, "r", encoding="Latin-1") as fid: 
                status = fid.seek(255*4, 0)
                tempdata = np.fromfile(fid, dtype='<f4')    
        else :
            print ('Error: the file doesn''t existe')
        
        # number of pixels per tiles in X and Y
        fileAttribue = os.stat(datfile) # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        le_bytes = np.double(fileAttribue[6]) # file size en octet
        le_bytes = le_bytes/4
        le_bytes = le_bytes -255
        le_bytes = le_bytes /len(self.wavenumbers)
        pixelNumber = int( np.sqrt(le_bytes))
        
        #pixelNumber = 128
        tempdata = tempdata.reshape(-1,pixelNumber,pixelNumber)
        tempdata = np.swapaxes(tempdata,0,2)
        tempdata = np.swapaxes(tempdata,1,0)
        tempdata = np.flip(tempdata,0)
        self.data = tempdata
    def get_DataCubeSingle(self):
        self.__get_Wavenumbers()
        self.__get_LoadDataCubeSingle()
        
#        
#FTIRdata = mcla_AgilentFTIR(path,fichier) # Object creation 
#print(FTIRdata.name)
#
##FTIRdata.__get_Wavenumbers() # this is private so do not work this way
## but work this way FTIRdata._mcla_AgilentFTIR__get_Wavenumbers()
##Wavenumber = FTIRdata.wavenumbers
##FTIRdata.get_CalculTileNumber()
##Tilex = FTIRdata.tiles_in_x
#FTIRdata.get_DataCubeMosaique()
#datacube = FTIRdata.data
##*
#plt.figure()
#plt.imshow(datacube[:,:,945])
#plt.title('Amide I with .dmd of mosaïque')
#plt.grid()
#plt.colorbar()
##*
#wave1 = FTIRdata.wavenumbers
#
#FTIRdata1 = mcla_AgilentFTIR(path,fichier) # Object creation 
#print(FTIRdata.name)
#FTIRdata1.get_DataCubeSingle()
#datacube1 = FTIRdata1.data
#
##*
#plt.figure()
#plt.imshow(datacube1[:,:,945])
#plt.title('Amide I with .dat of mosaique')
#plt.grid()
#plt.colorbar()
##*
#wave2 = FTIRdata1.wavenumbers
#
## Seond objet
#path = 'E:/LUU_FTIR/test/LUU020429_highR/'
#fichier = '020429_hm_1.dat'   
#FTIRdataSimple = mcla_AgilentFTIR(path,fichier) # Object creation 
#print(FTIRdataSimple.name)
#FTIRdataSimple.get_DataCubeSingle()
#datacubeSimple = FTIRdataSimple.data
##*
#plt.figure()
#plt.imshow(datacubeSimple[:,:,945])
#plt.title('Amide I Simple with .dat')
#plt.grid()
##*
#
####*********** Test PMMA ***********
#path = 'E:/LUU_FTIR/LUU2_07_2020/PMMA2/'
##fichier = 'pmma2.dmt'
#fichier = 'PMMA2.dat'
#
#path = 'E:/LUU_FTIR/test/LUU71212_p6/'
#fichier = 'LUU71212_p6.dms'   
#filename = path+fichier
#pathstr,nameExt = os.path.split(filename)
#name = os.path.splitext(nameExt)[0]
##name = name.lower() # Put the file name in small letters
#dmdfile = path + name + '.dms'
#
#my_file = fexiste(dmdfile)
#if my_file.is_file():
#    with open(dmdfile, "r", encoding="Latin-1") as fid: 
#        status = fid.seek(255*4, 0)
#        tempdata1 = np.fromfile(fid, dtype='<f4')    
#else :
#    print ('Error: the file doesn''t existe')
#
#bband = tempdata1[51855595:]
### number of pixels per tiles in X and Y
##fileAttribue = os.stat(datfile) # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
##le_bytes = np.double(fileAttribue[6]) # file size en octet
##le_bytes = le_bytes/4
##le_bytes = le_bytes -255
##le_bytes = le_bytes /len(self.wavenumbers)
##pixelNumber = int( np.sqrt(le_bytes))
#
#pixelNumber = 128
#tempdata1 = tempdata1.reshape(-1,pixelNumber,pixelNumber)
#tempdata1 = np.swapaxes(tempdata1,0,2)
#tempdata1 = np.swapaxes(tempdata1,1,0)
#tempdata1 = np.flip(tempdata1,0) #128 128 1558
##*    
#plt.figure() 
#plt.imshow(tempdata1[:,:,940],cmap='jet')
#plt.grid
#plt.title('PMMA mosaique')
#plt.colorbar()
##*
#
#spectrum = tempdata1[50,50,:]
#plt.figure()
#plt.plot(spectrum)
#plt.grid()
#
##------------- Autre PMMA -----------------
#path = 'E:/LUU_FTIR/LUU2_07_2020/PMMA/'
#fichier = 'PMMA.dat'
#   
#filename = path+fichier
#pathstr,nameExt = os.path.split(filename)
#name = os.path.splitext(nameExt)[0]
##name = name.lower() # Put the file name in small letters
#datfile = path + name + '.dat'
#
#my_file = fexiste(datfile)
#if my_file.is_file():
#    with open(datfile, "r", encoding="Latin-1") as fid: 
#        status = fid.seek(255*4, 0)
#        tempdata = np.fromfile(fid, dtype='<f4')    
#else :
#    print ('Error: the file doesn''t existe')
#
### number of pixels per tiles in X and Y
##fileAttribue = os.stat(datfile) # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
##le_bytes = np.double(fileAttribue[6]) # file size en octet
##le_bytes = le_bytes/4
##le_bytes = le_bytes -255
##le_bytes = le_bytes /len(self.wavenumbers)
##pixelNumber = int( np.sqrt(le_bytes))
#
#pixelNumber = 128
#tempdata = tempdata.reshape(-1,pixelNumber,pixelNumber)
#tempdata= np.swapaxes(tempdata,0,2)
#tempdata = np.swapaxes(tempdata,1,0)
#tempdata= np.flip(tempdata,0) #128 128 1558
##*    
#plt.figure() 
#plt.imshow(tempdata[:,:,940],cmap='jet')
#plt.grid
#plt.title('PMMA simple')
#plt.colorbar()
##*
#
#
#mmosaique = np.median(tempdata1, axis=0)
#mmosaique = np.median(mmosaique, axis=0)
#
#msingle = np.median(tempdata, axis=0)
#msingle = np.median(msingle, axis=0)
#
#from scipy import ndimage # Pour median filter
#modes = 'nearest'
#tempdata1 = ndimage.median_filter(tempdata1, mode=modes, size=(3, 3,1))
#tempdata = ndimage.median_filter(tempdata, mode=modes, size=(3, 3,1))
#
#mmosaique = np.mean(tempdata1, axis=0)
#mmosaique = np.mean(mmosaique, axis=0)
#
#msingle = np.mean(tempdata, axis=0)
#msingle = np.mean(msingle, axis=0)
#
#
#plt.figure()
#plt.plot(mmosaique)
#plt.plot(msingle,'--')
#plt.grid()
#plt.legend(['.dmd','.dat'])
#
#erreur = mmosaique-msingle
#plt.figure()
#plt.plot(erreur)
#plt.grid()
#plt.legend(['error =dmd-dat'])
#
#erreur = mmosaique/msingle
#plt.figure()
#plt.plot(1/erreur)
#plt.grid()
#plt.legend(['error =dmd/dat'])
#
##*    
#plt.figure() 
#plt.imshow(tempdata1[:,:,940],cmap='jet')
#plt.grid
#plt.title('PMMA mosaique')
#plt.colorbar()
##*
#
##*    
#plt.figure() 
#plt.imshow(tempdata[:,:,940],cmap='jet')
#plt.grid
#plt.title('PMMA simple')
#plt.colorbar()
##*
#
##from statistics import median
##
##d = median(tempdata,axis=2)
##
### AUTRE Data SIGNLE 
##datfile = path + name + '.seq'
##my_file = fexiste(datfile)
##if my_file.is_file():
##    with open(datfile, "r", encoding="Latin-1") as fid: 
##        status = fid.seek(255*4, 0)
##        tempdata = np.fromfile(fid, dtype='<f4')    
##else :
##    print ('Error: the file doesn''t existe')
##
#### number of pixels per tiles in X and Y
###fileAttribue = os.stat(datfile) # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
###le_bytes = np.double(fileAttribue[6]) # file size en octet
###le_bytes = le_bytes/4
###le_bytes = le_bytes -255
###le_bytes = le_bytes /len(self.wavenumbers)
###pixelNumber = int( np.sqrt(le_bytes))
##pixelNumber = 128
##tempdata = tempdata.reshape(-1,pixelNumber,pixelNumber)
##tempdata= np.swapaxes(tempdata,0,2)
##tempdata = np.swapaxes(tempdata,1,0)
##tempdata= np.flip(tempdata,0) # 128x128x2058
###*    
##plt.figure() 
###plt.imshow(tempdata[:,:,485])
###plt.imshow(tempdata[:,:,2057])
##plt.imshow(tempdata[:,:,0])
##plt.grid()
###*
##spectrum = tempdata[50,50,:]
##plt.figure()
##plt.plot(spectrum)
##plt.grid()
#
## 33 71 85 26
## 33 71 85 27
## 33 71 84 63
## 31 71 94 24
#
## 33 71 85 27
## 33 71 82 72
##
### 33718527- 33718272 = 255
### 33718272/(128*128) = 2058
### 33718527/(128*128) = 2058.0156
##
###bband = tempdata[33718508:]
##
##
### the wavenumbers for non mosaique data
##bspfile = path + name + '.bsp'
##my_file = fexiste(bspfile)
##if my_file.is_file():
##    with open(bspfile, "r", encoding="Latin-1") as fid: 
##        status = fid.seek(2228, 0)
##        dt = '<i4'
##        nelements = 1
##        startwavenumber = np.fromfile(fid, dt, nelements)
##        startwavenumber.shape = (nelements, 1)
##        status = fid.seek(2236, 0)
##        dt = np.int32
##        nelements = 1
##        numberofpoints = np.fromfile(fid, dt, nelements) 
##        numberofpoints.shape = (nelements, 1)
##        status = fid.seek(2216, 0)
##        dt = np.double
##        nelements = 1
##        wavenumberstep = np.fromfile(fid, dt, nelements) 
##        wavenumberstep.shape = (nelements, 1)
##    
##    wavenumbers = np.linspace(startwavenumber[0,0],numberofpoints[0,0]+startwavenumber[0,0],np.int32(numberofpoints[0,0]))
##    wavenumbers = wavenumbers * wavenumberstep[0,0]     
##else :
##    print ('Error: the file doesn''t existe')
##
##bspfile = path + name +'_0000_0000.dmd'#'.dat'
##my_file = fexiste(bspfile)
##if my_file.is_file():
##    with open(bspfile, "r", encoding="Latin-1") as fid: 
##        status = fid.seek(255*4, 0)
##        dt = '<i4'
##        nelements = 16384
##        startwavenumber1 = np.fromfile(fid, dt)
##else :
##    print ('Error: the file doesn''t existe')
##
##pixelNumber = 128
##startwavenumber1 = startwavenumber1.reshape(-1,pixelNumber,pixelNumber)
##startwavenumber1 = np.swapaxes(startwavenumber1,0,2)
##startwavenumber1 = np.swapaxes(startwavenumber1,1,0)
##startwavenumber1 = np.flip(startwavenumber1,0) # 128x128x2058
###*    
##plt.figure() 
###plt.imshow(tempdata[:,:,485])
###plt.imshow(tempdata[:,:,2057])
###plt.imshow(startwavenumber1[:,:,940]) 
##plt.imshow(startwavenumber1[:,:,940]) 
##plt.grid()
##plt.colorbar()
###*
##spectrum = startwavenumber1[50,50,:]
##plt.figure()
##plt.plot(spectrum)
##plt.grid()
##
#
#
##startwavelength = np.fromfile(fid, dt, nelements) 51855360
##
##dt = np.double
##nelements = 1
##wavenumberstep = np.fromfile(fid, dt, nelements) 25526272
#
##
### Extract the wavenumbers and date from the .dmt file
##pathstr, nameExt = os.path.split(filename)
##pathname, ext = os.path.splitext(filename)
##name = os.path.splitext(nameExt)[0]
##
##name = name.lower() # mettre le nom du fichier en minuscule
##
##dmtfilename = os.path.join(pathstr,name+'.dmt') # mettre le path au fichier .dmt
##dmtfilename = pathstr+'/'+ name+'.dmt'  # ???????????????
##
###with open(dmtfilename, "r", encoding="Latin-1") as fid: #
##with open(dmtfilename, "r", encoding="Latin-1") as fid: #
##    status = fid.seek(2228, 0)
##    dt = np.int32
##    nelements = 1
##    startwavelength = np.fromfile(fid, dt, nelements)
##    startwavelength.shape = (nelements, 1)
##    startwavelength = np.double(startwavelength)
##    
##    status = fid.seek(2236, 0)
##    nelements = 1
##    numberofpoints = np.fromfile(fid, dt, nelements)
##    numberofpoints.shape = (nelements, 1)
##    numberofpoints = np.double(numberofpoints)
##    
##    
##    status = fid.seek(2216, 0)
##    dt = np.double
##    nelements = 1
##    wavenumberstep = np.fromfile(fid, dt, nelements)
##    wavenumberstep.shape = (nelements, 1)
#    
##    wavenumbers = np.linspace(1,numberofpoints+startwavelength,numberofpoints+startwavelength)
##    wavenumbers = wavenumbers * wavenumberstep
###    D = wavenumbers[0][int(startwavelength)-1]
##    wavenumbers = wavenumbers[0][int(startwavelength)-1:-1]
##    wave = np.linspace(startwavelength,numberofpoints+startwavelength,np.int32(numberofpoints))
##    wave = wave * wavenumberstep
##    wave = wave[0]
###    
###    # date
###    status = fid.seek(0, 0)
###    dt = dtype='<f4'
###    dt = np.dtype('b') 
###    dt = np.dtype('c') 
####    dt = npstring
###    nelements = 1
####    D = fid.readline()
####    text = fid.read().strip()
###    D = np.fromfile(fid, dtype=dt, sep='')
####    A= fid.readline();
####    data_array = fread(fid, [2, inf], 'int16');