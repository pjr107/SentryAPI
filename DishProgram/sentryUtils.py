#!/usr/bin/env python
'''
Created on Aug 13 2018

@author: Patrick Rosini
'''

from sentryLogging import logger
from datetime import datetime, timedelta

logger.debug("Entering Sentry Utils")


def log_response(this_response):
    """
    write out all the info in the response from the Sentry/Medius
    """
    logger.debug("Entering log response")
    logger.debug("StatusCode: " + str(this_response.status_code))
    logger.debug("Headers: ")
    for header, value in this_response.headers.items():
        logger.debug("    %s : %s", header, value)
    logger.debug("Encoding: " + this_response.encoding)
    logger.debug("Text: " + this_response.text)
    try:
        logger.debug(this_response.json())
    except ValueError:
        pass
    logger.debug("Leaving log response")

def DateRange(startDate, endDate, stepDuration):
    """
    Iterate over date range
    Variables
    startDate - datetime to start
    endDate - datetime to stop
    stepDuration - Duration of the step in seconds


    """
    logger.debug("Entering dateRange: StartDate:{0} EndDate:{1} stepDuration:{2}".format(startDate, endDate, stepDuration))

    if startDate <= endDate:
        for n in range(0, int((endDate - startDate).total_seconds()), stepDuration):
            yield startDate + timedelta(seconds=n)
    else:
        for n in range(0, int((startDate - endDate).total_seconds()), stepDuration):
            yield startDate - timedelta(seconds=n)


def sentryDate(date, xmlFormat=False):
    """
    convert date to format needed by sentry
    """
    if xmlFormat:
        # '20150111,13:20:00-05'
        return datetime.strptime(date, '%Y%m%d').strftime('%m/%d/%y')
    else:
        return date.strftime('%m/%d/%y')

def sentryTime(time, xmlFormat=False):
    """
    convert time to format needed by sentry
    """
    if xmlFormat:
        # '20150111,13:20:00-05'
        return datetime.strptime(time[:-3], '%H:%M:%S').strftime('%I:%M:%S %p')
    else:
        # 12:00:00 AM
        return time.strftime('%I:%M:%S %p')

def systemDateTime(date, time = '', xmlFormat=False):
    """
    convert date/time to format needed by system
    """
    if xmlFormat:
        # '20150111,13:20:00-05'
        return datetime.strptime(date + " " + time[:-3], '%Y%m%d %H:%M:%S')
    if time:
        return datetime.strptime(date + " " + time, '%m/%d/%y %I:%M:%S %p')
    else:
        try:
            return datetime.strptime(date, '%m/%d/%y %I:%M:%S %p')
        except ValueError:
            one_day = timedelta(days=1)
            return datetime.strptime(datetime.today().strftime('%m/%d/%y')+' ' + date, '%m/%d/%y %I:%M:%S %p') - one_day

