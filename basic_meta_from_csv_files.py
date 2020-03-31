#!/usr/bin/python
#Python 2.7.16
# Read first line of each file in ./csvfiles/ (created by extract_csv.py) and write initial meta data to ./basic_meta.npz
# according to station_meta class definition in marine_station_def.py
# Execution time: <1 s
# JD Vlok 2020-03-06 jdvlok@gmail.com

from __future__ import division
import numpy as np
import time
import os
from marine_station_def import station_meta

t0 = time.time()

def fix_location(ID_, sitename_):
 if sitename_ == 'Scott Reef': #11 sites without location identified as 'Scott Reef'
  lat_, lon_ = '-13.999458', '121.833205' #Google maps location values for Scott Reef
 if ('Cape Ferguson' in ID_) or ('aims' in ID_): #AIMS Wharf assumed to be at Cape Ferguson
  lat_, lon_ = '-19.282644', '147.066881' #Google maps location values for Cape Ferguson
 if 'South Trees Inlet' in sitename_:
  lat_, lon_ = '-23.885657', '151.298300' #Google maps location values for South Trees Inlet
 if (sitename_ == 'Masig Island'):
  lat_, lon_ = '-9.751159', '143.408199' #Google maps location values for Masig Island
 if ('Hardy Reef' in ID_):
  lat_, lon_ = '-19.755285', '149.234313' #Google maps location values for Hardy Reef
 return (lat_,lon_)

issues = []
datfiles = os.listdir('./csvfiles/')
datfiles.sort()
Ld = len(datfiles)
mXvec = []
#make sure no files are open, creating a temporary file ~
c = 0
IDlist = []
for fileX in datfiles:
 ID = fileX[0:-4]
 IDlist.append(ID)
 mX = station_meta(ID)
 fncsv = './csvfiles/%s'%fileX
 f = open(fncsv,'r')
 line0 = f.readline() #read only first line of .csv file
 f.close()
# dtval,sitename,IDx,latx,lonx,depthx,Tx = line0.split(',')
 _,dtval,_,sitename,_,IDx,_,latx,_,lonx,_,depthx,_,Tx,_ = line0.split('"')
 if ID != IDx:
  isstxt = 'IDs mismatch: File %s not the same as content %s'%(ID,IDx)
  print isstxt
  issues.append(isstxt)
 if (latx == '') or (lonx == ''):
  mX.lat, mX.lon = fix_location(IDx,sitename)
  print 'Changed [lat,lon] of %s from [%s,%s] to [%s,%s]'%(ID,latx,lonx,mX.lat,mX.lon)
 else:
  mX.lat, mX.lon = latx, lonx

 mX.name = sitename
 mXvec.append(mX)

 c+=1
# telaps = time.time()-t0
# t_str = time.strftime('%H:%M:%S', time.gmtime(telaps))
 print '%d/%d. Read: %s'%(c,Ld,fileX)

npz_file = './basic_meta.npz'
np.savez_compressed(npz_file,v1=mXvec,v2=IDlist)
print 'Saved %d stations metadata to %s'%(c, npz_file)

if len(issues)==0:
 print 'All IDs match'
else:
 for issX in issues:
  print issX

tend = time.time()-t0
t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
print
print 'Time elapsed = %2.4f seconds = %s'%(tend,t_str)
