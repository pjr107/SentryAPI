#!/usr/bin/env python
'''
Created on Jan 3 2019

@author: Patrick Rosini
'''

import argparse
import logging
import json
import sentryConnection
import pandas as pd
from sentryLogging import logger
from collections import OrderedDict

logger.debug("Read Dish")

"""
In Use - enable
EVERTZ - Launch Status
EVERTZ - DMG1
EVERTZ - DMG2
EVERTZ - Encoder
Backup Port portnum (backup)
MULTICAST - groupAddr, desc
EVERTZ - IRD1
EVERTZ - IRD2
Multicast DUPLICATE
Primary Port - portnum (primary)
PORT - destPort
SSM1 - sourceIp (primary)
SSM2 - sourceIp (backup)
EVERTZ - Template
Audio_1 - 
Audio_2 - 
EVERTZ  Note-2
EVERTZ  Note-1
EVERTZ - Source Description
Sling Call DUPLICATE
SLING CALL - name, program name
Daily Summery Include
DISH CALL
BUNDLE
MAAMOV
Sentry Number - SentryName
BUNDLE NAME
"""

def main():
    '''
    main function
    '''
    logger.debug("Entering Read Dish Main")
    parser = argparse.ArgumentParser(description='Import new settings', add_help=True)
    parser.add_argument('--file','-f', dest='file', help='File to read', default="Sling.csv")
    parser.add_argument('--system' ,'-s', dest='system', help='URL of Sentry or Medius', required=True)
    parser.add_argument('--user' ,'-u', dest='userName', help='userName for login', required=True)
    parser.add_argument('--pass' ,'-p', dest='password', help='password for login', required=True)
    parser.add_argument('--sentrylist','-S', dest='sentrylist', help='list of Sentrys', default="sentrys.csv")
    parser.add_argument('--testing','-T', dest='testing', help='for testing, removes > 1000 and over Sentry 3', action='store_true')



    results = parser.parse_args()

    dt = pd.read_csv(results.file, keep_default_na=False)
    ProgramList = dt.to_dict('records')

    #sentrys=['10.0.1.12','10.0.1.13','10.0.1.14','10.126.2.37','10.126.2.39']
    sentrylist = open(results.sentrylist.strip(),"r")
    sentrys = sentrylist.readlines()

    medius = sentryConnection.Sentry(tekip=(results.system.strip()),
                        medius=True,
                        user=results.userName.strip(),
                        passwd=results.password.strip())

    UpdateMPEGInput = []

    for program in ProgramList:
        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug(program)
        if program['SLING CALL'] and (not results.testing or int(program['Sentry Number'].strip().replace("Sentry ","")) <= 3): # three to stay within my test system
            #primary monitoring
            ProgramDict = {'portnum':int((program['Primary Port']).replace("Port ",""))}
            ProgramDict['portNumber'] = int((program['Primary Port']).replace("Port ",""))
            ProgramDict['sourceIp'] = str(program['SSM1'].strip())
            ProgramDict['groupAddr'] = str(program['MULTICAST'].strip())
            ProgramDict['destPort'] = int(program['PORT'])
            ProgramDict['name'] = str(program['SLING CALL'].strip()) + str("-Pri")
            ProgramDict['desc'] = str(program['SSM1'].strip())
            ProgramDict['sentryName'] = sentrys[int(str(program['Sentry Number'].strip()).replace("Sentry ","")) - 1].strip()
            ProgramDict['providerName'] = str(program['SLING CALL'].strip()) + str("-Pri")
            if str(program['In Use'].strip()) == 'Yes':
                ProgramDict['enabled'] = True
            else:
                ProgramDict['enabled'] = False
            ProgramDict['Audio_1'] = str(program['Audio_1'].strip())
            ProgramDict['Audio_2'] = str(program['Audio_2'].strip())
            ProgramDict['userAdded'] = 'true'
            ProgramDict['programNumber'] = int(-1)            
            #write dict to list
            UpdateMPEGInput.append(ProgramDict)
            #Backup monitoring
            ProgramDict = {'sourceIp':str(program['SSM2'].strip())}
            if results.testing: # for testing fit the ports under 1000
                ProgramDict['portnum'] = int((program['Backup Port']).replace("Port ","")) - 500
                ProgramDict['portNumber'] = int((program['Backup Port']).replace("Port ","")) - 500
            else:
                ProgramDict['portnum'] = int((program['Backup Port']).replace("Port ",""))
                ProgramDict['portNumber'] = int((program['Backup Port']).replace("Port ",""))
            ProgramDict['groupAddr'] = str(program['MULTICAST'].strip())
            ProgramDict['destPort'] = int(program['PORT'])
            ProgramDict['name'] = str(program['SLING CALL'].strip()) + str("-Bu")
            ProgramDict['desc'] = str(program['SSM2'].strip())
            ProgramDict['sentryName'] = sentrys[int(str(program['Sentry Number'].strip()).replace("Sentry ","")) - 1].strip()
            ProgramDict['providerName'] = str(program['SLING CALL'].strip()) + str("-Bu")
            if str(program['In Use'].strip()) == 'Yes':
                ProgramDict['enabled'] = True
            else:
                ProgramDict['enabled'] = False
            ProgramDict['Audio_1'] = str(program['Audio_1'].strip())
            ProgramDict['Audio_2'] = str(program['Audio_2'].strip())
            ProgramDict['userAdded'] = 'true'
            ProgramDict['programNumber'] = int(-1)
            #write dict to list
            UpdateMPEGInput.append(ProgramDict)

    #print UpdateMPEGInput
    if logger.getEffectiveLevel() <= logging.DEBUG:
        for program in UpdateMPEGInput:
            logger.debug(json.dumps(program))
    
    medius.UpdateMPEGInput(UpdateMPEGInput, BreakNumber=40)
    medius.SetProgramMapping(UpdateMPEGInput, BreakNumber=40)
    medius.deletePrimaryPIDSettings(sentrys)
    medius.updatePrimaryAudio(UpdateMPEGInput)
    
 







if __name__ == '__main__':
    main()
