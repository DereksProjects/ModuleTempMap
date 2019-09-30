import pandas as pd  # Pandas used to process data
import os            # Operating System package, used for setting directories and navigating directories
import xlwings as xw # XLWings package used to communicate with excel
import shutil        # Package used to move .csv files from one directory to another
import zipfile       # Package used to unzip files in a directory




class OrganizeDataFiles:
    
    #Path will be the current working directory
    @staticmethod
    def isolateFiles( path ):

    #########
    #First search for zipped csv files
    #########
        zippedFiles = []
        # Use os walk to cycle through all directories and pull out .zip files
        for dirpath, subdirs, files in os.walk(path + '\RawData'):
            for x in files:
                if x.endswith(".zip"):
                    #Join the full path to the isolated folder, add to the zipped files list
                    # Note: os.path is referencing a method not the raw path argument
                    zippedFiles.append(os.path.join(dirpath, x))
                elif x.endswith(".ZIP"):
                    #Join the full path to the isolated folder, add to the zipped files list
                    # Note: os.path is referencing a method not the raw path argument
                    zippedFiles.append(os.path.join(dirpath, x))            
        
    ###################################    
        #Delete the content of the folder you will be sending the files to.
        # We do this as organization to make sure all the files are current
        for root, dirs, files in os.walk(path + '\Python_RawData_Combined'):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
    #####################################    
        # Unzip all the files and put them into the directory
        for i in range(0 , len( zippedFiles ) ):
            with zipfile.ZipFile( zippedFiles[i] ,"r") as zip_ref:
                # Directory to put files into
                zip_ref.extractall(path + '\Python_RawData_Combined')

       
    #########
    #Search for csv files through the directories
    #########
    
        cSV_Files = []
        # Use os walk to cycle through all directories and pull out .csv files
        for dirpath, subdirs, files in os.walk(path + '\RawData'):
            for x in files:
                if x.endswith(".csv"):
                    #Join the full path to the isolated folder, add to the csv files list
                    # Note: os.path is referencing a method not the raw path argument
                    cSV_Files.append(os.path.join(dirpath, x))
                    
                elif x.endswith(".CSV"):
                    #Join the full path to the isolated folder, add to the csv files list
                    # Note: os.path is referencing a method not the raw path argument
                    cSV_Files.append(os.path.join(dirpath, x))   
        
        # Move all CSV files and put them into the directory  
        for i in range(0 , len( cSV_Files ) ):
            
            shutil.copy(cSV_Files[i], path + '\Python_RawData_Combined')

            
    #########
    #Search for epw files through the directories
    #########          
       
        ePW_Files = []     
        # Use os walk to cycle through all directories and pull out .csv files
        for dirpath, subdirs, files in os.walk(path + '\RawData'):
            for x in files:
                if x.endswith(".epw"):
                    #Join the full path to the isolated folder, add to the csv files list
                    # Note: os.path is referencing a method not the raw path argument
                    ePW_Files.append(os.path.join(dirpath, x))
                    
                elif x.endswith(".EPW"):
                    #Join the full path to the isolated folder, add to the csv files list
                    # Note: os.path is referencing a method not the raw path argument
                    ePW_Files.append(os.path.join(dirpath, x))           
                  
    
        # Move all .epw files and put them into the directory  
        for i in range(0 , len( ePW_Files ) ):
            
            shutil.copy(ePW_Files[i], path + '\Python_RawData_Combined')

    ###############################
    #If zipped files extracted unwanted file types, this will delete them
        #Currently only removing .WY3 data from the Canada data that was extracted 
        # from the zipped folders
 
        dir_name = path + '\Python_RawData_Combined'
        allFiles = os.listdir(dir_name)
        
        for item in allFiles:
            if item.endswith(".WY3"):
                os.remove(os.path.join(dir_name, item))    
        

#OrganizeDataFiles.isolateFiles(r'C:\Users\DHOLSAPP\Desktop\Summer_Project\Weather_Database')        
        


    
