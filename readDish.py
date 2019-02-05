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
    parser.add_argument('--userName' ,'-u', dest='userName', help='userName for login', required=True)
    parser.add_argument('--password' ,'-p', dest='password', help='password for login', required=True)

    results = parser.parse_args()

    dt = pd.read_csv(results.file, keep_default_na=False)
    ProgramList = dt.to_dict('records')

    sentrys=['10.0.1.12','10.0.1.13','10.0.1.14','10.126.2.37','10.126.2.39']

    medius = sentryConnection.Sentry(tekip=(results.system.strip()),
                        medius=True,
                        user=results.userName,
                        passwd=results.password)

    UpdateMPEGInput = []

    for program in ProgramList:
        if logger.getEffectiveLevel() <= logging.DEBUG:
            print program
        if program['SLING CALL'] and int(program['Sentry Number'].replace("Sentry ","")) <= 3:
            #primary monitoring
            ProgramDict = {'portnum':int((program['Primary Port']).replace("Port ",""))}
            ProgramDict['sourceIp'] = str(program['SSM1'])
            ProgramDict['groupAddr'] = str(program['MULTICAST'])
            ProgramDict['destPort'] = int(program['PORT'])
            ProgramDict['name'] = str(program['SLING CALL']) + str("_PRI")
            ProgramDict['desc'] = str(program['MULTICAST'])
            ProgramDict['sentryName'] = sentrys[int(str(program['Sentry Number']).replace("Sentry ","")) - 1]
            ProgramDict['providerName'] = str(program['SLING CALL'])
            if str(program['In Use']) == 'Yes':
                ProgramDict['enabled'] = True
            else:
                ProgramDict['enabled'] = False
            ProgramDict['Audio_1'] = str(program['Audio_1'])
            ProgramDict['Audio_2'] = str(program['Audio_2'])
            ProgramDict['userAdded'] = 'true'
            #write dict to list
            UpdateMPEGInput.append(ProgramDict)
            #Backup monitoring
            #turning this off because i don't have port 1000+ on test Systems 
            '''ProgramDict = {'portnum':int((program['Backup Port']).replace("Port ",""))}
            ProgramDict['sourceIp'] = str(program['SSM2'])
            ProgramDict['groupAddr'] = str(program['MULTICAST'])
            ProgramDict['destPort'] = int(program['PORT'])
            ProgramDict['name'] = str(program['SLING CALL']) + str("_BU")
            ProgramDict['program name'] = str(program['SLING CALL'])
            ProgramDict['desc'] = str(program['MULTICAST'])
            ProgramDict['sentryName'] = sentrys[int(str(program['Sentry Number']).replace("Sentry ","")) - 1]
            ProgramDict['providerName'] = str(program['SLING CALL'])
            if str(program['In Use']) == 'Yes':
                ProgramDict['enabled'] = True
            else:
                ProgramDict['enabled'] = False
            ProgramDict['Audio_1'] = str(program['Audio_1'])
            ProgramDict['Audio_2'] = str(program['Audio_2'])
            ProgramDict['userAdded'] = 'true'
            #write dict to list
            UpdateMPEGInput.append(ProgramDict)'''

    #print UpdateMPEGInput
    if logger.getEffectiveLevel() <= logging.DEBUG:
        for program in UpdateMPEGInput:
            print json.dumps(program)
    
    medius.UpdateMPEGInput(UpdateMPEGInput)








if __name__ == '__main__':
    main()
