#!/usr/bin/python
#Python 2.7.16
# Extract AIMS data from single CSV (~14 GB) file and store in ./csvfiles/.dat files (750 stations with data)
# Source file: ftp://ftp.aims.gov.au/pub/rtds-export/temp-logger.zip
# Execution time: 420.7389 seconds = 00:07:00 (total lines: 141,012,623, valid lines: 130,432,208)
# JD Vlok 2020-02-17 jdvlok@gmail.com

from __future__ import division
import numpy as np
import time
import zipfile
import csv
import os
from datetime import datetime

t0 = time.time()

def write_to_file(fname_, mode_, vec1, vec2, vec3, vec4, vec5, vec6, vec7):
 linecount=0
 f_ = open(fname_, mode_) #w: write, a: append, r+: read/write, r: read
 for v1,v2,v3,v4,v5,v6,v7 in zip(vec1, vec2, vec3, vec4, vec5, vec6, vec7):
  f_.write('"%s","%s","%s","%s","%s","%s","%s"\n'%(v1,v2,v3,v4,v5,v6,v7))
  linecount+=1
 f_.close()
 return linecount

dirname = './csvfiles'
if not os.path.exists(dirname):
 os.mkdir(dirname)
 print 'New directory %s created'%dirname

#fncsv = 'smallset.csv'
fnzip = './temp-logger.zip'
fncsv = 'temp-logger.csv'
#extract_data(fncsv)
#onerow = extract_data(fncsv)

totallines, validlines, filecount = 0,0,0
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

  if Temp != '': #exclude lines in .csv file that does not contain a temperature value
   if prev_ID == loc_ID: #still processing the same station
    dtvec.append(datestruct) 
    depthvec.append(depth)
    Tvec.append(Temp)
    namevec.append(sitename)
    locvec.append(loc_ID)
    latvec.append(lat)
    lonvec.append(lon)
   else: #beginning of new station identified, although this station may have been seen previously
    if totallines>1: #don't write in first execution; first line contains column labels
     fn = './csvfiles/%s.csv'%prev_ID
     if os.path.isfile(fn): #data already written for this ID
      lc=write_to_file(fn, 'a', dtvec, namevec, locvec, latvec, lonvec, depthvec, Tvec)
     else: #write data to new file (station not seen previously)
      lc=write_to_file(fn, 'w', dtvec, namevec, locvec, latvec, lonvec, depthvec, Tvec)
      filecount+=1
      print '%03d new file: %s'%(filecount,fn)
     validlines+=lc
    dtvec, depthvec, Tvec = [datestruct],[depth],[Temp]
    namevec, locvec, latvec, lonvec = [sitename],[loc_ID],[lat],[lon]
   prev_ID, prev_lat, prev_lon, prev_name = loc_ID, lat, lon, sitename
   if (totallines % 1E6) == 0: #write progress to command line every 1 million lines
    telaps = time.time()-t0
    t_str = time.strftime('%H:%M:%S', time.gmtime(telaps))
    print '%2.2f million lines processed (%2.4f seconds --> %s)'%(totallines/1e6,telaps,t_str)
  totallines+=1

#write last data out (no new station identified at end)
fn = './csvfiles/%s.csv'%prev_ID
if os.path.isfile(fn): #data already written for this ID
 lc=write_to_file(fn, 'a', dtvec, namevec, locvec, latvec, lonvec, depthvec, Tvec)
else: #write data to new file 
 lc=write_to_file(fn, 'w', dtvec, namevec, locvec, latvec, lonvec, depthvec, Tvec)
validlines+=lc

print 'Total number of lines read =',totallines
print 'Lines containing data =',validlines

tend = time.time()-t0
t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
print
print 'Execution time: %2.4f seconds = %s'%(tend,t_str)
