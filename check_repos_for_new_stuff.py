#!/usr/local/bin/python

import re
import yaml
import io
import sys
import psycopg2
import psycopg2.extras

import os

from psycopg2.extensions import adapt

import configparser # for config.ini parsing

config = configparser.ConfigParser()
config.read('/usr/local/etc/freshports/config.ini')

SCRIPT_DIR = config['filesystem']['SCRIPT_DIR']

DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])


dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

# for updating the rows
cursUpdate = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)


curs.execute("SELECT * from GetReposToReview()")
NumRows = curs.rowcount
dbh.commit();
if (NumRows > 0):
  rows = curs.fetchall()
  for row in rows:
    print(row['abi_name'] + '/' + row['package_set']);

    command = SCRIPT_DIR + "/get_packagesite.txz_date " + row['abi_name'] + " " + row['package_set']
    timestamp = os.popen(command).readlines()
    if timestamp == []:
      repo_date = None
    else:
      repo_date = timestamp[0].strip()

    print(repo_date)
      
    # now we update the last_checked and repo_date in the packages_last_checked table
    # PackagesLastCheckedSetRepoDate(a_abi_name text, a_package_set text, a_CheckedDate text)    
    cursUpdate.callproc('PackagesLastCheckedSetRepoDate', (row['abi_name'],row['package_set'], repo_date))

dbh.commit();
dbh.close();
