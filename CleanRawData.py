# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 13:13:09 2019

@author: DHOLSAPP
"""

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
        fileNames = filesNameListCSV_EPW( path )
        
        # Convert the fileNames to have a .pickle extention
        pickleStringList = pickleNameList( fileNames )
        
        for i in range( 0 , len( fileNames ) ):
            dataFrames[i].to_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_RawData' +'\\'+ pickleStringList[i] )
    

        # Create the summary pickle
        
        createPickleFileFirstRow( path )
        
    
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
            csv_df = RenameFrame(csv_df)
            dataFrameCsvlist.append(csv_df) # Keep adding dataframes to the end of the list
    
    ############################################################################
    #Will have to sort the df by unique identifier at some point
    ######################################################    
    
        #Create a list of dataframes for csv files
        for i in range( 0 , len( allEpwFiles ) ):  
            # Use helper method to convert the EPW file to a dataframe
            epw_df = read_epw_df(allEpwFiles[i] , coerce_year=None)
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
          #Rename the columns of .epw_df to match the .csv_df                                     ])    
    
            
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

