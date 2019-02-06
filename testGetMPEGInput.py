#!/usr/bin/env python
'''
Created on Feb 5 2019

@author: Patrick Rosini
'''

import json
import argparse
import sentryConnection
from sentryLogging import logger


def main():
    '''
    main function
    '''

    logger.debug("Entering Read Dish Main")
    parser = argparse.ArgumentParser(description='Import new settings', add_help=True)
    parser.add_argument('--system' ,'-s', dest='system', help='URL of Sentry or Medius', required=True)
    parser.add_argument('--userName' ,'-u', dest='userName', help='userName for login', required=True)
    parser.add_argument('--password' ,'-p', dest='password', help='password for login', required=True)

    results = parser.parse_args()

    sentrys=['10.0.1.12','10.0.1.13','10.0.1.14','10.126.2.37','10.126.2.39']

    medius = sentryConnection.Sentry(tekip=(results.system.strip()),
                        medius=True,
                        user=results.userName.strip(),
                        passwd=results.password.strip())
    
    medius.getMPEGInput()



if __name__ == '__main__':
    main()
