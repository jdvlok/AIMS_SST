#!/usr/bin/python
#Python 2.7.16
# Process timestamps by removing timezone information. Change all timestamps to local time, and save original (dominant
# or max) time offset as the timezone assumed. All timestamps in the date vector are thus unified to the same time zone.
# Execution time: 01:17
# JD Vlok 2020-02-11 jdvlok@gmail.com
# Last update: 2020-03-07

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
from datetime import datetime, timedelta
#import pylab as pl

t0 = time.time()
#pl.close('all')

def timecheck(datevec_):
 timezonevec__ = []
 UTC_detected = False
 no_issues, issues_text_ = True,''
 for dx in datevec_:
#  print dx
  dayx,timex,offset = dx.split()
  Y,M,D = dayx.split('-')
  y,m,d = np.int(Y),np.int(M),np.int(D)

  Ht,Mt,St = timex.split(':')
  ht,mt,st = np.int(Ht),np.int(Mt),np.int(St)

  if offset == 'AUSTRALIA/BRISBANE':
   oh,om = 10,0 #offset hours, offset minutes
  elif offset == 'UTC':
   oh,om = 0,0
   UTC_detected = True
  else:
   oH,oM = offset.split(':')
   oh,om = np.int(oH),np.int(oM)
  fl_offset = oh+(om/60)
  if fl_offset not in timezonevec__:
   timezonevec__.append(fl_offset)
# no_issues, issues_text_ = True,''
 if len(timezonevec__) > 1:
  issues_text_ = 'Multiple timezones/offsets present in time series'
  no_issues = False
 if UTC_detected:
  if issues_text_ != '':
   issues_text_ += ', '
  issues_text_ += 'UTC as timezone present'
  no_issues = False
 if no_issues:
  issues_text_ = 'No problems with time series'
 return (timezonevec__, issues_text_)

def extract_tz_offset(offset_): #extract floating time offset from string time zone
 if offset_ == 'AUSTRALIA/BRISBANE':
  oh,om = 10,0 #offset hours, offset minutes
 elif offset_ == 'UTC':
  oh,om = 0,0
 else:
  oH,oM = offset_.split(':')
  oh,om = np.int(oH),np.int(oM)
 fl_offset_ = oh+(om/60)
 return fl_offset_

def processT(sX_):
 datevec = sX_.dtvec #'2010-12-10 00:25:46 +10:00'
 timezonevec_, issues_text = timecheck(datevec)
 sX_.timezonevec = timezonevec_ #[10]
 sX_.issues_text = issues_text #'No problems with time series'

 d_timezone = np.max(timezonevec_) #10, dominant timezone (time offset) - using max here, could use most occurring
 sX_.timezone = d_timezone #

 uniform_dtvec = [] #datetime objects in local time (dominant time zone of sX.dtvec)
#remove timezone from date vector:
 for dx in datevec: #'2010-12-10 00:25:46 +10:00'
  dayx,timex,offset = dx.split() #['2010-12-10', '00:25:46', '+10:00']
  fl_offset = extract_tz_offset(offset) #10
#  print '%s: %f: %f'%(sX_.ID,fl_offset,d_timezone)
  datetimestr = '%s %s'%(dayx,timex) #'2010-12-10 00:25:46'
  dtobj = datetime.strptime(datetimestr,'%Y-%m-%d %H:%M:%S') #datetime.datetime(2010, 12, 10, 0, 25, 46)
  time_diff = d_timezone - fl_offset #0
  dtobj2 = dtobj + timedelta(hours = time_diff) #datetime.datetime(2010, 12, 10, 0, 25, 46): datetime in local time (dominant time zone)
  uniform_dtvec.append(dtobj2)
 sX_.uniform_dtvec = uniform_dtvec

 return sX_

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

#emptyvec:
#['CARSL1', 'CREALFL1', 'DOUBLEFL1', 'FREDERICKFL2', 'Fantasea Ferry (Airlie Beach - Hardy Reef)', 'MIRSL2', 'ORPHFL2',\
# 'PCIMP-GC4-1', 'PCIMP-QAL1', 'PCIMP-QAL2', 'PCIMP-QAL3', 'POMPEY1FL1', 'RV Cape Ferguson', 'SCOTTSS2-3', 'SMLLAGSL1',\
# 'TERNFL1', 'YORKSL1', 'YORKSL3', 'YORKSL6', 'aims_wharf']

#extract meta data file:
npz_file = './basic_meta2.npz'
npzf = np.load(npz_file)
mXvec,IDvec = npzf['v1'],npzf['v2']
Lm = len(IDvec)
cc=0
emptyvec,emptyfiles = [],0
for ID0 in IDvec:
 cc+=1
 fn = './datfiles/%s.dat'%ID0
 fdat = open(fn,'rb')
 sX = pickle.load(fdat)
 fdat.close()
 N = sX.N
 if N > 0:
  sX = processT(sX)
  if (sX.lat == '') or (sX.lon == ''):
   sX = fix_location(sX)
  fdat = open(fn,'wb') #create or overwrite file
  pickle.dump(sX,fdat)
  fdat.close()
 elif N==0:
  emptyfiles+=1

 tend = time.time()-t0
 t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
 print '%d/%d. ID: %s [N = %d] [t=%s]'%(cc,Lm,ID0,N,t_str)
 if N==0:
  print '%s contains no data'%ID0
  print
  emptyvec.append(ID0)
# IDlist.append(ID0)
# counter_list.append(sX.N+sX.M)
# nan_counter_list.append(sX.M)

print 'Empty files counted:', emptyfiles

tend = time.time()-t0
t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
print
print 'Time elapsed = %2.4f seconds = %s'%(tend,t_str)
