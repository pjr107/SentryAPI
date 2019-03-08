#!/usr/bin/env python
'''
Created on Aug 13 2018

@author: Patrick Rosini

This will pull the Audio Stats for any time period and return the average
between 00 and 10 minutes past the hour and return a CSV file with the
program and the avarage audio levels

Example output:
program_name,18:10:00-08:00,19:10:00-08:00,20:10:00-08:00,21:10:00-08:00,22:10:00-08:00,23:10:00-08:00
TNT/TBS Slate,N/A,N/A,N/A,N/A,N/A,N/A
1_1 HBO,-30.1574,-30.0968,-29.9265,-30.0425,-30.1678,-30.3842
1_10 VH-1 CLASSICS,-19.9671,-19.9763,-19.875,-19.8572,-20.053,-20.0413
1_2 HBO2,-32.4669,-33.0476,-32.7578,-32.7702,-32.8741,-33.3465
1_3 CMAX,-28.5273,-28.3733,-28.4462,-28.1602,-28.0961,-28.4536
1_4 HBOS,-27.5744,-27.5395,-27.4735,-27.5898,-27.7435,-27.7097
'''

from datetime import datetime, timedelta
import argparse
import sys
#from xml.sax.saxutils import escape
import codecs
from time import sleep #we can only do pregram stats requests once per minute
import sqlite3
import csv
import sentryConnection # Connection to Sentry and implement calls
import sentryUtils # date transform and other things needed
from sentryLogging import logger  #Setup logging in a single file

STATS_SLEEP_TIME = 60  # Time to wait between requests

logger.debug("Entering audio report")

def main():

    sys.stdout = codecs.getwriter('utf8')(sys.stdout)


    logger.debug("Entering Main")


    one_day = timedelta(days=1)
    header = False
    parser = argparse.ArgumentParser(description='Generate reports from Sentry/Medius', add_help=True)
    parser.add_argument('--startDate' ,'-d', dest='startDate', help='date/time to start reporting period mm/dd/yy hh:mm:ss PM', required=True)
    parser.add_argument('--endDate' ,'-e', dest='endDate', help='date/time to end reporting period mm/dd/yy hh:mm:ss PM', required=True)
    parser.add_argument('--duration' ,'-D', dest='duration', help='length of reports in seconds', required=True)
    parser.add_argument('--system' ,'-s', dest='system', help='URL of Sentry or Medius', required=True)
    parser.add_argument('--userName' ,'-u', dest='userName', help='userName for login', required=True)
    parser.add_argument('--password' ,'-p', dest='password', help='password for login', required=True)
    parser.add_argument('--output', '-o', dest='outFile', help='file for output', default=(datetime.today()-one_day).strftime('%d%b%Y'))
    parser.add_argument('--endmin' ,'-m', dest='endMin', help='End minute to filter results on', default='20')

    results = parser.parse_args()


    sentrys = []

    for item in results.system.split(','):
        sentrys.append(sentryConnection.Sentry(tekip=(item.strip()),
                        medius=False,
                        user=results.userName,
                        passwd=results.password))

    # make real dates
    try:
        system_start_date = sentryUtils.systemDateTime(results.startDate)
        system_end_date = sentryUtils.systemDateTime(results.endDate)
    except Exception, e:
        print "invalid dates, they should be in for format mm/dd/yy hh:mm:ss PM, {0}".format(e)
        sys.exit(1)
    print 'Start Report: {0}/ End Report: {1}'.format(system_start_date, system_end_date)

    # Use sqlite to save the data in the format needed
    try:
        connection = sqlite3.connect(results.outFile + '.db')
        cur = connection.cursor()
        logger.debug("opened file {0}".format(results.outFile))
    except Exception, e:
        print "can't open file {0}".format(e)
        sys.exit(1)
    cur.execute('CREATE TABLE IF NOT EXISTS audio_data (program_name PRIMARY KEY)')
    connection.commit()

    start_date = sentryUtils.sentryDate(system_start_date)
    start_time = sentryUtils.sentryTime(system_start_date)
    end_date = sentryUtils.sentryDate(system_end_date)
    end_time = sentryUtils.sentryTime(system_end_date)
    report_duration = int(results.duration)

    #print startDate,endDate
    for date in sentryUtils.DateRange(sentryUtils.systemDateTime(start_date,start_time),sentryUtils.systemDateTime(end_date,end_time), int(results.duration)):
        if str(sentryUtils.sentryTime(date+timedelta(seconds=report_duration))).find(results.endMin, 3) == 3:
            #print str(sentryUtils.sentryTime(date+timedelta(seconds=report_duration)))
            # This will only do 10 after
            print(
                "Start Date/Time: {0} {1} End Date/Time: {2} {3}".format(
                                                sentryUtils.sentryDate(date),
                                                sentryUtils.sentryTime(date),
                                                sentryUtils.sentryDate(date+timedelta(seconds=report_duration)),
                                                sentryUtils.sentryTime(date+timedelta(seconds=report_duration))))
            for Sentry in sentrys:
                print("Doing Sentry: {0!s}".format(Sentry.tekip))
                # Get the stats, this will return JSON
                try:
                    stats_load = (Sentry.get_program_stats(fromdate=sentryUtils.sentryDate(date),
                                                    todate=sentryUtils.sentryDate(date+timedelta(seconds=report_duration)),
                                                    fromtime=sentryUtils.sentryTime(date),
                                                    totime=sentryUtils.sentryTime(date+timedelta(seconds=report_duration)),
                                                    types = "3"))

                    # We are going to add new colums to the table needs to be wraped in a try because we can only add it once
                    column_name = "{0!s} to {1!s}".format(stats_load[0]['rpt_start_time'][:8], stats_load[0]['rpt_end_time'][:8])
                    sql = 'ALTER TABLE audio_data ADD COLUMN "{0!s}"'.format(column_name)
                    try:
                        cur.execute(sql)
                    except:
                        pass
                    # Write the avarage audio level 
                    for row in stats_load:
                        # if nothing was returned make the value N/A
                        if not row['average_volume_level']:
                            row['average_volume_level'] = '"N/A"'
                        # if the program name does not exist add it with the avarage volume
                        # if it already exists just update the row
                        sql1 = '''INSERT OR IGNORE INTO audio_data (program_name, "{0!s}")
                                VALUES ("{1!s}",{2!s})'''.format(column_name,
                                row['program_name'], row['average_volume_level'])
                        sql2 = '''UPDATE audio_data SET "{0!s}" = {1!s}
                                WHERE program_name = "{2!s}"'''.format(column_name,
                                row['average_volume_level'], row['program_name'])
                        cur.execute(sql1)
                        cur.execute(sql2)
                except:
                    print "Cannot connect to {0!s}".format(Sentry.tekip)
                    pass
                connection.commit()
            # wait the minute to make the next request
            sleep(STATS_SLEEP_TIME)
        else: 
            print(
            "Skipping: Start Date/Time: {0} {1} End Date/Time: {2} {3}".format(
                                            sentryUtils.sentryDate(date),
                                            sentryUtils.sentryTime(date),
                                            sentryUtils.sentryDate(date+timedelta(seconds=report_duration)),
                                            sentryUtils.sentryTime(date+timedelta(seconds=report_duration))))
    pass

    # Write the sqlite to a CSV file
    with open(results.outFile + ".csv", "wb+") as f:
        csvWriter = csv.writer(f)
        rows = cur.execute("SELECT * FROM audio_data")
        header = ''
        for x in cur.description:
            header += x[0] + ','
        #print header
        f.write(header[:-1] + '\n')
        for row in rows:
            csvWriter.writerow(row)
        #print cur.description
    connection.close()




if __name__ == '__main__':
    main()
