#File:      parse.py
#Author:    Julia Beiferman
#Date:      7/5/2022

from datetime import datetime
import os
from bson import ObjectId
import pandas as pd
from pymongo import MongoClient
import time
import warnings
import pprint

warnings.filterwarnings('ignore')

client = MongoClient()
client = MongoClient('localhost', 27017)

mydatabase = client['SRC']
mycollection = mydatabase['VerboseRuns']
moduleCollection = mydatabase['Modules']

directory = r"\\datagroveaz.amr.corp.intel.com\sttd\HDMT\TesterIntegration\HISV\SRCLoopingData" #folder for src looping data 
testers = {}
runs = []
numFiles = 0 

def read_excel(filename, column, row):
    #Read a single cell value from an Excel file
    return pd.read_excel(filename, skiprows=row - 1, usecols=column, nrows=1, header=None, names=["Value"], engine='openpyxl').iloc[0]["Value"]


def findFails(filename, key, header):
    successRuns = [0,0]

    df = pd.read_excel(filename)
    run_df = df[df[header].str.startswith(key).fillna(False)]
    run_index = run_df[run_df[header].str.endswith(':').fillna(False)].index # returns a list of indexes to where HalInit is shown
    successRuns[1] = len(run_index)
    err = {}
    errormessages = []

    time_index = run_df[run_df[header].str.endswith('hours').fillna(False)].index

    for i in range(len(run_index+1)):
        subModule = str(read_excel(filename, "A", run_index[i]+2).replace(":", ""))
        
        result = str(read_excel(filename, "A", run_index[i]+3)) #add three because the index is 2 rows off and then read the line after
        runtime = ""
        if(len(time_index) > 0):
            runtime = str(read_excel(filename, "A", time_index[i]+2)).replace(subModule, "").replace(":", "")
        
        j = run_index[i]+3
        if result.endswith('ran successfully.') | result.startswith('No'):
            successRuns[0] += 1
            continue
        else: #if we don't immediately get an error, then read the following lines for error message or even pass
            try:
                #result = read_excel(filename, "A", run_index[i]+3) #add three because the index is 2 rows off and then read the line after
                hbiresult = read_excel(filename, "A", run_index[i]+6) #read the next 3 lines for cal card
                if hbiresult.startswith('No') or 'loops ran successfully' in result:
                    successRuns[0] += 1
                    continue
            except IndexError:
                pass
            except AttributeError:
                pass
            except TypeError:
                pass
            except FileNotFoundError:
                pass
            
            
            errormessages = []

            if(i+1 < len(run_index)):
                while j < run_index[i+1]+1:
                    errMsg = read_excel(filename, "A", j)

                    if str(errMsg).endswith('ran successfully.') | str(errMsg).startswith('No'):
                        successRuns[0] += 1
                        break
                    else:
                        try:
                            if(pd.isna(errMsg)):
                                pass
                            elif(pd.isna(read_excel(filename, "B", j))): #check if we read nan
                                errormessages.append(errMsg)
                            else:
                                letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
                                row = []
                                for letter in letters:
                                    try:
                                        readCol = read_excel(filename, letter, j)
                                        row.append(str(readCol))
                                    except IndexError:
                                        break
                                    errormessages.append(row)
                        except IndexError:
                                    break

                    
                    j+=1

                    
                            

        err.update({
            subModule: {
            'runtime': runtime,
            'errors': errormessages
            }
            })
    
    return successRuns, err

def extractIter(filename): #extract advanced data such as iterations
    #we need a few things.., these aren't always standardized

    iterations = {
        'Calibration':      [0,0],
        'Diagnostics':      [0,0],
        'ChannelCard':      [0,0],
        'DPS':              [0,0],
        'SysVal':           [0,0],
        'HalInit':          [0,0]
    }


    HDMTItr = ['Calibration', 'Diagnostics', 'ChannelCard', 'DPS', 'HDMTSysVal', 'HalInit']
    HBIItr = ['Calibration', 'HBIDiagnostics', 'HBICC', 'HBIDPS', 'HBISysVal', 'HalInit']

    header = read_excel(filename, "A", 1)
    nonRuns = []

    if 'HBI' in filename: # see if we're using HBI or HDMT before hand to save time, since their names are different for each module
        ItrList = HBIItr
    else:
        ItrList = HDMTItr

    i = 0

    errs = {}

    for key in iterations.keys():
        successRuns, err = findFails(filename, ItrList[i], header)
        iterations[key] = successRuns
        errs[key] = err
        if iterations[key][1] == 0:
            nonRuns.append(key)

        i += 1

    for noRun in nonRuns:
        iterations.pop(noRun)

    return iterations, errs

def getModuleData(id, filename, run, iterations, errs):
    srcDir = os.path.join(directory, filename, run)

    modules_ids = {}

    for mod in iterations.keys():
        module_data = []
        for subModule in os.listdir(srcDir):
            if mod in subModule:
                if subModule in errs[mod]:
                    modex = {
                        'module_execution': subModule,
                        'fail_info': errs[mod][subModule],
                        'parametric_data': ""
                        }

                    module_data.append(modex)
                
       
        moduleData = {
            'module_name': mod,
            'src_run': ObjectId(id),
            'tester_metadata': '',
            'start_time': datetime,
            'end_time':  datetime,
            'datagrove': srcDir,        
            'exeucting order': 1,
            'test_data': module_data,
            'summary': {
                'tests_passed': iterations[mod][0],
                'tests_executed': iterations[mod][1],
                'tests_failed': iterations[mod][1]-iterations[mod][0],
                'tests_acceptance': 0,
                'tests_bypassed': 0
            }
        }

        modid = moduleCollection.insert_one(moduleData)

        modules_ids.update({mod: modid.inserted_id})

    return modules_ids


def parseOne(filename, run, datasheet): #similar function to parse only one file
    #start = time.time()

    wbDir = os.path.join(directory, filename, run, datasheet)
    
    try:
        #things we cna get from the excel sheet
        date = run[0:10].replace("_",'/')
        ww = float(read_excel(wbDir, "A", 1).replace("Work Week: ", ""))
        tos = read_excel(wbDir, "A", 5).replace("TOS: ", "").replace('hdmtOS_', "").replace("_Release", "").replace("_", " ").replace("BUILD", ".")
        suite = read_excel(wbDir, "A", 6).replace("SRC looping Suite: ", "")
        HWConfig = read_excel(wbDir, "A", 4).replace("Config: ", "")
        deltaTime = read_excel(wbDir, "A", 10).replace("Total time: ", "")
        #startTime validation_details.txt
        #endTime

        tos = tos.split(".")

        iterations, errs = extractIter(wbDir)

        runToData = {
            'name': filename,
            'ww': ww,
            'tos': {
                'version' : tos[0],
                'major'   : tos[1],
                'minor'   : tos[2],
                'patch'   : tos[3],
                'build'   : tos[4],
                'formatted': tos[0]+"."+tos[1]+"."+tos[2]+"."+tos[3]+" Build "+tos[4]
            },
            'suite': suite,
            'summary': iterations,
            'comments': "",
            'datagrove': wbDir,
            'date': date,
            'ados': [],
            'tester_hw_config': {
                'config_string': HWConfig,
                'hw_config_xml': HWConfig
            },
            'RunSeed':	    "",
            'RunFlow':		"",
            'RunType': 	    "General",
            'start_time': deltaTime,
            'end_time': deltaTime

        }

        _id = mycollection.insert_one(runToData)

        #get object id to link
        objId = _id.inserted_id
        modules_ids = getModuleData(objId, filename, run, iterations, errs)
        

    except IndexError:
        pass
    except FileNotFoundError:
        pass    
        

    #end=time.time()

    #print(f"Uploaded to Mongodb. Elapsed Time: {end-start}s")


#parseOne('CH4HDMTISV02', '2022_07_22_13_25_15_Run','CH4HDMTISV02_2022_07_22_13_25_15.xlsx')
#\\datagroveaz.amr.corp.intel.com\sttd\HDMT\TesterIntegration\HISV\SRCLoopingData\CH4HDMTISV02\2022_07_22_13_25_15_Run

parseOne('CH4HBI10004', '2022_02_14_11_13_59_Run', 'CH4HBI10004_2022_02_14_11_13_59.xlsx')


def parseAll():
    start = time.time()
    numFiles = 0
    for filename in os.listdir(directory):
        if filename.startswith("CH4"): #filter out only testers that start with ch4 
            for run in os.listdir(os.path.join(directory, filename)):
                if run.endswith("_Run") and not run.startswith("2022_04_16_02") and run.startswith("2022") and not run.startswith("2022_01"):
                    datasheet = filename + "_" + run.replace("_Run", "") + ".xlsx"
                    
                    if datasheet in os.listdir(os.path.join(directory, filename, run)):
                        parseOne(filename, run, datasheet)
    end=time.time()
    print(f"Uploaded to Mongodb. Elapsed Time: {end-start}s, expected files: {numFiles}")

def updateSingle(id):
    query = {"_id": ObjectId(id)}
 
    instance = mycollection.find_one(query)
    
    formattedStr = instance['tos']['version'] + "." + instance['tos']['major'] + "." + instance['tos']['minor'] + "." + instance['tos']['patch']
    
    newValues = { "$set": {'tos': {
        'version' : instance['tos']['version'],
        'major'   : instance['tos']['major'],
        'minor'   : instance['tos']['minor'],
        'patch'   : instance['tos']['patch'],
        'build'   : instance['tos']['build'],
        "formatted": formattedStr}}}
    mycollection.update_one(query, newValues)
    

def updateAll():
    for id in mycollection.find().distinct('_id'):
        try:
            updateSingle(id)
        except KeyError:
            pass
        

#updateSingle('62eab2eff2497d27d99f5671')

#parseAll()

#updateAll()

