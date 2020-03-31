#2020-02-07: marinestations.py
#AIMS water temperature data

# year range (self.yearseq), and annual averages (self.Tyear)
import numpy as np
import calendar

class station_meta:
 def __init__(self,stationID):
  self.ID = stationID #location acronym
  self.name = None
  self.lat = None
  self.lon = None
  self.unique_depths = [] #vector containing nominal depth
  self.N = None #number of valid (non-NaN) temperature measurements
  self.M = None #number of missing (NaN) temperature measurements

 
class station:
 def __init__(self,stationID):
#components extracted from individual .csv files (csv2obj3.py):
  self.ID = stationID #location acronym
  self.name = None
  self.lat = None
  self.lon = None
  self.dtvec = [] #datetime vector
  self.Tvec = [] #temperature
  self.depthvec = [] #vector containing nominal depth
  self.N = None #number of valid (non-NaN) temperature measurements
  self.M = None #number of missing (NaN) temperature measurements

  self.timezonevec = None #set of time zones present #previously: offsetvec
  self.issues_text = None #text describing potential datetime vector problems
  self.timezone = None #dominant timezone: largest value in timezonevec
  self.uniform_dtvec = [] #dtvec (datetime objects) with timezone removed (time corrected to dominant timezone)


class station_xdata: #compute_daily_data.py to store all objects in ./daily_dat/*.dat
 def __init__(self,stationID):
  self.ID = stationID #location acronym
  self.name = None
  self.lat = None
  self.lon = None
  self.timezone = None #dominant timezone: largest value in timezonevec

  self.depth_array = None
  self.sample_period_array = None #sample spacing between multiple daily measurements in seconds
  self.sample_target_array = None #maximum number of measurements per day according to sample spacing
  self.Tdatframe_array = None #pandas dataframe containing daily measurements: ['Tmax','Tmin','Tmean','Nsamples','Complete[%]','Start','End']


class station_meta_list:
 def __init__(self,stationID):
  self.ID = stationID #location acronym
  self.name = None
  self.lat = None
  self.lon = None
  self.depthvec = [] #vector containing nominal depth
  self.startvec = [] #vector containing datetime of start of period
  self.endvec = [] #vector containing datetime of end of period
  self.Tsvec = [] #sample spacing vector
  self.completevec = [] #percentage complete vector
  self.Nvec = [] #number of samples

