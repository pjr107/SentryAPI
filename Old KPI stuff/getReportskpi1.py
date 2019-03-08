#!/usr/bin/env python
'''
Created on Apr 16 2015

@author: Patrick Rosini
'''


import logging


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






class my_class(object):
    pass



def main():
    import argparse
    import sentrykpi1
    from datetime import timedelta
    import sys
    from xml.sax.saxutils import escape
    import codecs
    from time import sleep

    sys.stdout = codecs.getwriter('utf8')(sys.stdout)


    logger.debug("Entering Main")
    header = False
    parser = argparse.ArgumentParser(description='Genrate reports from Sentry/Medius',add_help=True)
    parser.add_argument('--startDate' ,'-d',dest='startDate',help='date/time to start reporting period mm/dd/yy hh:mm:ss PM',required=True)
    parser.add_argument('--endDate' ,'-e',dest='endDate',help='date/time to end reporting period mm/dd/yy hh:mm:ss PM',required=True)
    parser.add_argument('--duration' ,'-D',dest='duration',help='length of reports in seconds',required=True)
    parser.add_argument('--system' ,'-s',dest='system',help='URL of Sentry or Medius',required=True)
    parser.add_argument('--userName' ,'-u',dest='userName',help='userName for login',required=True)
    parser.add_argument('--password' ,'-p',dest='password',help='password for login',required=True)
    parser.add_argument('--output', '-o',dest='outFile',help='file for output',required=True)

    results = parser.parse_args()
    # make real dates
    try:
        systemStartDate = sentrykpi1.systemDateTime(results.startDate)
        systemEndDate = sentrykpi1.systemDateTime(results.endDate)
    except Exception, e:
        print "invalid dates, they should be in for format mm/dd/yy hh:mm:ss PM"
        sys.exit(1)
    print 'Start Report: {0}/ End Report: {1}'.format(systemStartDate,systemEndDate)
    try:
        fileToWrite = open(results.outFile, 'wb')
    except Exception, e:
        print "can't open file {0}".format(e)
        sys.exit(1)

    startDate = sentrykpi1.sentryDate(systemStartDate)
    startTime = sentrykpi1.sentryTime(systemStartDate)
    endDate = sentrykpi1.sentryDate(systemEndDate)
    endTime = sentrykpi1.sentryTime(systemEndDate)


    report = sentrykpi1.getReportskpi1(startDate=startDate,
             startTime=startTime,
             endDate=endDate,
             endTime=endTime,
             reportDuration=int(results.duration))


    sentryConnection = sentrykpi1.sentry( sentryIP=results.system,
                         username=results.userName,
                         passwd=results.password)

    print report.startDateTime,report.endDateTime
    for date in sentrykpi1.dateRange(report.startDateTime,report.endDateTime, report.reportDuration):

        logger.info("Start Date/Time: {0} {1}/End Date/Time: {2} {3}".format(sentrykpi1.sentryDate(date),
                                                                                sentrykpi1.sentryTime(date),
                                                                                sentrykpi1.sentryDate(date+timedelta(seconds = report.reportDuration)),
                                                                                sentrykpi1.sentryTime(date+timedelta(seconds = report.reportDuration))))
        stats = sentryConnection.getStats(fromdate=sentrykpi1.sentryDate(date),
                                            todate=sentrykpi1.sentryDate(date+timedelta(seconds = report.reportDuration)),
                                            fromtime=sentrykpi1.sentryTime(date),
                                            totime=sentrykpi1.sentryTime(date+timedelta(seconds = report.reportDuration)),
                                            preview="1",
                                            streamcsv="1") 
        splitStats = stats.splitlines()
        if not header: # only output header once
            fileToWrite.write(splitStats[1])
	    fileToWrite.write('\n')  #have to write a line
            header = True
        for row in splitStats[2:-1]:
            fileToWrite.write(escape(row.encode('utf8')))
            fileToWrite.write('\n')  #have to write a line
        #print data

        sleep(1)

    pass
    



if __name__ == '__main__':
    main()
