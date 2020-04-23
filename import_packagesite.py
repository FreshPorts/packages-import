#!/usr/local/bin/python

# fetch and import the trees which need to be updated.

import re
import yaml
import io
import sys
import psycopg2
import psycopg2.extras

import os
from pprint import pprint

from psycopg2.extensions import adapt

import configparser # for config.ini parsing

config = configparser.ConfigParser()
config.read('/usr/local/etc/freshports/config.ini')

SCRIPT_DIR = config['filesystem']['SCRIPT_DIR']

DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])

PKG_SITE_DIR = config['filesystem']['PACKAGE_IMPORT_DIR']

dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# for updating the rows
cursUpdate = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

curs.callproc('PackagesGetReposNeedingImports')
NumRows = curs.rowcount
dbh.commit();
if (NumRows > 0):
  print("we have " + str(NumRows) + " to process");
  rows = curs.fetchall()
  for row in rows:
    abi_name    = row['abi_name']
    package_set = row['package_set']
    print(abi_name + '/' + package_set);

    # First, we delete any existing values for this ABI/set combintation. We don't want duplicates on the import
    cursUpdate.callproc('PackagesRawDeleteForABIPackageSet', (abi_name, package_set))

    # the script name needs a space before the first parameter
    # when importing, this script will do a commit if it succeeds.
    command = SCRIPT_DIR + "/fetch-extract-parse-import-one-abi.sh " + abi_name + " " + package_set
    
    print("command is: " + command);
    result = os.popen(command).readlines()

    # we trim to avoid the trailing newline
    print(result)
    if result != [] and result[0].strip() == 'Done':
      # now we update the last_checked and repo_date in the packages_last_checked table
      cursUpdate.callproc('PackagesLastCheckedSetImportDate', (abi_name, package_set))
      dbh.commit();
    else:
       pprint(result)
       sys.exit("something went wrong with the os.popen")

    # safe thing to do here
    dbh.rollback();

dbh.rollback();
dbh.close();
