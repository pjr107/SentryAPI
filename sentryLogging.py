#!/usr/bin/env python
'''
Created on Aug 13 2018

@author: Patrick Rosini
'''
import logging

logging.basicConfig(filename='debug.txt',
                        filemode='a',
                        formatter='%(levelname)-8s: %(module)-12s %(lineno)4d: %(message)s',
                        level=logging.DEBUG)
logger = logging.getLogger(__name__)
#create console handler and set level to debug
#logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
#create formatter
#formatter = logging.Formatter('%(levelname)-8s: %(module)-12s %(lineno)4d: %(message)s')
#add formatter to ch
#ch.setFormatter(formatter)
#add ch to logger
logger.addHandler(ch)


if __name__ == '__main__':
    logger.debug("Logging main")
    