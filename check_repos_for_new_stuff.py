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


DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])


dbh = psycopg2.connect(DSN)
curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)


curs.execute("SELECT * from GetReposToReview()")
NumRows = curs.rowcount
dbh.commit();
if (NumRows > 0):
  rows = curs.fetchall()
  for row in rows:
    print(row['abi_name'] + '/' + row['branch']);

    command = "/usr/home/dan/src/packages-import/get_packagesite.txz_date " + row['abi_name'] + " " + row['branch']
    timestamp = os.popen(command).readlines()
    if timestamp == []:
      print('nil')
    else:
      print(timestamp[0].strip())

dbh.close();
