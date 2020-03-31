#!/usr/bin/python
#JD Vlok 2017-05-12
# 1. 2017-03-27: flexmap_agi2017.py: plot stations with Tmax colors in region used for AI paper agi2017
# 2. 2017-05-12: rect_map.py: plot stations around Deniliquin for paper attempt 2 
# 3. 2017-10-23: rect_map2.py: plot stations per state
# 4. 2018-11-21: rect_map4.py: plot all stations on map
# 5. 2020-02-05: VICmap.py: plot map of Victoria
# 6. 2020-02-11: aims_map.py: map of Australia with AIMS stations
# 7. 2020-02-12: map_dat.py: plot map of Australia with AIMS stations and data
# 8. 2020-02-14: plot_one.py: plot SST timeseries of one station
# 9. 2020-02-19: plot_one_v2.py: plot SST timeseries of one station using preprocessed object files
# 10. 2020-02-20: plot_one_v3.py: process time vector
# 11. 2020-02-25: plot_one_v4.py: read updated .dat files written by process_obj3.py
# 12. 2020-03-27: list_stations_0.py: extract metadata from 1 file in ./datfiles/
# 13. 2020-03-27: list_stations.py: extract metadata from all files in ./datfiles/

from __future__ import division
import numpy as np
import time
#from geopy.geocoders import Nominatim #to obtain GPS coordinates of cities
from marine_station_def import station_meta, station_meta_list
import pickle
from os import listdir
from calendar import monthrange
import pandas as pd
from datetime import datetime
from dateutil import parser
import sys

t0 = time.time()

def extract_meta(sX_):
 mX_ = station_meta_list(sX_.ID)
 mX_.name = sX_.name
 mX_.lat, mX_.lon = sX_.lat, sX_.lon

 #Combine date, temperature and depth data into dictionary:
 dX = {'date': sX_.uniform_dtvec, 'Temp': sX_.Tvec, 'depth': sX_.depthvec}
 #Change dictionary into pandas dataframe:
 df = pd.DataFrame(dX, columns=['date','Temp','depth'], dtype=float)
 #df_sorted = df.sort_values(by=['date','depth'])
 df_sorted = df.sort_values(by=['depth','date'])
 df = df_sorted.set_index('date') #set dataframe index using date column
 df['datetime'] = df.index #add a column to dataframe, named "datetime" and set this to the index

 #split dataframe by depth values:
 by_depth = df.groupby('depth')
 for depth_, subframe in by_depth:
  if depth_ == '':
#   print 'Unknown depth'
   depthval = '-'
  else:
#   print 'Depth =', depth_, 'm'
   depthval = depth_

  starttime = np.min(subframe.datetime)
  endtime = np.max(subframe.datetime)
#  print 'Start time:', starttime
#  print '  End time:', endtime

  mX_.depthvec.append(depthval)
  mX_.startvec.append(starttime)
  mX_.endvec.append(endtime)

  #remove duplicates from subframe:
  subframe2 = subframe.groupby('datetime').mean()
  subframe2['datetime'] = subframe2.index

  #calculate sample spacing:
#  subframe3 = subframe2.groupby(pd.Grouper(freq='1D'))
  N = len(subframe2)
  if N>1:
#   mindif = subframe2.datetime.diff().min()
#   Ts_min = np.int(mindif.total_seconds()) #minimum sample spacing [s]
#   Nmax = len(pd.date_range(start=starttime, end=endtime, freq='%ds'%Ts_min)) #maximum length

   mostfreqdif = subframe2.datetime.diff().value_counts().nlargest(1)
   Ts_most = np.int(mostfreqdif.index.total_seconds()[0]) #most occurring sample spacing [s]
   Nmax = len(pd.date_range(start=starttime, end=endtime, freq='%ds'%Ts_most)) #maximum length

   complete = 100*N/Nmax
  else:
   Ts_most = '-' #Ts_min = '-'
   complete = '-'
   Nmax=0

#  try:
#   mindif = subframe2.datetime.diff().min()
#   Ts_min = np.int(mindif.total_seconds()) #minimum sample spacing [s]
#   Nmax = len(pd.date_range(start=starttime, end=endtime, freq='%ds'%Ts_min)) #maximum length
#   complete = 100*N/Nmax
#  except:
#   print 'Could not calculate minimum Ts'
#   Ts_min = '-'
#   complete = '-'

  mX_.Tsvec.append(Ts_most) #(Ts_min)
  mX_.Nvec.append(N)
  mX_.completevec.append(complete)
  print 'Depth:',depthval,
  print 'Dates: ', starttime, 'to', endtime
  print 'Completion:',N,'out of',Nmax,'=',complete,'percent'

 return mX_

c=0
mXvec=[]
dirx = './datfiles/'
datfiles = listdir(dirx)
for fn in datfiles:
 fdat = open(dirx+fn,'rb') #create/overwrite file
 sX = pickle.load(fdat)
 fdat.close()

 tend = time.time()-t0
 t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
 c+=1
 print '%03d. %s: %s %s [t = %s]'%(c, fn, sX.ID, sX.name, t_str)
 mX = extract_meta(sX)
 print
 mXvec.append(mX)
 
# print 'Lat:', mX.lat
# print 'Lon:', mX.lon
# print 'N =', N
# print 'Ts_min =', Ts_min, 'seconds'
# print 'Complete = %f%%'%complete
# print

npz_file = './table_meta.npz'
np.savez_compressed(npz_file,v1=mXvec)
print 'Saved %d stations metadata to %s'%(c, npz_file)

tend = time.time()-t0
t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
print 'Time elapsed = %2.4f seconds = %s'%(tend,t_str)
