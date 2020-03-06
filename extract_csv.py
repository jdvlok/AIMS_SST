#!/usr/bin/python
# Extract AIMS data from single CSV (~14 GB) file and store in ./csvfiles/.dat files (770 stations)
# Source file: ftp://ftp.aims.gov.au/pub/rtds-export/temp-logger.zip
# JD Vlok 2020-02-17

from __future__ import division
import numpy as np
import time
import zipfile
import csv
import os
from datetime import datetime

t0 = time.time()

#fncsv = 'smallset.csv'
fnzip = './temp-logger.zip'
fncsv = 'temp-logger.csv'
#extract_data(fncsv)
#onerow = extract_data(fncsv)

def write_to_file(fname_, mode_, vec1, vec2, vec3, vec4, vec5, vec6, vec7):
 f_ = open(fname_, mode_) #w: write, a: append, r+: read/write, r: read
 for v1,v2,v3,v4,v5,v6,v7 in zip(vec1, vec2, vec3, vec4, vec5, vec6, vec7):
  f_.write('"%s","%s","%s","%s","%s","%s","%s"\n'%(v1,v2,v3,v4,v5,v6,v7))
 f_.close()

c=0
archive = zipfile.ZipFile(fnzip,'r')
prev_ID, prev_lat, prev_lon, prev_name = 'NONE','NONE','NONE','NONE'
dtvec, depthvec, Tvec = [],[],[]
namevec, locvec, latvec, lonvec = [],[],[],[]
with archive.open(fncsv) as csvfile:
#with open(fncsv) as csvfile:
 datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
 for row in datareader:
  datestruct = row[0] #2012-06-25 08:50:33 +10:00
  sitename = row[1] #Bramble Cay
  loc_ID = row[2] #BRAMBLEFL1
  lat, lon = row[3],row[4] #-9.4732166666667, 143.876733333333
  depth = row[5] #3
  Temp = row[6] #26.613814

  if prev_ID == loc_ID: #still processing the same station
   dtvec.append(datestruct) 
   depthvec.append(depth)
   Tvec.append(Temp)
   namevec.append(sitename)
   locvec.append(loc_ID)
   latvec.append(lat)
   lonvec.append(lon)
  else: #beginning of new station identified
   if c>1: #don't write in first execution; first line contains column labels
    fn = './csvfiles/%s.csv'%prev_ID
    if os.path.isfile(fn): #data already written for this ID
     write_to_file(fn, 'a', dtvec, namevec, locvec, latvec, lonvec, depthvec, Tvec)
    else: #write data to new file 
     write_to_file(fn, 'w', dtvec, namevec, locvec, latvec, lonvec, depthvec, Tvec)
   dtvec, depthvec, Tvec = [datestruct],[depth],[Temp]
   namevec, locvec, latvec, lonvec = [sitename],[loc_ID],[lat],[lon]
  prev_ID, prev_lat, prev_lon, prev_name = loc_ID, lat, lon, sitename
  if (c % 1E6) == 0:
   telaps = time.time()-t0
   t_str = time.strftime('%H:%M:%S', time.gmtime(telaps))
   print '%2.2f million lines processed (%2.4f seconds --> %s)'%(c/1e6,telaps,t_str)
  c+=1

#write last data out (no new station identified at end)
fn = './csvfiles/%s.csv'%prev_ID
if os.path.isfile(fn): #data already written for this ID
 write_to_file(fn, 'a', dtvec, namevec, locvec, latvec, lonvec, depthvec, Tvec)
else: #write data to new file 
 write_to_file(fn, 'w', dtvec, namevec, locvec, latvec, lonvec, depthvec, Tvec)


print 'Total number of lines read =',c

tend = time.time()-t0
t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
print
print 'Time elapsed = %2.4f seconds = %s'%(tend,t_str)
