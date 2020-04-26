#!/usr/local/bin/python

# check the repos for new build


import psycopg2
import psycopg2.extras
import configparser # for config.ini parsing
import re           # for escaping the database passwords
import syslog       # for logging

from pathlib import Path  # for touching the signal file

import os
import sys



syslog.openlog(ident=os.path.basename(__file__), facility=syslog.LOG_LOCAL3)
syslog.syslog(syslog.LOG_NOTICE, 'Starting up')

config = configparser.ConfigParser()
config.read('/usr/local/etc/freshports/config.ini')

SCRIPT_DIR = config['filesystem']['SCRIPT_DIR']

DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])

SIGNAL_NEW_REPO_READY_FOR_IMPORT = config['filesystem']['SIGNAL_NEW_REPO_READY_FOR_IMPORT']
SIGNAL_JOB_WAITING               = config['filesystem']['SIGNAL_JOB_WAITING']

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

    syslog.syslog(syslog.LOG_NOTICE, 'checking: ' + row['abi_name'] + '/' + row['package_set'] + ' : ' + str(repo_date or ""))
      
    # now we update the last_checked and repo_date in the packages_last_checked table
    # PackagesLastCheckedSetRepoDate(a_abi_name text, a_package_set text, a_CheckedDate text)    
    cursUpdate.callproc('PackagesLastCheckedSetRepoDate', (row['abi_name'],row['package_set'], repo_date))
    retval = cursUpdate.fetchone()[0]
    if retval == 1:
      ReposNeedImporting.append(row['abi_name'] + '/' + row['package_set'] + ' : ' + repo_date)

dbh.commit();
dbh.close();

if len(ReposNeedImporting) > 0:
  # set the flag for job-waiting.pl
  Path(SIGNAL_NEW_REPO_READY_FOR_IMPORT).touch()
  Path(SIGNAL_JOB_WAITING).touch()
  syslog.syslog(syslog.LOG_NOTICE, 'There are ' + str(len(ReposNeedImporting)) + ' new repos ready for import: ' + str(ReposNeedImporting))
else:
  syslog.syslog(syslog.LOG_NOTICE, 'No repos need importing')

syslog.syslog(syslog.LOG_NOTICE, 'finishes');
