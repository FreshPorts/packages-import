#!/usr/local/bin/python

import re
import yaml
import io
import sys
import psycopg2
import psycopg2.extras

from pathlib import Path  # for touching the signal file
import syslog             # for logging

import os

from psycopg2.extensions import adapt

import configparser # for config.ini parsing

syslog.openlog(ident=__file__., facility=syslog.LOG_LOCAL3)
syslog.syslog(syslog.LOG_NOTICE, 'Starting up')

config = configparser.ConfigParser()
config.read('/usr/local/etc/freshports/config.ini')

SCRIPT_DIR = config['filesystem']['SCRIPT_DIR']

DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])

SIGNAL_NEW_REPO = config['filesystem']['SIGNAL_NEW_REPO']


dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# for updating the rows
cursUpdate = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# There are no repos to import
ReposNeedImporting = []

curs.execute("SELECT * from GetReposToReview()")
NumRows = curs.rowcount
dbh.commit();
if (NumRows > 0):
  rows = curs.fetchall()
  for row in rows:

    command = SCRIPT_DIR + "/get_packagesite.txz_date " + row['abi_name'] + " " + row['package_set']
    timestamp = os.popen(command).readlines()
    if timestamp == []:
      repo_date = None
    else:
      repo_date = timestamp[0].strip()

    syslog.syslog(syslog.LOG_NOTICE, 'checking: ' + row['abi_name'] + '/' + row['package_set'] + ' : ' + repo_date)
      
    # now we update the last_checked and repo_date in the packages_last_checked table
    # PackagesLastCheckedSetRepoDate(a_abi_name text, a_package_set text, a_CheckedDate text)    
    cursUpdate.callproc('PackagesLastCheckedSetRepoDate', (row['abi_name'],row['package_set'], repo_date))
    retval = cur.fetchone()[0]
    if retval == 1:
      ReposNeedImporting.append(row['abi_name'] + '/' + row['package_set'] + ' : ' + repo_date)

dbh.commit();
dbh.close();

if length(ReposNeedImporting) > 0:
  # set the flag for job-waiting.pl
  Path(SIGNAL_NEW_REPO)
  syslog.syslog(syslog.LOG_NOTICE, 'There are ' + ReposNeedImporting.length() + ' which need importing ' + str(ReposNeedImporting))
else:
  syslog.syslog(syslog.LOG_NOTICE, No )

syslog.syslog(syslog.LOG_NOTICE, 'finishes');
