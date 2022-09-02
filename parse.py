#File:      parse.py
#Author:    Julia Beiferman
#Date:      7/5/2022

import os
import pandas as pd
from pymongo import MongoClient
import psycopg2

client = MongoClient()
client = MongoClient('localhost', 27017)

mydatabase = client['SRC']
mycollection = mydatabase['Runs']


postgres_insert_query = """ INSERT INTO mobile (name, date, ww, tos, suite, iterations, , MODEL, PRICE) VALUES (%s,%s,%s)"""
record_to_insert = (5, 'One Plus 6', 950)


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
    err = []

    time_index = run_df[run_df[header].str.endswith('hours').fillna(False)].index

    for i in range(len(run_index+1)):

        try:
            result = read_excel(filename, "A", run_index[i]+3) #add three because the index is 2 rows off and then read the line after
            modHrs = read_excel(filename, "A", time_index[i]+2)
            #successRuns.append(modHrs)
            if result.endswith('ran successfully.') | result.startswith('No'):
                successRuns[0] += 1
                continue
        except IndexError:
            pass
        except AttributeError:
            pass
        except TypeError:
            pass

        try:
            #result = read_excel(filename, "A", run_index[i]+3) #add three because the index is 2 rows off and then read the line after
            hbiresult = read_excel(filename, "A", run_index[i]+6) #read the next 3 lines for cal card
            if hbiresult.startswith('No') or 'loops ran successfully' in result:
                successRuns[0] += 1
            '''
            else: #if we don't immediately get an error, then read the following lines for error message or even pass
                for j in range(run_index[i]+3, run_index[i+1]+1):
                    result = read_excel(filename, "A", run_index[j])
                                       
                    if result.endswith('ran successfully.') | result.startswith('No'):
                        successRuns[0] += 1
                        err = []
                        break
                    else:
                        err.append(result)
            '''

        except IndexError:
            pass
        except AttributeError:
            pass
        except TypeError:
            pass

    return successRuns

def extractIter(filename): #extract advanced data such as iterations
    #we need a few things.., these aren't always standardized

    '''
    New Table SRC fail report 
    optional things to view 
    Comment:
    ADO:        Assigned
    Fails:      0/2
    Module:     Calibration
    Tier:       0
    Instances: 
    '''

    iterations = {
        'Calibration':      [0,0], #add a third element delta time
        'Diagnostics':      [0,0],
        'ChannelCard':      [0,0],
        'DPS':              [0,0],
        'SysVal':           [0,0],
        'HalInit':          [0,0]
    }

    allinstances = {
        'Calibration':      [],
        'Diagnostics':      [],
        'ChannelCard':      [],
        'DPS':              [],
        'SysVal':           [],
        'HalInit':          []
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

    for key in iterations.keys():
        iterations[key] = findFails(filename, ItrList[i], header)
        if iterations[key][1] == 0:
            nonRuns.append(key)

        i += 1

    for noRun in nonRuns:
        iterations.pop(noRun)

    return iterations


#testfile = os.path.join(directory, 'CH4HBI10004', '2022_01_05_17_41_39_Run', 'CH4HBI10004_2022_01_05_17_41_39.xlsx')
    

file = os.path.join(directory, 'CH4HDMTISV10', '2022_06_17_16_04_12_Run','CH4HDMTISV10_2022_06_17_16_04_12.xlsx')



def parseFiles():
    global numFiles

    for filename in os.listdir(directory):
        if filename.startswith("CH4"): #filter out only testers that start with ch4 
            for run in os.listdir(os.path.join(directory, filename)):
                if run.endswith("_Run") and not run.startswith("2022_04_16_02") and run.startswith("2022"):
                    for datasheet in os.listdir(os.path.join(directory, filename, run)):
                        if datasheet.startswith(filename) and datasheet.endswith("xlsx") and filename[0]!="~":
                            wbDir = os.path.join(directory, filename, run, datasheet)
                            try:
                                
                                date = run[0:10].replace("_",'/')
                                ww = float(read_excel(wbDir, "A", 1).replace("Work Week: ", ""))
                                tos = read_excel(wbDir, "A", 5).replace("TOS: ", "").replace('hdmtOS_', "").replace("_Release", "").replace("_", " ").replace("BUILD", "Build ")
                                suite = read_excel(wbDir, "A", 6).replace("SRC looping Suite: ", "")
                                
                                tos = tos.split(" ", 1)

                                runToData = {
                                    'name': filename,
                                    'ww': ww,
                                    'tos': 
                                        {
                                            'version': tos[0],
                                            'build': tos[1]
                                        },
                                    'suite': suite,
                                    'iteration': extractIter(wbDir),
                                    'comments': "",
                                    'datagrove': os.path.join(directory, filename, run),
                                    'date': date,
                                    'ados': []
                                }

                                mycollection.insert_one(runToData)
                                numFiles += 1
                                

                            except FileNotFoundError:
                                pass
                            
            
    
    print(numFiles)
    print("done uploading")

parseFiles()

