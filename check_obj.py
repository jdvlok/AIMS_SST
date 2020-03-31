#!/usr/bin/python
# JD Vlok 2020-02-11
# 1. 2020-02-11: read_waterT.py: Read data files created by store_waterT_v2.py
# 2. 2020-02-11: meta_from_dat.py: Extract meta data from datafiles created by store_waterT_v2.py
# 3. 2020-02-20: compare_meta.py: Extract simple statistics from datafiles created by extract_csv2.py
# 4. 2020-02-19: csv2obj.py: Repackage ./csvfiles/ as object data files
# 5. 2020-02-19: check_obj.py: Check N and M values in object files created by csv2obj.py with build_meta.py output
# 6. 2020-02-20: check_obj2.py: Use metadata in csvs_meta.npz instead of loading each .dat file to extract N and M

from __future__ import division
import numpy as np
#import os.path
from calendar import monthrange
import time
import zipfile
import csv
import os
import sys
import pickle
from marine_station_def import station, station_meta
from datetime import datetime
#import pylab as pl

t0 = time.time()
#pl.close('all')

def fix_location(sX):
 if sX.name == 'Scott Reef': #11 sites without location identified as 'Scott Reef'
  lat, lon = '-13.999458', '121.833205' #Google maps location values for Scott Reef
 if ('Cape Ferguson' in sX.ID) or ('aims' in sX.ID): #AIMS Wharf assumed to be at Cape Ferguson
  lat, lon = '-19.282644', '147.066881' #Google maps location values for Cape Ferguson
 if 'South Trees Inlet' in sX.name:
  lat, lon = '-23.885657', '151.298300' #Google maps location values for South Trees Inlet
 if (sX.name == 'Masig Island'):
  lat, lon = '-9.751159', '143.408199' #Google maps location values for Masig Island
 if ('Hardy Reef' in sX.ID):
  lat, lon = '-19.755285', '149.234313' #Google maps location values for Hardy Reef
 sX.lat, sX.lon = lat, lon
 return sX

#extract meta data file:
npz_file = './basic_meta.npz'
npzf = np.load(npz_file)
mXvec = npzf['v1']
IDvec_complete,counter_list,nan_counter_list = [],[],[]
IDvec_valid,IDvec_empty=[],[]
emptystations, validstations = 0,0
cc=0
Lm = len(mXvec)
for mX in mXvec:
 cc+=1
 ID0 = mX.ID
 N,M = mX.N, mX.M
 IDvec_complete.append(ID0)
 counter_list.append(N+M)
 nan_counter_list.append(M)
 print '%d/%d. ID: %s'%(cc,Lm,ID0)
 if N==0:
  emptystations+=1
  IDvec_empty.append(ID0)
 else:
  validstations+=1
  IDvec_valid.append(ID0)

 lat, lon = mX.lat, mX.lon
 if (lat == '') or (lon == ''):
  mX = fix_location(mX)
  print 'Location information for %s changed from [lat: %s, lon: %s] to [lat: %s, lon: %s]'%(ID0,lat,lon,mX.lat,mX.lon)

print
print 'Number of stations:'
print ' * According to %s: %d'%(npz_file, len(IDvec_complete))
print '   -> Valid:', len(IDvec_valid)
print '   -> Empty:', len(IDvec_empty)
print
print 'Current files:'
print ' * ./csvfiles/:',len(os.listdir('./csvfiles/'))
print ' * ./datfiles/:',len(os.listdir('./datfiles/'))

np.savez_compressed(npz_file,v1=mXvec,v2=IDvec_complete,v3=IDvec_valid,v4=IDvec_empty)
print 'Saved %d stations metadata to %s'%(len(mXvec), npz_file)

tend = time.time()-t0
t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
print
print 'Time elapsed = %2.4f seconds = %s'%(tend,t_str)
