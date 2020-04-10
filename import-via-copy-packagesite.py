#!/usr/local/bin/python

import re
#import yaml
#import io
#import sys
import psycopg2
import psycopg2.extras

from psycopg2.extensions import adapt

import configparser # for config.ini parsing

ABI = 'FreeBSD:12:amd64'


config = configparser.ConfigParser()
config.read('/usr/local/etc/freshports/config.ini')


DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])


dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)


curs.execute("select freshports_branch_set('head')")


with open('csv', 'r') as f:
    curs.copy_from(f, 'packages_raw', sep = '\t', columns = ['abi_id', 'package_origin', 'package_name', 'package_version'] )

dbh.commit()
dbh.close();
