#!/usr/local/bin/python

# fetch and import the trees which need to be updated.


import psycopg2
import psycopg2.extras
import configparser # for config.ini parsing
import re           # for escaping the database passwords
import syslog       # for logging

from pathlib import Path  # for touching the signal file

import os
import sys

from pprint import pprint

syslog.openlog(ident=os.path.basename(__file__), facility=syslog.LOG_LOCAL3)
syslog.syslog(syslog.LOG_NOTICE, 'Starting up')

config = configparser.ConfigParser()
config.read('/usr/local/etc/freshports/config.ini')

SCRIPT_DIR = config['filesystem']['SCRIPT_DIR']

DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD']) + ' sslcertmode=disable'

PKG_SITE_DIR = config['filesystem']['PACKAGE_IMPORT_DIR']

# the flag we will remove
SIGNAL_NEW_REPO_READY_FOR_IMPORT = config['filesystem']['SIGNAL_NEW_REPO_READY_FOR_IMPORT']

# the flags we will set
SIGNAL_NEW_REPO_IMPORTED = config['filesystem']['SIGNAL_NEW_REPO_IMPORTED']

dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# for updating the rows
cursUpdate = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

ImportedRepos = []

curs.callproc('PackagesGetReposNeedingImports')
NumRows = curs.rowcount
dbh.commit();
if (NumRows > 0):
  syslog.syslog(syslog.LOG_NOTICE, "we have " + str(NumRows) + " repos to process");
  rows = curs.fetchall()
  for row in rows:
    abi_name    = row['abi_name']
    package_set = row['package_set']
    syslog.syslog(syslog.LOG_NOTICE, 'importing ' + abi_name + '/' + package_set);

    # First, we delete any existing values for this ABI/set combintation. We don't want duplicates on the import
    cursUpdate.callproc('PackagesRawDeleteForABIPackageSet', (abi_name, package_set))

    # the script name needs a space before the first parameter
    # when importing, this script will do a commit if it succeeds.
    command = SCRIPT_DIR + "/fetch-extract-parse-import-one-abi.sh " + abi_name + " " + package_set
    
    syslog.syslog(syslog.LOG_NOTICE, "command is: " + command);
    result = os.popen(command).readlines()

    # we trim to avoid the trailing newline
    if result != [] and result[0].strip() == 'Done':
      # now we update the last_checked and repo_date in the packages_last_checked table
      syslog.syslog(syslog.LOG_NOTICE, 'calling PackagesLastCheckedSetImportDate()')
      cursUpdate.callproc('PackagesLastCheckedSetImportDate', (abi_name, package_set))
      dbh.commit();
      ImportedRepos.append(abi_name + ":" + package_set)
    else:
      pprint(result)
      syslog.syslog(syslog.LOG_CRIT, 'something went wrong with the os.popen for ' + abi_name + " " + package_set)

    # safe thing to do here
    dbh.rollback();

dbh.rollback();
dbh.close();

# we must always remove this when we finish
Path(SIGNAL_NEW_REPO_READY_FOR_IMPORT).unlink()

if NumRows > 0:
  # set the flag for job-waiting.pl
  Path(SIGNAL_NEW_REPO_IMPORTED).touch()
  syslog.syslog(syslog.LOG_NOTICE, 'There are ' + str(len(ImportedRepos)) + ' repos which need post-import processing: ' + str(ImportedRepos))
else:
  syslog.syslog(syslog.LOG_NOTICE, 'No repos need importing. How did this happen? This should never happen.')

syslog.syslog(syslog.LOG_NOTICE, 'Finishing')
