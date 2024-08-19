#!/usr/local/bin/python

# Update the packages_raw table with port_id and abi_id
# Then update the packages tables from packages_raw

import psycopg2
import psycopg2.extras
import configparser # for config.ini parsing
import re           # for escaping the database passwords
import syslog       # for logging

from pathlib import Path  # for touching the signal file

import os


syslog.openlog(ident=os.path.basename(__file__), facility=syslog.LOG_LOCAL3)
syslog.syslog(syslog.LOG_NOTICE, 'Starting up')

config = configparser.ConfigParser()
config.read('/usr/local/etc/freshports/config.ini')

SCRIPT_DIR = config['filesystem']['SCRIPT_DIR']

DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD']) + ' sslcertmode=disable'

dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# for updating the rows
cursUpdate = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# before we start, delete the existing package notifications.

curs.execute("truncate package_notifications;")

curs.execute("SELECT * from PackagesGetImportedReposNeedingProcessing()")
NumRows = curs.rowcount
if (NumRows > 0):
  rows = curs.fetchall()
  for row in rows:
    syslog.syslog(syslog.LOG_NOTICE, 'updating packages table for ' + row['abi_name'] + '/' + row['package_set']);

    cursUpdate.execute("BEGIN");
    cursUpdate.callproc('UpdatePackagesFromRawPackages', (row['abi_name'],row['package_set']))
    # I'm not sure how to properly check the return value so,
    # be sure to terminate this transaction one way or another
    cursUpdate.execute("COMMIT");
    cursUpdate.execute("ROLLBACK");

cursUpdate.execute("ROLLBACK");

if NumRows > 0:
  # set the flag for job-waiting.pl
  syslog.syslog(syslog.LOG_NOTICE, 'There were ' + str(NumRows) + ' repos updated in packages.')

  # this will prompt the front ends to clear their package caches
  cursUpdate.execute("NOTIFY packages_imported")
else:
  syslog.syslog(syslog.LOG_NOTICE, 'There were no packages to update.  I should never be called like this.  It is such an inconvenience.  Have you no shame?')

dbh.close();

syslog.syslog(syslog.LOG_NOTICE, 'Finishing')
