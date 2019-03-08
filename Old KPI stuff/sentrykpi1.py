#!/usr/bin/env python
'''
Created on Dec 15 2014

@author: Patrick Rosini
'''

import logging
from datetime import datetime,timedelta
from collections import OrderedDict,defaultdict



logger = logging.getLogger(__name__)
#create console handler and set level to debug
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
#create formatter
formatter = logging.Formatter('%(levelname)-8s: %(module)-12s %(lineno)4d: %(message)s')
#add formatter to ch
ch.setFormatter(formatter)
#add ch to logger
logger.addHandler(ch)


class sentry(object):
    """
    Class to connect to Sentry
    """

    def __init__(self,
                 sentryIP="",
                 page="login",
                 _z="0",
                 static="1",
                 username="",
                 passwd="",
                 submit=' Log In '):
        """
        Initilize the connection to the Sentry

        Arguiments:
        Logon data
        sentryIP - URL to sentry
        page - Initial page
        _z=0 - 
        username - login
        passwd - password
        submit 


        """

        logger.debug("Entering Init")
        self.sentryIP=sentryIP
        self.page=page
        self._z=_z
        self.static=static
        self.username=username
        self.passwd=passwd
        self.submit=submit
        self.requestLogin() #log into Sentry or Medius
        self.loadTimeGraphData = OrderedDict() # data for graph
        self.data = defaultdict(lambda: []) #
        self.labels = []
        logger.debug("leaving Init")

    def requestLogin(self):
        """
        Do login
        Requests session will keep login cookie
        """
        import requests #request package will have to be installed, does HTTP requests

        logger.debug("Entering requestLogin")
        self.requestSession = requests.Session()
        loginData = {'page' : self.page,
                        '_z' : self._z,
                        'static' : self.static,
                        'username' : self.username,
                        'passwd' : self.passwd,
                        'submit' : self.submit}
        r = self.requestSession.post(self.sentryIP + "/index.php", loginData)


        logger.debug("Leaving requestLogin")

    def getStats(self,
                 types="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30", #get everything
                 #types="1,2,3,4,5,6,7,8,9,10", #get everything
                 fromdate="01/11/15",
                 todate=None,
                 fromtime="01:00:00 PM",
                 totime="03:00:00 PM",
                 preview="0",
                 streamcsv="1",
                 reportDuration=None,
                 dst_page='kpi1'):
        """
        Get Stats - Pull statistics for specific time period

        Variables:
        types - KPI types
        fromDate - date to start
        todate - date to end
        fromtime - time to sart
        totime - time to end
        preview - 
        streamcsv - 
        """
        from datetime import datetime,timedelta
        from time import sleep

        logger.debug("Entering getStats")

        startDateTime = systemDateTime(fromdate,fromtime) #convert dates and times
        if not reportDuration:
            if not todate:
                todate = fromdate #if no end date is passed, default to the same day
            endDateTime = systemDateTime(todate,totime)
        else:
            endDateTime = startDateTime + timedelta(seconds = reportDuration)
        logger.debug("Start Date/Time: {0} {1}/End Date/Time: {2} {3}".format(sentryDate(startDateTime),
                                                                        sentryTime(startDateTime),
                                                                        sentryDate(endDateTime),
                                                                        sentryTime(endDateTime)))
        requestData={"types" : types,
                 "fromdate" : sentryDate(startDateTime), #convert timestamp back
                 "todate" : sentryDate(endDateTime),
                 "fromtime" : sentryTime(startDateTime),
                 "totime" : sentryTime(endDateTime),
                 "preview" : preview,
                 "streamcsv" : streamcsv}


        while True:
            r = self.requestSession.post(self.sentryIP + "/index.php?page=" + dst_page, requestData)
            self.labels.append(sentryTime(startDateTime)) #labels for graph, this is a bad place for this
            if "With your current request parameters, you must wait until " in r.text:
                print r.text
                print "waiting a minute to run report"
                sleep(61)
		print "retrying"
            else:
                break
        logger.debug("Leaving getStat")
        return r.text


    def  __repr__(self):
        """
        Print out the variables and values stored in the object
        
        Return:
        The variables and values
        
        """
        
        #logger.info("Entering repr")
        to_return = ""
        for key, value in self.__dict__.items():
            if value != None:
                to_return += "%s = %s\n" % (key,value)
        #logger.info("Leaving repr")
        return to_return

class getReportskpi1(object):

    def __init__(self,startDate="04/05/15",
             startTime="12:00:00 AM",
             endDate="04/11/15",
             endTime="12:01:00 AM",
             reportDuration=43200):
        """
        init - Initilize get reports object
        startDate - Date to start reporting
             startTime - Time to start reporting
             endDate - Date to start reporting
             endTime - Time to start reporting
             reportDuration - length of each report in seconds


        """
        logger.debug("Entering getReportskpi1 Init")
        self.reportDuration = reportDuration
        self.startDateTime = systemDateTime(startDate,startTime)
        if not endDate:
            endDate = startDate
        self.endDateTime = systemDateTime(endDate,endTime)

        logger.debug(self.startDateTime)
        logger.debug(self.endDateTime)


        logger.debug("Leaving getReportskpi1 Init")

def sentryDate(date,xmlFormat=False):
    """
    convert date to format needed by sentry
    """
    if xmlFormat:
        # '20150111,13:20:00-05'
        return datetime.strptime(date,'%Y%m%d').strftime('%m/%d/%y')
    else:
        return date.strftime('%m/%d/%y')

def sentryTime(time,xmlFormat=False):
    """
    convert time to format needed by sentry
    """
    if xmlFormat:
        # '20150111,13:20:00-05'
        return datetime.strptime(time[:-3],'%H:%M:%S').strftime('%I:%M:%S %p')
    else:
        return time.strftime('%I:%M:%S %p')

def systemDateTime(date,time = '',xmlFormat=False):
    """
    convert date/time to format needed by system
    """
    if xmlFormat:
        # '20150111,13:20:00-05'
        return datetime.strptime(date + " " + time[:-3],'%Y%m%d %H:%M:%S')
    if time:
        return datetime.strptime(date + " " + time,'%m/%d/%y %I:%M:%S %p')
    else:
        return datetime.strptime(date,'%m/%d/%y %I:%M:%S %p')



def processCSV(csvString):
    """
    Create a DICT from each line of the returned data and iterate over it

    """
    import csv
    reader = csv.DictReader(csvString.splitlines()[1:-1]) #create dict of the returned data, drop the first and last line
    for row in reader:
        yield row

def dateRange( startDate, endDate, stepDuration ):
    """
    Iterate over date range
    Variables
    startDate - datetime to start
    endDate - datetime to stop
    stepDuration - Duration of the step in seconds


    """
    from datetime import timedelta
    logger.debug("Entering dateRange: StartDate:{0} EndDate:{1} stepDuration:{2}".format(startDate, endDate, stepDuration))

    if startDate <= endDate:
         for n in range( 0,int(( endDate - startDate ).total_seconds()), stepDuration ):
            yield startDate + timedelta( seconds = n )
    else:
        for n in range( 0,int(( startDate - endDate ).total_seconds()), stepDuration ):
            yield startDate - timedelta( seconds = n )




if __name__ == '__main__':
    sentry = sentry()
    print sentry
    test = sentry.getStats()
    print test
    
    """for row in processCSV(test):
        sentry.buildGraphData(row)
    print sentry.loadTimeGraphData"""

