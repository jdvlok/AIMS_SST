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
# 14. 2020-03-30: table_stations.py: create LaTeX table code from './table_meta.npz' created by list_stations.py

from __future__ import division
import numpy as np
import time
#from geopy.geocoders import Nominatim #to obtain GPS coordinates of cities
from marine_station_def import station_meta_list #station_meta
import pickle
from os import listdir, path
from calendar import monthrange
import pandas as pd
from datetime import datetime
from dateutil import parser
import sys


def write_table_header(txtf_):
 txtf_.write('\\begin{table}[!htp]\n')
 txtf_.write('\\vspace{-6ex}\n')
 txtf_.write('\\hspace{-2ex}\n')
 txtf_.write('\scriptsize\n') #\footnotesize, \scriptsize, \tiny
 txtf_.write('\centering\n')
 txtf_.write('\\begin{tabular}{|p{5mm}||p{8.5cm}|R{1.25cm}|R{1.25cm}||R{8mm}|C{1.6cm}|C{1.6cm}|R{1.25cm}|R{1cm}|R{1cm}|}\n')
# txtf_.write('\\begin{tabular}{|l|l||c|c|c||c|c|c|c|c|}\n')
 txtf_.write('\hline\n')
 lath = '{\\bf Lat} ($^\circ$S)'
 lonh = '{\\bf Lon} ($^\circ$E)'
 strh = '{\\bf Start date}'
 endh = '{\\bf End date}'
 Nh = '\\multicolumn{1}{c}{$N$}'
 eol = '\\multicolumn{1}{|c|}{\\%} \\\\'
 hl = '\\multicolumn{1}{|c||}{\#}'
 txtf_.write('%s & {\\bf Station Identifier} & %s & %s & $d$ (m) & %s & %s & $T_s$ (min) & %s & %s \n'%(hl,lath,lonh,strh,endh,Nh,eol))
 txtf_.write('\hline\n')
 txtf_.write('\hline\n')

def write_table_footer(txtf_):
 txtf_.write('\hline\n')
 txtf_.write('\end{tabular}\n')
# txtf_.write('\caption{Threshold escape and SNR values associated with AWGN noise power.}\n')
# txtf_.write('\label{tab:gevspn}\n')
 txtf_.write('\end{table}\n')
 txtf_.write('\n')
# txtf_.write('\\newpage\n')

def int_or_float(nr):
 if nr == np.int(nr):
  txt = '%d'%nr
 else:
  txt = '%2.2f'%nr
 return txt

def calc_line(mX__, c__, d_): #d_: depth counter
 if d_ == 0: #first depth item per record
  cstr = '%03d'%c__
  ID,name = mX__.ID,mX__.name
  ID = ID.replace('_','\_')
  lat_fl = -np.float(mX__.lat)
  lon_fl = np.float(mX__.lon)
  if np.mod(c__,2)==1: #uneven numbers
   strX = '\celc %s & \celc %s: %s & \celc %2.4f & \celc %2.4f'%(cstr, ID, name, lat_fl, lon_fl)
  else:
   strX = '%s & %s: %s & %2.4f & %2.4f'%(cstr, ID, name, lat_fl, lon_fl)
 else:
  if np.mod(c__,2)==1: #uneven numbers
   strX = '\celc & \celc & \celc  & \celc '
  else:
   strX = ' &  &  & '

 depth = mX__.depthvec[d_]
 start, end = mX__.startvec[d_], mX__.endvec[d_]
 Ts, complete, N = mX__.Tsvec[d_], mX__.completevec[d_], mX__.Nvec[d_]
 startX = '%d-%02d-%02d'%(start.year, start.month, start.day)
 endX = '%d-%02d-%02d'%(end.year, end.month, end.day)
 if complete == '-':
  compX = '-'
 else:
  compX = '%2.1f'%complete
 #change sampling period to minutes:
 if Ts == '-':
  TsX = '-'
 else:
  if Ts >= 86400: #longer than a day
   TsX = '%s $d$'%int_or_float(Ts/86400)
  elif 60 <= Ts < 86400: #between 1 min and 1 day
   TsX = '%s'%int_or_float(Ts/60)
  else: 
   TsX = '%d $s$'%Ts

 if np.mod(c__,2)==1: #uneven numbers
  ptxt = '%s & \celc %s & \celc %s & \celc %s & \celc %s & \celc %d & \celc %s \\\\ \n'%(strX, depth, startX, endX, TsX, N, compX)
 else:
  ptxt = '%s & %s & %s & %s & %s & %d & %s \\\\ \n'%(strX, depth, startX, endX, TsX, N, compX)

# txtf_.write(ptxt)
# print ptxt
# lines_+=1
 return ptxt

def calc_block(mX_, c_):
 firstline = calc_line(mX_, c_, 0)
 block_ = [firstline]
 for d in np.arange(1,len(mX_.depthvec),1):
  line = calc_line(mX_, c_, d) #dc: depth counter
  block_.append(line)
 return block_

def write_block(txtf_, block_):
 for line_ in block_:
  txtf_.write(line_)

# strX = '\celc %s & \celc %s: %s & \celc %2.4f & \celc %2.4f'%(cstr, ID, name, lat_fl, lon_fl)

t0 = time.time()
npz_file = './table_meta.npz'
if path.isfile(npz_file):
 print npz_file,'exists'
 npzf = np.load(npz_file)
 mXvec=npzf['v1']

txtf = open('./stations_table.tex','w') #w: write, a: append, r+: read/write, r: read
#txtf.write('Test %d\n'%(x))

txtf.write('\\begin{landscape}\n')
write_table_header(txtf) #start new table

mXvec_sorted = sorted(mXvec, key=lambda x: x.ID, reverse=False)

c,lines=0,0
for mX in mXvec_sorted:
 c+=1
 block = calc_block(mX, c) #one block (details of one station) to be written to .tex file
 if lines + len(block) > 40: #if current block will not fit on current page
  write_table_footer(txtf) #close off table
  txtf.write('\\newpage\n')
  write_table_header(txtf) #start new table
  lines=0

 write_block(txtf, block)
 lines+=len(block)

write_table_footer(txtf)
txtf.write('%% %s\n'%__file__) #write name of python script to file
txtf.write('\\end{landscape}\n')
txtf.close()

#  self.startvec = [] #vector containing datetime of start of period
#  self.endvec = [] #vector containing datetime of end of period
#  self.Tsvec = [] #sample spacing vector
#  self.completevec = [] #percentage complete vector
#  self.Nvec = [] #number of samples


tend = time.time()-t0
t_str = time.strftime('%H:%M:%S', time.gmtime(tend))
print 'Time elapsed = %2.4f seconds = %s'%(tend,t_str)
