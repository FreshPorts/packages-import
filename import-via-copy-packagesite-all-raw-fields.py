#!/usr/local/bin/python

# take a packagesite.yaml file and import some of it into the databases


import psycopg2
import psycopg2.extras
import configparser # for config.ini parsing
import re           # for escaping the database passwords
import syslog       # for logging
import sys
import getopt

import os




syslog.openlog(ident=os.path.basename(__file__), facility=syslog.LOG_LOCAL3)
syslog.syslog(syslog.LOG_NOTICE, 'Starting up')

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print (__file__  + ' -i <inputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg


   syslog.syslog(syslog.LOG_NOTICE, 'copying in from ' + inputfile)

   config = configparser.ConfigParser()
   config.read('/usr/local/etc/freshports/config.ini')


   DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])


   dbh = psycopg2.connect(DSN)
   curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)


   curs.execute("select freshports_branch_set('head')")
   with open(inputfile, 'r') as f:
      curs.copy_from(f, 'packages_raw', sep = '\t', columns = ['abi', 'package_set', 'package_origin', 'package_name', 'package_version'] )

   dbh.commit()
   dbh.close();

syslog.openlog(ident=os.path.basename(__file__), facility=syslog.LOG_LOCAL3)
syslog.syslog(syslog.LOG_NOTICE, 'Starting up')

if __name__ == "__main__":
   main(sys.argv[1:])

syslog.syslog(syslog.LOG_NOTICE, 'Finishing')
