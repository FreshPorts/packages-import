#!/usr/local/bin/python

import re    # for escaping the database passwords
#import yaml
#import io
#import sys
import psycopg2
import psycopg2.extras

#import os

#from psycopg2.extensions import adapt

import syslog             # for logging

import configparser # for config.ini parsing

syslog.openlog(ident=__file__., facility=syslog.LOG_LOCAL3)
syslog.syslog(syslog.LOG_NOTICE, 'Starting up')

config = configparser.ConfigParser()
config.read('/usr/local/etc/freshports/config.ini')

SCRIPT_DIR = config['filesystem']['SCRIPT_DIR']

DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])


dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# for updating the rows
cursUpdate = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)


curs.execute("SELECT * from PackagesGetImportedReposNeedingProcessing()")
NumRows = curs.rowcount
if (NumRows > 0):
  rows = curs.fetchall()
  for row in rows:
    syslog.syslog(syslog.LOG_NOTICE, 'checking ' + row['abi_name'] + '/' + row['package_set']);

    cursUpdate.execute("BEGIN");
    cursUpdate.callproc('UpdatePackagesFromRawPackages', (row['abi_name'],row['package_set']))
    # I'm not sure how to properly check the return value so,
    # be sure to terminate this transaction one way or another
    cursUpdate.execute("COMMIT");
    cursUpdate.execute("ROLLBACK");

cursUpdate.execute("ROLLBACK");
dbh.close();

syslog.syslog(syslog.LOG_NOTICE, 'Finishing')
