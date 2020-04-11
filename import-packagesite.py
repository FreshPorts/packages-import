#!/usr/local/bin/python

import re
import yaml
import io
import sys
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

line = sys.stdin.readline()
while line:
    docs = yaml.load_all(line, Loader=yaml.FullLoader)
    try:
        for doc in docs:
#            print(doc['origin'], doc['name'], doc['version'])
#            print(curs.mogrify("INSERT INTO test (num, data) VALUES (%s, %s)", (42, 'bar')))
#            print(curs.morgify("PackageAdd(%s, %s, %s, %s)", ( ABI, doc['origin'], doc['name'], doc['version'] ) ) )
            curs.execute("SELECT PackageAdd('%s', '%s', '%s', '%s')" % ( ABI, doc['origin'], doc['name'], doc['version']))
            
            line = sys.stdin.readline()
    except:
        print('exception')
        line = sys.stdin.readline()


dbh.commit();
dbh.close();
