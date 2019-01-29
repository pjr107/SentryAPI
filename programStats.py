#!/usr/bin/env python
'''
Created on Aug 13 2018

@author: Patrick Rosini
'''

from sentryLogging import logger
from datetime import datetime, timedelta

logger.debug("Entering Sentry Utils")




def main():
    import argparse
    import sentryConnection
    import sentryUtils
    from datetime import datetime, timedelta
    import sys
    from xml.sax.saxutils import escape
    import codecs
    from time import sleep
    import json
    import csv

    sys.stdout = codecs.getwriter('utf8')(sys.stdout)


    logger.debug("Entering Main")


    one_day = timedelta(days=1)
    header = False
    parser = argparse.ArgumentParser(description='Genrate reports from Sentry/Medius',add_help=True)
    parser.add_argument('--startDate' ,'-d',dest='startDate',help='date/time to start reporting period mm/dd/yy hh:mm:ss PM',required=True)
    parser.add_argument('--endDate' ,'-e',dest='endDate',help='date/time to end reporting period mm/dd/yy hh:mm:ss PM',required=True)
    parser.add_argument('--duration' ,'-D',dest='duration',help='length of reports in seconds',required=True)
    parser.add_argument('--system' ,'-s',dest='system',help='URL of Sentry or Medius',required=True)
    parser.add_argument('--userName' ,'-u',dest='userName',help='userName for login',required=True)
    parser.add_argument('--password' ,'-p',dest='password',help='password for login',required=True)
    parser.add_argument('--output', '-o',dest='outFile',help='file for output',default=(datetime.today()-one_day).strftime('%d%b%Y')+'.csv')

    results = parser.parse_args()

    Sentry = sentryConnection.Sentry(tekip=results.system,
                    medius=False,
                    user=results.userName,
                    passwd=results.password)
    #print Sentry.get_sentry_info()




    # make real dates
    try:
        systemStartDate = sentryUtils.systemDateTime(results.startDate)
        systemEndDate = sentryUtils.systemDateTime(results.endDate)
    except Exception, e:
        print "invalid dates, they should be in for format mm/dd/yy hh:mm:ss PM, {0}".format(e)
        sys.exit(1)
    print 'Start Report: {0}/ End Report: {1}'.format(systemStartDate,systemEndDate)

    try:
        fileToWrite = open(results.outFile, 'wb')
        logger.debug("opened file {0}".format(results.outFile))
    except Exception, e:
        print "can't open file {0}".format(e)
        sys.exit(1)

    startDate = sentryUtils.sentryDate(systemStartDate)
    startTime = sentryUtils.sentryTime(systemStartDate)
    endDate = sentryUtils.sentryDate(systemEndDate)
    endTime = sentryUtils.sentryTime(systemEndDate)
    reportDuration = int(results.duration)

    #print startDate,endDate
    for date in sentryUtils.DateRange(sentryUtils.systemDateTime(startDate,startTime),sentryUtils.systemDateTime(endDate,endTime), int(results.duration)):

        logger.info("Start Date/Time: {0} {1} End Date/Time: {2} {3}".format(sentryUtils.sentryDate(date),
                                                                                sentryUtils.sentryTime(date),
                                                                                sentryUtils.sentryDate(date+timedelta(seconds = reportDuration)),
                                                                                sentryUtils.sentryTime(date+timedelta(seconds = reportDuration))))
        stats = (Sentry.get_program_stats(fromdate=sentryUtils.sentryDate(date),
                                            todate=sentryUtils.sentryDate(date+timedelta(seconds = reportDuration)),
                                            fromtime=sentryUtils.sentryTime(date),
                                            totime=sentryUtils.sentryTime(date+timedelta(seconds = reportDuration)),
                                            types = "3"))
        #for row in stats:
        #    print "row: " + row
        #print stats

        header = {'port_number':1, 'port_name':2, 'transport_number':3, 'program_number':4,\
                     'program_name':5, 'primary_audio_pid_number':6, 'average_volume_level':7, \
                     'max_volume_level':8, 'min_volume_level':9, 'average_dialnorm':10, \
                     'distance_from_dialnorm':11, 'audio_pid_lang':12, 'audio_mode':13, 'audio_format':14, \
                     'used_backup':15, 'port_info':16, 'port_source_info':17, 'device_info':18, \
                     'rpt_start_date_yyyymmdd':19, 'rpt_start_time':20, 'rpt_end_date_yyyymmdd':21, 'rpt_end_time':22}

        statsLoad = json.loads(stats)
        statsLoad = statsLoad['result']
        #print statsLoad
        f = csv.writer(fileToWrite)
        headers = sorted(header, key=header.__getitem__)
        logger.debug(headers)
        f.writerow(headers)
        for row in statsLoad:
            output =  [row[i] for i in sorted(row, key=header.__getitem__)]
            logger.debug(output)
            f.writerow(output)
        '''splitStats = stats.splitlines()
        if not header: # only output header once
            fileToWrite.write(splitStats[1])
	    fileToWrite.write('\n')  #have to write a line
            header = True
        for row in splitStats[2:-1]:
            fileToWrite.write(escape(row.encode('utf8')))
            fileToWrite.write('\n')  #have to write a line
        #print data'''


        sleep(60)
    pass
    




if __name__ == '__main__':
    main()

