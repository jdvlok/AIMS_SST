#!/usr/bin/python
#Python 2.7.16
# Repackage ./csvfiles/ as object data files in ./datfiles/ according to station definition in marine_station_def.py
# Data written to object files: ID, name, lat, lon, datetime vector, temperature vector, depth vector, record length N,
# number of samples missing M (should be zero, as lines with no data excluded by extract_csv.py)
# Meta file basic_meta.npz also updated, by adding N, M and set of unique depths
# Execution time: 905.1032 seconds = 00:15:05
# JD Vlok 2020-02-11 jdvlok@gmail.com
# Last update: 2020-03-06

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

def const_check(const_test, testval, refval, IDval):
 const_test = const_test and (testval==refval)
 if not const_test:
  print 'Check failed for %s: %s [TEST] != %s [REF]'%(IDval, testval, refval)
 return const_test

dirname = './datfiles'
if not os.path.exists(dirname):
 os.mkdir(dirname)
 print 'New directory %s created'%dirname

#extract meta data file:
npz_file = './basic_meta.npz'
npzf = np.load(npz_file)
mXvec = npzf['v1']

IDlist,nodataIDvec,fileswritten,files_notwritten = [],[],0,0
totallines,totalvalid,totalmissing=0,0,0
c,Ld=0,len(mXvec)
changevec = []
for mX in mXvec:
 c+=1
 ID0 = mX.ID
 IDlist.append(ID0)
 name0 = mX.name
 lat0, lon0 = mX.lat, mX.lon
 fncsv = './csvfiles/%s.csv'%ID0
 fndat = './datfiles/%s.dat'%ID0
 IDconst, nameconst, latconst, lonconst = True, True, True, True
 sX = station(ID0) #create new station object defined in marine_station_def.py
 sX.name = name0
 sX.lat, sX.lon = lat0, lon0
 dtvec, depthvec, Tvec = [],[],[] #datetime, nominal depth, water temperature
 N,M = 0,0 #valid, missing number of temperature samples
 with open(fncsv) as csvfile:
  datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
  for row in datareader:
   datestruct = row[0] #2012-06-25 08:50:33 +10:00
   sitename = row[1] #Bramble Cay
   loc_ID = row[2] #BRAMBLEFL1
   lat, lon = row[3],row[4] #-9.4732166666667, 143.876733333333
   depth = row[5] #3
   Temp = row[6] #26.613814

   IDconst = const_check(IDconst, loc_ID, ID0, ID0)
   nameconst = const_check(nameconst, sitename, name0, ID0)
   latconst = const_check(latconst, lat, lat0, ID0)
   lonconst = const_check(lonconst, lon, lon0, ID0)
   totallines+=1
   if Temp != '': #only store data if temperature measurement is present
    dtvec.append(datestruct)
    depthvec.append(depth)
    Tvec.append(Temp)
    N+=1
    totalvalid+=1
   elif Temp == '':
    M+=1
    totalmissing+=1
   else:
    print 'ID: %s non-conforming temperature value: %s'%(ID0, Temp)
 sX.dtvec = dtvec
 sX.Tvec = Tvec
 sX.depthvec = depthvec
 sX.N, sX.M = N,M

 mX.unique_depths = np.unique(depthvec)
 mX.N, mX.M = N,M

 if N>0:
  fdat = open(fndat,'wb') #create/overwrite file
  pickle.dump(sX,fdat)
  fdat.close()
  fileswritten+=1
 else:
  print '%s does not contain any data'%ID0
  nodataIDvec.append(ID0)
  files_notwritten+=1

 telaps = time.time()-t0
 print '%d/%d. Read: %s [%2.2f s]'%(c,Ld,ID0,telaps)

 if not (IDconst and nameconst and latconst and lonconst):
  print 'Changes in %s:'%ID0
  print '  IDconst:', IDconst
  print 'nameconst:', nameconst
  print ' latconst:', latconst
  print ' lonconst:', lonconst
  changetxt = 'Const: %s: ID [%s], Name [%s], Lat [%s], Lon [%s]'%(ID0,IDconst,nameconst,latconst,lonconst)
  changevec.append(changetxt)

#write more complete basic meta data to new file to prevent being overwritten by basic_meta_from_csv_files.py:
npz_file = './basic_meta2.npz' 
np.savez_compressed(npz_file,v1=mXvec,v2=IDlist)
print 'Saved %d stations metadata to %s'%(c, npz_file)
print 'len(IDlist) = %d'%(len(IDlist))

print 'Total lines =', totallines
print '-Valid:',totalvalid
print '-  NaN:',totalmissing
print
print 'Object files written:', fileswritten
print 'Object files not written (stations with no data):', files_notwritten

if len(changevec)==0:
 print 'All parameters (ID, name, lat, lon) constant throughout each file'
else:
 print 'Parameter changes:'
 for chx in changevec:
  print chx
   
tend = time.time()-t0
t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
print
print 'Time elapsed = %2.4f seconds = %s'%(tend,t_str)
