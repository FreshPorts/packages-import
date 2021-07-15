#!/bin/sh

abi=$1
package_set=$2

# get the name of this script
LOGGERTAG=${0##*/}

JQ=/usr/local/bin/jq

. /usr/local/etc/freshports/config.sh

$LOGGER -t $LOGGERTAG starting $0

# we just try to create every time
mkdir -p $BASEDIR_PACKAGER/$abi/$package_set

if [ ! -d $BASEDIR_PACKAGER ]
then
  $LOGGER -t LOGGERTAG "FATAL error: $BASEDIR_PACKAGER does not exist - $0 terminating"
  exit 1
fi

if [ ! -d $BASEDIR_PACKAGER/$abi/$package_set ]
then
  mkdir -p $BASEDIR_PACKAGER/$abi/$package_set
  if [ $? -ne 0 ]
  then
    $LOGGER -t LOGGERTAG "FATAL error: unable to create $BASEDIR_PACKAGER/$abi/$package_set - $0 terminating"
    exit 1
  fi  
fi

cd $BASEDIR_PACKAGER/$abi/$package_set/
if [ $? -ne 0 ]
then
  $LOGGER -t LOGGERTAG "FATAL error: unable to cd $BASEDIR_PACKAGER/$abi/$package_set - $0 terminating"
  exit 1
fi

rm -f packagesite.txz packagesite.tar
if [ $? -ne 0 ]
then
  $LOGGER -t LOGGERTAG "FATAL error: unable to rm packagesite.txz packagesite.tar - $0 terminating"
  exit 1
fi  

fetch --quiet https://pkg.freebsd.org/$abi/$package_set/packagesite.txz
if [ $? -ne 0 ]
then
  $LOGGER -t LOGGERTAG "FATAL error: unable to fetch https://pkg.freebsd.org/$abi/$package_set/packagesite.txz - $0 terminating"
  exit 1
fi

#unxz packagesite.txz
#if [ $? -ne 0 ]
#then
#  $LOGGER -t LOGGERTAG "FATAL error: unable to unxz packagesite.txz - $0 terminating"
#  exit 1
#fi

tar -xf packagesite.txz
if [ $? -ne 0 ]
then
  $LOGGER -t LOGGERTAG "FATAL error: unable to tar -xf packagesite.txz - $0 terminating"
  exit 1
fi


$JQ -rc --arg ABI "$abi" --arg PACKAGE_SET "$package_set" '[$ABI, $PACKAGE_SET, .origin, .name, .version] | @tsv' < packagesite.yaml > packagesite.tsv
if [ $? -ne 0 ]
then
  $LOGGER -t LOGGERTAG "FATAL error: unable to run jq to get the tsv file - $0 terminating"
  exit 1
fi

$SCRIPTDIR/import-via-copy-packagesite-all-raw-fields.py -i packagesite.tsv
if [ $? -ne 0 ]
then
  $LOGGER -t LOGGERTAG "FATAL error: unable to run import-via-copy-packagesite.py to import the file - $0 terminating"
  exit 1
fi

$LOGGER -t LOGGERTAG "finished importing $abi/$package_set"

# this is the return value expected by import_packagesite.py
echo Done

$LOGGER -t LOGGERTAG "finishes"

exit 0
