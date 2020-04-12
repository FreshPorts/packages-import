#!/usr/local/bin/python

import re
#import yaml
#import io
import sys
import getopt
import psycopg2
import psycopg2.extras

from psycopg2.extensions import adapt

import configparser # for config.ini parsing
def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
#      print ('test.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
#      print(opt)
      if opt == '-h':
         print ('import-via-copy-packagesite.py -i <inputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
#         print("my input file is {}".format(inputfile))
   
#   print("my input file is {}".format(inputfile))




#   print("inputfile='%s'" % (inputfile))

   config = configparser.ConfigParser()
   config.read('/usr/local/etc/freshports/config.ini')


   DSN = 'host=' + config['database']['HOST'] + ' dbname=' + config['database']['DBNAME'] + ' user=' + config['database']['PACKAGER_DBUSER'] + ' password=' + re.escape(config['database']['PACKAGER_PASSWORD'])


   dbh = psycopg2.connect(DSN)
   curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)


   curs.execute("select freshports_branch_set('head')")


   with open(inputfile, 'r') as f:
      curs.copy_from(f, 'packages_raw', sep = '\t', columns = ['abi', 'branch', 'package_origin', 'package_name', 'package_version'] )

   dbh.commit()
   dbh.close();



if __name__ == "__main__":
   main(sys.argv[1:])

