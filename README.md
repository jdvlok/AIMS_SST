# AIMS_SST
Extract and analyse AIMS sea surface temperature data

Source file: ftp://ftp.aims.gov.au/pub/rtds-export/temp-logger.zip


1. extract_csv.py: extract 770 CSV files from single temp-logger.csv --> saved in ./csvfiles/
Total number of lines read = 141012623 (incl 1 header line)
Lines containing data = 130432208
Execution time: 420.7389 seconds = 00:07:00

2. basic_meta_from_csv_files.py: read first line of each csv file in ./csvfiles/ and store result in ./basic_meta.npz
according to station_meta class definition in marine_station_def.py containing ID,name,lat,lon for each station.
Also fix location (lat and lon) for station records not having this information.
Execution time: 0 seconds

3. csv2obj.py: repackage ./csvfiles/ as object data files in ./datfiles/ according to station definition in
marine_station_def.py
Data written to object files: ID, name, lat, lon, datetime vector, temperature vector, depth vector, record length N,
number of samples missing M (should be zero, as lines with no data excluded by extract_csv.py)
Meta file basic_meta2.npz created containing data in basic_meta.npz and N, M and set of unique depths
Execution time: 905.1032 seconds = 00:15:05

Total lines = 130432208
       Valid: 130432208
         NaN: 0
Object files written: 750
Object files not written (stations with no data): 0
All parameters (ID, name, lat, lon) constant throughout each file
Saved 750 stations metadata to ./basic_meta.npz

Parameter changes:
Const: MASIGFL1: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL1-TIDEGUAGE1: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL1-TIDEGUAGE2: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL1-TIDEGUAGE3: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL2-TIDEGUAGE1: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL2-TIDEGUAGE2: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL3-TIDEGUAGE1: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL4-TIDEGUAGE1: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL4-TIDEGUAGE2: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSL4-TIDEGUAGE3: ID [True], Name [True], Lat [False], Lon [False]
Const: SCOTTSS3: ID [True], Name [True], Lat [False], Lon [False]

Time elapsed = 960.9902 seconds = 00:16:00

4. process_obj.py: make series uniform by removing timezone information after changing time to local
Time elapsed = 4642.9801 seconds = 01:17:22

5. compute_daily_data.py

6. list_stations.py
Run through all stations in ./datfiles, extract and save metadata (station_meta_list as in marine_station_def.py) to
table_meta.npz, which will be used to generate LaTeX table containing all 750 stations and their metadata
Saved 750 stations metadata to ./table_meta.npz
Time elapsed = 1553.9474 seconds = 00:25:53

7. table_stations.py
Read table_meta.npz and create code for multiple LaTeX tables in stations_table.tex

