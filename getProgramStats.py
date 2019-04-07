#!/usr/bin/env python
'''
Created on Jan 3 2019

@author: Patrick Rosini
'''

import argparse
import logging
import json
#import prometheus_client
import sentryConnection
import datetime
from sentryLogging import logger
from psycopg2.extensions import AsIs
from time import sleep
import psycopg2

"""
    python getProgramStats.py --system demo.vnm.tek.com:9015 --user Administrator --pass none!! --duration "1 Minute"
    port_number: 3010
    port_name: Port 3010
    transport_number: 1
    program_number: 2
    program_name: Weerkanaal redundant
    video_format: MPEG-2
    primary_video_pid_number: 33
    audio_mode: BS.1770-3\/3 sec
    port_info: 225.21.11.1:8000
    port_source_info: *
    device_info: LAN 2
    rpt_start_date_yyyymmdd: 20190206
    rpt_start_time: 11:19:57-08:00
    rpt_end_date_yyyymmdd: 20190206
    rpt_end_time: 12:19:57-08:00
    scrambled: N
    used_backup: N

    hd_flag: SD

    average_video_quality: 91.2916
    max_video_quality: 100
    min_video_quality: 5

    min_idr:
    avg_idr:
    max_idr:
    min_ebp:
    avg_ebp:
    max_ebp:

    primary_audio_pid_number: 34
    audio_pid_lang: eng
    audio_format: MPEG-1 Layer II
    average_audio_quality: 96.7085
    max_audio_quality: 100
    min_audio_quality: 41
    average_volume_level: -24.7768
    max_volume_level: -13.7481
    min_volume_level: -73.1743
    average_dialnorm:
    distance_from_dialnorm:

    audio_pid_number_2nd:
    audio_pid_lang_2nd:
    audio_format_2nd:
    avg_aqoe_2nd:
    min_aqoe_2nd:
    max_aqoe_2nd:
    avg_volume_lvl_2nd:
    max_volume_lvl_2nd:
    min_volume_lvl_2nd:
    avg_dialnorm_2nd:
    dist_from_dialnorm_2nd:

    average_bitrate: 5291865.2303
    min_bitrate: 76627.0000
    max_bitrate: 5384871.0000

    discontinuity_count: 0

    average_gop_length: 12.00
    min_gop_length: 3
    max_gop_length: 20

    min_perceptual_video_quality: 
    average_perceptual_video_quality: 
    max_perceptual_video_quality: 

    availability_percent: 74.777778
    error_seconds: 908

    ad_cue_out_events: 0

    closed_caption_percent: 0.0000
    cc_error_pct: 0.0000
    cc_valid_pct: 0.0000
    cc_608_pct: 0.0000
    cc_608_error_pct: 0.0000
    cc_608_valid_pct: 0.0000
    cc_708_pct: 0.0000
    cc_708_error_pct: 0.0000
    cc_708_valid_pct: 0.0000
    cc_scte_pct: 0.0000
    cc_scte_error_pct: 0.0000
    cc_scte_valid_pct: 0.0000

    rep_index:
    manifest_bitrate:
    avg_frag_duration:
    min_frag_size:
    avg_frag_size:
    max_frag_size:

    min_frag_load_time:
    avg_frag_load_time:
    max_frag_load_time:

    min_frag_load_bitrate:
    avg_frag_load_bitrate:
    max_frag_load_bitrate:

    min_frag_load_latency:
    avg_frag_load_latency:
    max_frag_load_latency:

    frag_httpstat_100:
    frag_httpstat_200:
    frag_httpstat_300:
    frag_httpstat_400:
    frag_httpstat_500:
    frag_httpstat_600:

    >  --name graphite\
>  --restart=always\
>  -p 80:80\
>  -p 2003-2004:2003-2004\
>  -p 2023-2024:2023-2024\
>  -p 8125:8125/udp\
>  -p 8126:8126\
>  graphiteapp/graphite-statsd
labels=['port_number','port_name','transport_number', 'program_number','program_name','port_info','port_source_info','device_info']

"""

STATS_SLEEP_TIME = 60  # Time to wait between requests



def process_json(data, Sentry):
    try:
        conn = psycopg2.connect("dbname='sentry' user='postgres' host='172.16.17.140'")

        cur = conn.cursor()
        for row in data:
            row['sentry_ip'] = Sentry
            row['rpt_start'] = "{0!s} {1!s}".format(row['rpt_start_date_yyyymmdd'], row['rpt_start_time'])
            row['rpt_end'] = "{0!s} {1!s}".format(row['rpt_end_date_yyyymmdd'], row['rpt_end_time'])
            del row['rpt_start_date_yyyymmdd']
            del row['rpt_start_time']
            del row['rpt_end_date_yyyymmdd']
            del row['rpt_end_time']
            row['url'] = '''http://{0!s}/index.php?page=program_detail&port={1!s}&tsid={2!s}\
                            &program={3!s}&range_type=span&span=1+hour&bl=1'''.format(row['sentry_ip'],
                                                                                    row['port_number'],
                                                                                    row['transport_number'],
                                                                                    row['program_number'])
            fixed_rows = {k: v for k, v in row.items() if v != ''}
            columns = fixed_rows.keys()
            values = [fixed_rows[column] for column in columns]

            insert_statement = 'insert into program_data_time (%s) values %s'
            #print row
            #print fixed_rows
            cur.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values)))
            cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
            conn.commit()
        if(conn):
            cur.close()
            conn.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        if(conn):
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")



def main():
    '''
    main function
    '''
    logger.debug("Entering Get program stats Main")
    parser = argparse.ArgumentParser(description='Import new settings', add_help=True)
    parser.add_argument('--system', '-s', dest='system', help='URL of Sentry/s', required=True)
    parser.add_argument('--user', '-u', dest='userName', help='userName for login', required=True)
    parser.add_argument('--pass', '-p', dest='password', help='password for login', required=True)
    parser.add_argument('--duration', '-D', dest='duration', help='length of reports in seconds', required=True)


    results = parser.parse_args()

    sentrys = []
    nextStartTime = datetime.datetime.now() + datetime.timedelta(seconds = STATS_SLEEP_TIME)

    for item in results.system.split(','):
        sentrys.append(sentryConnection.Sentry(tekip=(item.strip()),
                                               medius=False,
                                               user=results.userName,
                                               passwd=results.password))
    while True:
        end = datetime.datetime.now() - datetime.timedelta(hours=3)
        start = end - datetime.timedelta(seconds=STATS_SLEEP_TIME)
        for Sentry in sentrys:
            print ("Doing Sentry: {0!s} Start: {1!s} End:{2!s}".format(Sentry.tekip,
                                start.isoformat(), end.isoformat()))
            # Get the stats, this will return JSON
            #try:
            stats_load = Sentry.get_program_stats(
                        types="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24",
                        fromdate=start.date(),
                        todate=end.date(),
                        fromtime=start.strftime('%H:%M:00'),
                        totime=end.strftime('%H:%M:00'))
            #stats_load = (Sentry.get_program_stats_span(span="1 minute"))
            #logger.debug(stats_load)
            #print stats_load
            process_json(stats_load, Sentry.tekip)

            #except:
            #    print "Cannot connect to {0!s}".format(Sentry.tekip)
            #for key, value in stats_load[0].items():
            #    print key, value

        
        logger.debug("leaving Get program stats Main")
        if nextStartTime > datetime.datetime.now():
            delta = nextStartTime - datetime.datetime.now()
            sleep(delta.seconds)



if __name__ == '__main__':
    main()

