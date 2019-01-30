#!/usr/bin/env python
'''
Created on Aug 13 2018

@author: Patrick Rosini
'''

import requests #request package will have to be installed, does HTTP requests
import json
from time import sleep #we can only do pregram stats requests once per minute
from sentryLogging import logger
import sentryUtils

STATS_SLEEP_TIME = 60  # Time to wait between requests

logger.debug("Entering Sentry Connection")

class Sentry(object):
    """
    Class to connect to Sentry
    """

    def __init__(self,
                 tekip="",
                 medius=True,
                 user="",
                 passwd=""):
        """
        Initilize the connection to the Sentry
        This will build the request URL
        arguments:
                tekIP - Ip of Sentry/Medius
                medius - True if Medius
                user - Logon User name
                passwd - Password
                requestURL - Url for Request
        """

        logger.debug("Entering Sentry Init")
        self.tekip = tekip
        self.medius = medius
        self.user = user
        self.passwd = passwd
        self.requesturl = "http://"+user+":"+passwd+"@"+tekip+"/vnm-api/index.php"
        logger.debug("Request URL: {0!s}".format(self.requesturl))
        logger.debug("leaving Sentry Init")

    def test_login(self):
        """
        Test logon
        this will return the response and headers from the Sentry
        This should get a 200 response and an error saying
        there is no real request
        """

        logger.debug("Entering Sentry test login")
        this_response = requests.get(self.requesturl)
        print "StatusCode: " + str(this_response.status_code)
        print "Headers: "
        for header, value in this_response.headers.items():
            print "    %s : %s", header, value
        print "Encoding: " + this_response.encoding
        print "Text: " + this_response.text
        try:
            print "Json" + this_response.json()
        except ValueError:
            pass
        logger.debug("Leaving Sentry test login")
        return this_response.status_code

    def get_sentry_info(self):
        """
        return the Sentry info
        {
        "jsonrpc":2.0,
        "method":"Report.GetSentryInfo",
        "params":{"outputType":"json"},
        "id":1
        }
        """
        logger.debug("Entering Get Sentry Info")

        request = """{
                    "jsonrpc":2.0,
                    "method":"Report.GetSentryInfo",
                    "params":{"outputType":"json"},
                    "id":1
                    }"""
        this_response = requests.post(self.requesturl, data=request)

        logger.debug("leaving Get Sentry Info")

        return this_response.text


    def get_program_stats(self,
                          types="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30",
                          fromdate="12/19/18",
                          todate="12/20/18",
                          fromtime="06:00:00 PM",
                          totime="12:00:00 AM"):
        """
        Get Stats - Pull statistics for specific time period, can do multiple reports of a duration

        Variables:
        types - KPI types
        fromDate - date to start
        todate - date to end
        fromtime - time to start
        totime - time to end
        reportDuration - duration to report on
        """
        logger.debug("Entering get_program_stats")
        request = '''{{
            "id":1,
            "jsonrpc":2.0,
            "method":"Report.GetProgramStatistics",
                    "params":{{
                    "outputType":"json",
                    "fromDate":"{0!s}",
                    "fromTime":"{1!s}",
                    "toDate":"{2!s}",
                    "toTime":"{3!s}",
                    "types":[{4!s}],
                    "availabilityProduct":"sentry"}}
        }}'''.format(fromdate, fromtime, todate, totime, types)
        logger.debug(request)
        '''need to make sure the request is good
           and check for an early request
        '''
        while True:
            this_response = requests.post(self.requesturl, data=request)

            sentryUtils.log_response(this_response)
            stats_load = json.loads(this_response.text)
            if stats_load.has_key('result'):
                return stats_load['result']
            elif stats_load.has_key('code'):
                if str(stats_load["code"]) == "-32000": #code -32000 is an early request
                    print "Made a request too fast waiting a minute"
                    logger.debug("code: {0!s}".format(stats_load["code"]))
                    logger.debug("text: {0!s}".format(stats_load["message"]))
                    sleep(STATS_SLEEP_TIME)
                else:
                    raise Exception("Bad response from Sentry {0!s}".format(this_response.text))
            else:
                print "error: {0!s}".format(this_response.text)

        


    
    def UpdateMPEGInput(self, UpdateMPEG, BreakNumber = 20):
        '''{
            "jsonrpc":2.0,"method":"Input.UpdateMPEGInput","params":
            {"inputType":"json","inputSettings":[{"sentryName":"Name or IP",
            "portnum":13,"sourceIp":"*","groupAddr":"225.215.1.5","destPort":8000,
            "name":"Port 13","desc":"My port 13","monitorBackup":false,
            "backupSourceIp":"*","backupGroupAddr":"225.215.2.1","backupDestPort":8001,
            "vlanId":1069,"mode":"Multicast"}]},"id":1}'''

        '''
        {"ver":"1.0","jsonrpc":"2.0","code":-32602,"message":"sentryName is a required parameter.","data":null,"cnt":null}
        {"ver":"1.0","jsonrpc":"2.0","id":1,"result":[{"region":"PA","location":"Danville","display_name":"sentry3",
            "ip_addr":"10.0.1.14","unit_name":"sentry3","Error":"Port 1155, 1156, 1157, 1158, 1159 are out of the range.","System ID":4}]}
        
        {"ver":"1.0","jsonrpc":"2.0","id":1,"result":[{"region":"PA","location":"Danville","display_name":"sentry3",
            "ip_addr":"10.0.1.14","unit_name":"sentry3","response":{"resultCode":"200","resultMsg":"Success"},"System ID":4}]}
        '''
        logger.debug("Entering UpdateMPEGInput")
        InputSettings = ''
        for num, port in enumerate(UpdateMPEG, start=1):
            InputSettings += str(json.dumps(port))
            if num % BreakNumber == 0 or num == len(UpdateMPEG):
                print InputSettings
                request = '''{{"jsonrpc":2.0,
                    "method":"Input.UpdateMPEGInput",
                    "params":
                    {{"inputType":"json",
                    "inputSettings":
                    [{0!s}]}},"id":1}}'''.format(str(InputSettings))
                this_response = requests.post(self.requesturl, data=request)
                sentryUtils.log_response(this_response)
                '''if stats_load.has_key('result'):
                    return stats_load['result']
                else:
                        raise Exception("Bad response from Sentry {0!s}".format(this_response.text))
                else:
                    print "error: {0!s}".format(this_response.text)'''
                InputSettings = ''
            else:
                InputSettings += ','

        logger.debug("Leaving UpdateMPEGInput")


        '''
        '''
        
        
        
        
        
        
        
        
        
        '''while True:
            this_response = requests.post(self.requesturl, data=request)
                
            sentryUtils.log_response(this_response)
            stats_load = json.loads(this_response.text)
            try:
                return stats_load['result']
            except KeyError as error:
                #print "error: {0!s}".format(error)
                #print stats_load["code"]
                try:
                    if str(stats_load["code"]) == "-32000": #code -32000 is an early request
                        print "Made a request too fast waiting a minute"
                        logger.debug("code: {0!s}".format(stats_load["code"]))
                        logger.debug("text: {0!s}".format(stats_load["message"]))
                        sleep(STATS_SLEEP_TIME)
                    else:
                        raise Exception("Bad response from Sentry {0!s}".format(this_response.text))
                except error:
                    print "error: {0!s}".format(e)'''
