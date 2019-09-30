# -*- coding: utf-8 -*-


import os            # Operating System package, used for setting directories and navigating directories
import shutil        # Package used to move .csv files from one directory to another
import glob
import pandas as pd  # Pandas used to process data
import io
import pvlib

try:
    # python 2 compatibility
    from urllib2 import urlopen, Request
except ImportError:
    from urllib.request import urlopen, Request

"""
Created on Mon Sep 30 13:13:09 2019

@author: DHOLSAPP
"""


path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\Weather_Database'


class CleanRawData:
    
    
    def createPickleFiles( currentDirectory ):
    
            
        path = currentDirectory
        
        
        dataFrames = CleanRawData.filesToDataFrame( path ) 
        
        
        #First delete the content of the folder you will be sending the files to.
        # We do this as organization to make sure all the files are current
        for root, dirs, files in os.walk(path + '\\Pandas_Pickle_DataFrames\\Pickle_RawData'):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        for root, dirs, files in os.walk(path + '\\Pandas_Pickle_DataFrames\\Pickle_FirstRows'):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        

        #Pull out the file names from the file path(.csv files) and return a list of file names without .csv extension
        fileNames = CleanRawData.filesNameListCSV_EPW( path )
        
        # Convert the fileNames to have a .pickle extention
        pickleStringList = CleanRawData.pickleNameList( fileNames )
        
        for i in range( 0 , len( fileNames ) ):
            dataFrames[i].to_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_RawData' +'\\'+ pickleStringList[i] )
    

        # Create the summary pickle
        
        CleanRawData.createPickleFileFirstRow( path )
        
    
    '''
    HELPER METHOD
    
    filesToDataFrame()
    
    Put both csv and epw hourly data files as dataframes,  At this point there will
    be no difference between csv and epw files since they are now pandas dataframes
    
     @param path            -String, path of the folder where the raw data .csv files 
                                     are located
    
     @return dataFramelist  -List, List of Dataframes containing semi cleaned frames.  
                                 *Note: the first row of the datafraemw will not be accessed
                                 The first line of data will be saved in a different list with 
                                 the same index                   
    '''
    
    def filesToDataFrame( path ):
        
        allCsvFiles = glob.glob(path + '\Python_RawData_Combined' + "/*.csv")
        allEpwFiles = glob.glob(path + '\Python_RawData_Combined' + "/*.epw")
  
        dataFrameCsvlist = [] # Create a list to hold all the csv dataframes
        dataFrameEpwlist = [] # Create a list to hold all the epw dataframes
        
        #Create a list of dataframes for csv files
        for i in range( 0 , len( allCsvFiles ) ):  
            # (access the file, skip the first 1 rows)
            csv_df = pd.read_csv(allCsvFiles[i], skiprows= 1 ,  header=0)
            #Helper method, deltes NA data and renames column headers
            if len(csv_df.columns) == 71:
                csv_df = csv_df.drop(['PresWth source','PresWth uncert (code)'], axis=1)
            csv_df = CleanRawData.renameFrame(csv_df)
            dataFrameCsvlist.append(csv_df) # Keep adding dataframes to the end of the list
    
    ############################################################################
    #Will have to sort the df by unique identifier at some point
    ######################################################    
    
        #Create a list of dataframes for csv files
        for i in range( 0 , len( allEpwFiles ) ):  
            # Use helper method to convert the EPW file to a dataframe
            epw_df = CleanRawData.read_epw_df(allEpwFiles[i] , coerce_year=None)
            #Put the datetime objects into their own column by reseting the index
            epw_df.reset_index(inplace=True)
            #Convert the pandas time series to MM/DD/YYYY format
            epw_df['Date (MM/DD/YYYY)'] = epw_df['index'].map(lambda x: x.strftime('%m/%d/%Y'))
            #Convert the pandas time series to "Hour(24hrs scale):Minute"   format
            epw_df['Time (HH:MM)'] = epw_df['index'].map(lambda x: x.strftime('%H:%M'))
            #Convert the atmospheric pressure form Pa to mbar
            epw_df['atmospheric_pressure'] = epw_df['atmospheric_pressure'].apply(lambda x: x/100)
            #Convert the visibility to km to m
            epw_df['visibility'] = epw_df['visibility'].apply(lambda x: x*1000)        
            # Drop columns that we do not need
            epw_df = epw_df.drop(['index', 
                                  'year',
                                  'month',
                                  'day',
                                  'hour',
                                  'minute',
                                  'data_source_unct'], 
                                    axis=1)
            #Re-index the columns in a proper fashion
            epw_df = epw_df.reindex(columns = ['Date (MM/DD/YYYY)', 
                                               'Time (HH:MM)',
                                               'etr',
                                               'etrn',
                                               'ghi_infrared',
                                               'ghi',
                                               'dni', 
                                               'dhi',
                                               'global_hor_illum',
                                               'direct_normal_illum', 
                                               'diffuse_horizontal_illum',
                                               'zenith_luminance',
                                               'total_sky_cover',
                                               'opaque_sky_cover',
                                               'temp_air',
                                               'temp_dew',
                                               'relative_humidity',
                                               'atmospheric_pressure',
                                               'wind_direction',
                                               'wind_speed',
                                               'visibility', 
                                               'ceiling_height',
                                               'precipitable_water',
                                               'aerosol_optical_depth',
                                               'albedo',
                                               'liquid_precipitation_depth',
                                               'liquid_precipitation_quantity',
                                               'present_weather_observation',
                                               'present_weather_codes',
                                               'snow_depth',
                                               'days_since_last_snowfall'])                                          
          #Rename the columns of .epw_df to match the .csv_df  ])    
    
            
    #Perform all cleaning to match the format of the CSVs
            # Start with the first df
           
            epw_df.columns = ['Date (MM/DD/YYYY)', 
                          'Time (HH:MM)',
                          'Hourly extraterrestrial radiation on a horizontal surface',
                          'Hourly extraterrestrial radiation normal to the sun',
                          'Horizontal infrared radiation',
                          'Global horizontal irradiance',
                          'Direct normal irradiance',
                          'Diffuse horizontal irradiance',
                          'Global horizontal illuminance',
                          'Direct normal illuminance',
                          'Diffuse horizontal illuminance',
                          'Zenith luminance',
                          'Total sky cover',
                          'Opaque sky cover',
                          'Dry-bulb temperature',
                          'Dew-point temperature',
                          'Relative humidity',
                          'Station pressure',
                          'Wind direction',
                          'Wind speed',
                          'Horizontal visibility',
                          'Ceiling height',
                          'Precipitable water',
                          'Aerosol optical depth, broadband',
                          'Albedo',
                          'Liquid percipitation depth',
                          'Liquid percipitation quantity',
                          'Present Weather Observations',
                          'Present Weather Codes',
                          'Snow Depth',
                          'Days Since Last Snowfall']        
            
            
            dataFrameEpwlist.append(epw_df) # Keep adding dataframes to the end of the list
    
        #Combine both dataframe lists together
        dataFrameCsvlist.extend(dataFrameEpwlist)
    
    
        return dataFrameCsvlist    

    '''
    HELPER METHOD
    
    filesNameListCSV()
    
    Pull out the file name from the file path and return a list of file names
    
    @param path       -String, path to the folder with the files
    
    @return allFiles  -List of Strings, filenames without the file path or extension
    
    '''
    def filesNameListCSV_EPW( path ):
        
        #list of strings of all the files
        allFilesCSV = glob.glob(path + '\Python_RawData_Combined' + "/*.csv")
        allFilesEPW = glob.glob(path + '\Python_RawData_Combined' + "/*.epw")
        
        allFiles = allFilesCSV + allFilesEPW 
        
        #for loop to go through the lists of strings and to remove irrelavant data
        for i in range( 0, len( allFiles ) ):
    
            # Delete the path and pull out only the file name using the os package from each file
            temp = os.path.basename(allFiles[i])
            #remove extension from file name
            temp = temp[:-4]
            allFiles[i] = temp
            
    
        
        return allFiles
    
    '''
    HELPER METHOD
    
    pickleNameList()
    
    convert a list of strings to have a .pickle extention
    
    @param fileNames  - List of Strings , string of list names to be converted to have pickle extention
    
    @return allFiles  - List of Strings, file names with pickle extension
    
    '''
    
    def pickleNameList( fileNames ):
    
        pickleNames = []
    
        for i in range( 0 , len( fileNames ) ):
            temp = fileNames[i] + '.pickle'
            pickleNames.append(temp)
        
        return pickleNames
    
    '''
    Main METHOD
    
    createPickleFileFirstRow()
    
    Cycle through the raw csv folder and pull out the first row of every csv.  
    Combine the lists into a dataframe and save it as a pickle
    
     @param path          -string, current working directory
    
     @return void         -Will convert dataframe into raw pickle datafile 
                      
    '''
    
    def createPickleFileFirstRow( path ):
        
        fileName = 'firstRowSummary_Of_CSV_Files'
        # Convert the fileNames to have a .pickle extention
        
        dataFrame = CleanRawData.cleanFirstRowDataFrame( path )
        
        dataFrame.to_pickle( path + '\Pandas_Pickle_DataFrames\Pickle_FirstRows' +'\\'+ fileName + '.pickle' )

    '''
    HELPER METHOD
    
    cleanAndRenameFrame()
    
    Rename and clean a csv dataframe (raw data)
    
     @param df            -DataFrame, frame of raw data from csv file, uncleaned
    
     @return df           -DataFrame, cleaned and renamed frame                  
    '''    
    def renameFrame(df):
    
        #Rename the columns of the frame
        df.columns = ['Date (MM/DD/YYYY)', 
                      'Time (HH:MM)',
                      'Hourly extraterrestrial radiation on a horizontal surface',
                      'Hourly extraterrestrial radiation normal to the sun',
                      'Global horizontal irradiance',
                      'Global horizontal irradiance source flag',
                      'Global horizontal irradiance uncertainty',
                      'Direct normal irradiance',
                      'Direct normal irradiance source flag',
                      'Direct normal irradiance uncertainty',
                      'Diffuse horizontal irradiance',
                      'Diffuse horizontal irradiance source flag',
                      'Diffuse horizontal irradiance uncertainty',
                      'Global horizontal illuminance',
                      'Global horizontal illuminance source flag',
                      'Global horizontal illuminance uncertainty',
                      'Direct normal illuminance',
                      'Direct normal illuminance source flag',
                      'Direct normal illuminance uncertainty',
                      'Diffuse horizontal illuminance',
                      'Diffuse horizontal illuminance source flag',
                      'Diffuse horizontal illuminance uncertainty',
                      'Zenith luminance',
                      'Zenith luminance source flag',
                      'Zenith luminance uncertainty',
                      'Total sky cover',
                      'Total sky cover (source)',
                      'Total sky cover (uncertainty)',
                      'Opaque sky cover',
                      'Opaque sky cover (source)',
                      'Opaque sky cover flag (uncertainty)',
                      'Dry-bulb temperature',
                      'Dry-bulb temperature flag (source)',
                      'Dry-bulb temperature flag (uncertainty)',
                      'Dew-point temperature',
                      'Dew-point temperature flag (source)',
                      'Dew-point temperature flag (uncertainty)',
                      'Relative humidity',
                      'Relative humidity flag (source)',
                      'Relative humidity flag (uncertainty)',
                      'Station pressure',
                      'Station pressure flag (source)',
                      'Station pressure flag (uncertainty)',
                      'Wind direction',
                      'Wind direction flag (source)',
                      'Wind direction flag (uncertainty)',
                      'Wind speed',
                      'Wind speed flag (source)',
                      'Wind speed flag (uncertainty)',
                      'Horizontal visibility',
                      'Horizontal visibility flag (source)',
                      'Horizontal visibility flag (uncertainty)',
                      'Ceiling height',
                      'Ceiling height flag (source)',
                      'Ceiling height flag (uncertainty)',
                      'Precipitable water',
                      'Precipitable water flag (source)',
                      'Precipitable water flag (uncertainty)',
                      
                      # Data may contain NA 
                      ######
                      'Aerosol optical depth, broadband',
                      'Aerosol optical depth, broadband flag (source)',
                      'Aerosol optical depth, broadband flag (flag)',
                      'Albedo',
                      'Albedo flag (source)',
                      'Albedo flag (uncertainty)',
                      ######
                      
                      'Liquid percipitation depth',
                      'Liquid percipitation quantity',
                      'Liquid percipitation depth flag (source)',
                      'Liquid percipitation depth flag (uncertainty)',
                      'Present Weather']
        return df
    
    
    '''
    HELPER METHOD
    
    cleanFirstRowDataFrame()
    
    Create the First row summary from both csv and epw
    
     @param path                -String, path of current working directory
    
     @return firstRowDataFrame  -DataFrame, clean and frame of all the first rows of .csv files                  
    '''
    
    
    
    def cleanFirstRowDataFrame( path ):
        # Create the data frame from the first line of the .csv files
    
        path = path + '\Python_RawData_Combined'  
        
        #Create a pandas frame of all the row 1 data 
        row1_df = pd.DataFrame(columns=['Site Identifier Code',
                                        'Station name',
                                        'Station State', 
                                        'Site time zone (Universal time + or -)',
                                        'Site latitude', 
                                        'Site longitude',
                                        'Site elevation (meters)',
                                        'Station country or political unit',
                                        'WMO region',
                                        'Time zone code',
                                        'Koppen-Geiger climate classification'])
                
        #Glob all the .csv files together        
        allFilesCSV = glob.glob(path + "/*.csv")
        #Organize all Csv files into a pandas frame
        for i in range(0, len(allFilesCSV)):
        
            csv_df = pd.read_csv(allFilesCSV[i], skiprows= 0 ,nrows= 1, header = None, 
                                 names =['Site Identifier Code',
                                        'Station name',
                                        'Station State', 
                                        'Site time zone (Universal time + or -)',
                                        'Site latitude', 
                                        'Site longitude',
                                        'Site elevation (meters)',
                                        'Station country or political unit',
                                        'WMO region',
                                        'Time zone code',
                                        'Koppen-Geiger climate classification'] )
            
            row1_df = row1_df.append({'Site Identifier Code': csv_df['Site Identifier Code'][0],
                                      'Station name': csv_df['Station name'][0],
                                      'Station State': csv_df['Station State'][0],   
                                      'Site time zone (Universal time + or -)': csv_df[ 'Site time zone (Universal time + or -)'][0],
                                      'Site latitude': csv_df['Site latitude'][0], 
                                      'Site longitude': csv_df['Site longitude'][0],
                                      'Site elevation (meters)': csv_df['Site elevation (meters)'][0],
                                      'Station country or political unit': csv_df['Station country or political unit'][0],
                                      'WMO region': csv_df['WMO region'][0],
                                      'Time zone code': csv_df['Time zone code'][0],
                                      'Koppen-Geiger climate classification': csv_df['Koppen-Geiger climate classification'][0]
                                    }, ignore_index=True )
        
        
        #glob all the .epw files together
        allFilesEPW = glob.glob(path + "/*.epw") 
        
        for j in range( 0 , len(allFilesEPW)):
            #Helper method that pulls the first row of data
            epwFirstRow = CleanRawData.read_epw_firstRow(allFilesEPW[j], coerce_year=None)
        
            # Use the dictionary created to append the master frame
            row1_df = row1_df.append({'Site Identifier Code': '',
                                      'Station name':epwFirstRow.get('city'),
                                      'Station State': '',   
                                      'Site time zone (Universal time + or -)': epwFirstRow.get('TZ'),
                                      'Site latitude': epwFirstRow.get('latitude'), 
                                      'Site longitude': epwFirstRow.get('longitude'),
                                      'Site elevation (meters)': epwFirstRow.get('altitude'),
                                      'Station country or political unit': epwFirstRow.get('country'),
                                      'WMO region': '',
                                      'Time zone code': '',
                                      'Koppen-Geiger climate classification': ''
                                    }, ignore_index=True ) 
        
        #The read_epw_firstRow() parser is having difficulty with the WMO code, some identifiers contain characters
        # Created a unique ID generator to go through the file paths and pull out each identifier
        
        uniqueID = allFilesCSV + allFilesEPW
        #Helper method ID generator found in RawDataSearch_and_FirstRow_SummaryReport.py
        uniqueID = CleanRawData.stringList_UniqueID_List( uniqueID)
        
        row1_df['Site Identifier Code'] = uniqueID
        
        return row1_df
            
    '''
    Read an EPW file in to a pandas dataframe.
    
    Note that values contained in the metadata dictionary are unchanged
    from the EPW file.
    
    EPW files are commonly used by building simulation professionals
    and are widely available on the web. For example via:
    https://energyplus.net/weather , http://climate.onebuilding.org or
    http://www.ladybug.tools/epwmap/
    
    
    Parameters
    ----------
    filename : String
        Can be a relative file path, absolute file path, or url.
    
    coerce_year : None or int, default None
        If supplied, the year of the data will be set to this value. This can
        be a useful feature because EPW data is composed of data from
        different years.
        Warning: EPW files always have 365*24 = 8760 data rows;
        be careful with the use of leap years.
    
    
    Returns
    -------
    Tuple of the form (data, metadata).
    
    data : DataFrame
        A pandas dataframe with the columns described in the table
        below. For more detailed descriptions of each component, please
        consult the EnergyPlus Auxiliary Programs documentation
        available at: https://energyplus.net/documentation.
    
    metadata : dict
        The site metadata available in the file.
    
    Notes
    -----
    
    The returned structures have the following fields.
    
    ===============   ======  =========================================
    key               format  description
    ===============   ======  =========================================
    loc               String  default identifier, not used
    city              String  site loccation
    state-prov        String  state, province or region (if available)
    country           String  site country code
    data_type         String  type of original data source
    WMO_code          String  WMO identifier
    latitude          Float   site latitude
    longitude         Float   site longitude
    TZ                Float   UTC offset
    altitude          Float   site elevation
    ===============   ======  =========================================
    
    
    =============================       ==============================================================================================================================================================
    EPWData field                       description
    =============================       ==============================================================================================================================================================
    index                               A pandas datetime index. NOTE, times are set to local standard time (daylight savings is not included). Days run from 0-23h to comply with PVLIB's convention
    year                                Year, from original EPW file. Can be overwritten using coerce function.
    month                               Month, from original EPW file
    day                                 Day of the month, from original EPW file.
    hour                                Hour of the day from original EPW file. Note that EPW's convention of 1-24h is not taken over in the index dataframe used in PVLIB.
    minute                              Minute, from original EPW file. Not used.
    data_source_unct                    Data source and uncertainty flags. See [1], chapter 2.13
    temp_air                            Dry bulb temperature at the time indicated, deg C
    temp_dew                            Dew-point temperature at the time indicated, deg C
    relative_humidity                   Relatitudeive humidity at the time indicated, percent
    atmospheric_pressure                Station pressure at the time indicated, Pa
    etr                                 Extraterrestrial horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    etrn                                Extraterrestrial normal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    ghi_infrared                        Horizontal infrared radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    ghi                                 Direct and diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    dni                                 Amount of direct normal radiation (modeled) recv'd during 60 mintues prior to timestamp, Wh/m^2
    dhi                                 Amount of diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    global_hor_illum                    Avg. total horizontal illuminance recv'd during the 60 minutes prior to timestamp, lx
    direct_normal_illum                 Avg. direct normal illuminance recv'd during the 60 minutes prior to timestamp, lx
    diffuse_horizontal_illum            Avg. horizontal diffuse illuminance recv'd during the 60 minutes prior to timestamp, lx
    zenith_luminance                    Avg. luminance at the sky's zenith during the 60 minutes prior to timestamp, cd/m^2
    wind_direction                      Wind direction at time indicated, degrees from north (360 = north; 0 = undefined,calm)
    wind_speed                          Wind speed at the time indicated, meter/second
    total_sky_cover                     Amount of sky dome covered by clouds or obscuring phenonema at time stamp, tenths of sky
    opaque_sky_cover                    Amount of sky dome covered by clouds or obscuring phenonema that prevent observing the sky at time stamp, tenths of sky
    visibility                          Horizontal visibility at the time indicated, km
    ceiling_height                      Height of cloud base above local terrain (7777=unlimited), meter
    present_weather_observation         Indicator for remaining fields: If 0, then the observed weather codes are taken from the following field. If 9, then missing weather is assumed.
    present_weather_codes               Present weather code, see [1], chapter 2.9.1.28
    precipitable_water                  Total precipitable water contained in a column of unit cross section from earth to top of atmosphere, cm
    aerosol_optical_depth               The broadband aerosol optical depth per unit of air mass due to extinction by aerosol component of atmosphere, unitless
    snow_depth                          Snow depth in centimeters on the day indicated, (999 = missing data)
    days_since_last_snowfall            Number of days since last snowfall (maximum value of 88, where 88 = 88 or greater days; 99 = missing data)
    albedo                              The ratio of reflected solar irradiance to global horizontal irradiance, unitless
    liquid_precipitation_depth          The amount of liquid precipitation observed at indicated time for the period indicated in the liquid precipitation quantity field, millimeter
    liquid_precipitation_quantity       The period of accumulation for the liquid precipitation depth field, hour
    =============================       ==============================================================================================================================================================
    
    References
    ----------
    
    [1] EnergyPlus documentation, Auxiliary Programs
    https://energyplus.net/documentation.
    '''
    
    def read_epw_firstRow(filename, coerce_year=None):
    
        if filename.startswith('http'):
            # Attempts to download online EPW file
            # See comments above for possible online sources
            request = Request(filename, headers={'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 '
                'Safari/537.36')})
            response = urlopen(request)
            csvdata = io.StringIO(response.read().decode(errors='ignore'))
        else:
            # Assume it's accessible via the file system
            csvdata = open(filename, 'r')
    
        # Read line with metadata
        firstline = csvdata.readline()
    
        head = ['loc', 'city', 'state-prov', 'country', 'data_type', 'WMO_code',
                'latitude', 'longitude', 'TZ', 'altitude']
        meta = dict(zip(head, firstline.rstrip('\n').split(",")))
    
        meta['altitude'] = float(meta['altitude'])
        meta['latitude'] = float(meta['latitude'])
        meta['longitude'] = float(meta['longitude'])
        meta['TZ'] = float(meta['TZ'])
    
        colnames = ['year', 'month', 'day', 'hour', 'minute', 'data_source_unct',
                    'temp_air', 'temp_dew', 'relative_humidity',
                    'atmospheric_pressure', 'etr', 'etrn', 'ghi_infrared', 'ghi',
                    'dni', 'dhi', 'global_hor_illum', 'direct_normal_illum',
                    'diffuse_horizontal_illum', 'zenith_luminance',
                    'wind_direction', 'wind_speed', 'total_sky_cover',
                    'opaque_sky_cover', 'visibility', 'ceiling_height',
                    'present_weather_observation', 'present_weather_codes',
                    'precipitable_water', 'aerosol_optical_depth', 'snow_depth',
                    'days_since_last_snowfall', 'albedo',
                    'liquid_precipitation_depth', 'liquid_precipitation_quantity']
    
        # We only have to skip 6 rows instead of 7 because we have already used
        # the realine call above.
        data = pd.read_csv(csvdata, skiprows=6, header=0, names=colnames)
    
        # Change to single year if requested
        if coerce_year is not None:
            data["year"] = coerce_year
    
        # create index that supplies correct date and time zone information
        dts = data[['month', 'day']].astype(str).apply(lambda x: x.str.zfill(2))
        hrs = (data['hour'] - 1).astype(str).str.zfill(2)
        dtscat = data['year'].astype(str) + dts['month'] + dts['day'] + hrs
        idx = pd.to_datetime(dtscat, format='%Y%m%d%H')
        idx = idx.dt.tz_localize(int(meta['TZ'] * 3600))
        data.index = idx
    
        return meta
    
    '''
    stringList_UniqueID_List()
    
    This method takes a lists of strings and searches for a unique sample identifier.  
    It then takes that unique identifier and creates a list.  If one of the strings 
    does not have a unique identifier it will put that original string back into the list
    
    Example List
    
    '690190TYA.pickle',
    'GRC_SOUDA(AP)_167460_IW2.pickle',
    'GRC_SOUDA-BAY-CRETE_167464_IW2.pickle',
    'Test']
    
    
    Return List
    
    '690190'
    '167460'
    '167464'
    'Test'
     
    
    param@ listOfStrings   -List of Strings , list of strings containing unique identifier
    
    @return                - List of Strings, list of filtered strings with unique identifiers
    '''
    
    def stringList_UniqueID_List( listOfStrings ):
        sampleList = []
        #Create a list of ASCII characters to find the sample name from the given string
        for i in range(0, len(listOfStrings)):
            
            #Create a list of ASCII characters from the string
            ascii_list =[ord(c) for c in listOfStrings[i]]
            char_list = list(listOfStrings[i])
    
            
            #If the first string  does not pass the filter set the sample flag to 0
     #       sampleFlag = 0 
            count = 0 
            # j will be the index referencing the next ASCII character
            for j in range(0, len(ascii_list)):
    
                #Filter to find a unique combination of characters and ints in sequence
                ###############
                
                # ASCII characters for numbers 0 - 10
                if ascii_list[j] >= 48 and ascii_list[j] <= 57:
    
                    #If a number is encountered increase the counter
                    count = count + 1
    
                    # If the count is 6 "This is how many numbers in a row the unique identifier will be"
                    if count == 3:
                        # Create a string of the unique identifier
                        sampleList.append( char_list[ j - 2 ] +
                                           char_list[ j - 1 ] + 
                                           char_list[ j ]     + 
                                           char_list[ j + 1 ] + 
                                           char_list[ j + 2 ] + 
                                           char_list[ j + 3 ] )
                        # Stop the search.  The identifier has been located
                        break
                # If the next ASCII character is not a number reset the counter to 0        
                else:
                    count = 0
            # If a unique identifier is not located insert string as placeholder so that indexing is not corrupted
            if count == 0 and j == len(ascii_list) - 1 :
                    
                sampleList.append(listOfStrings[i])        
                    
                    
        return sampleList       