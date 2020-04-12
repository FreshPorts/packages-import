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


DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])

PKG_SITE_DIR = config['filesystem']['PACKAGE_IMPORT_DIR']

dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# for updating the rows
cursUpdate = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# what needs to be updated?
curs.execute('select * from PackagesGetReposNeedingUpdates() ORDER BY abi_name, branch')
NumRows = curs.rowcount
dbh.commit();
if (NumRows > 0):
  print("we have " + str(NumRows) + " to process");
  rows = curs.fetchall()
  for row in rows:
    print(row['abi_name'] + '/' + row['branch']);

    # the script name needs a space before the first parameter
    command = "/usr/home/dan/src/packages-import/fetch-extract-parse-import-one-abi.sh " + row['abi_name'] + " " + row['branch']
    
    print("command is: " + command);
    result = os.popen(command).readlines()

    # we trim to avoid the trailing newline
    print(result)
    if result != [] and result[0].strip() == 'Done':
      # now we update the last_checked and repo_date in the packages_last_checked table
      # PackagesLastCheckedSetRepoDate(a_abi_name text, a_branch_name text, a_CheckedDate text)    
      cursUpdate.callproc('PackagesLastCheckedSetImportDate', (row['abi_name'], row['branch']))
      dbh.commit();
#      sys.exit("that went well!")
    else:
       pprint(result)
       sys.exit("something went wrong with the os.popen")

dbh.rollback();
dbh.close();
