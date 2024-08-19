#!/bin/sh

abi=$1
package_set=$2

# get the name of this script
LOGGERTAG=${0##*/}

JQ=/usr/local/bin/jq

. /usr/local/etc/freshports/config.sh

$LOGGER -t $LOGGERTAG starting $0

# we just try to create every time
WORKDIR="$BASEDIR_PACKAGER/$abi/$package_set"
$LOGGER -t $LOGGERTAG creating $WORKDIR
mkdir -p $WORKDIR

if [ ! -d $BASEDIR_PACKAGER ]
then
  $LOGGER -t $LOGGERTAG "FATAL error: $BASEDIR_PACKAGER does not exist - $0 terminating"
  exit 1
fi

if [ ! -d $WORKDIR ]
then
  mkdir -p $WORKDIR
  if [ $? -ne 0 ]
  then
    $LOGGER -t $LOGGERTAG "FATAL error: unable to create $WORKDIR - $0 terminating"
    exit 1
  fi  
fi

$LOGGER -t $LOGGERTAG cd $WORKDIR/
cd $WORKDIR/
if [ $? -ne 0 ]
then
  $LOGGER -t $LOGGERTAG "FATAL error: unable to cd $WORKDIR - $0 terminating"
  exit 1
fi

# NOTE: some older ABI do not have meta.conf
# Notably
# * FreeBSD:12:aarch64 latest, 
# * FreeBSD:12:armv6 latest
# * FreeBSD:12:armv7
#
# If not found, we assumes it is older, and use older default values.
#
 
$LOGGER -t $LOGGERTAG fetch --quiet https://pkg.freebsd.org/$abi/$package_set/meta.conf
fetch --quiet https://pkg.freebsd.org/$abi/$package_set/meta.conf
if [ $? -ne 0 ]
then
  $LOGGER -t $LOGGERTAG "WARNING: unable to fetch https://pkg.freebsd.org/$abi/$package_set/meta.conf - using default values."
  ARCHIVE=packagesite
  ARCHIVE_FILE=packagesite.txz
  PACKAGE_FILE=packagesite.yaml
else

  # This is the name of the archive we need to download
  ARCHIVE=$(grep 'manifests_archive = ' meta.conf | cut -f 2 -d '=' | cut -f 2 -d '"')

  # This is the archive format, usually txz
  FORMAT=$(grep 'packing_format = ' meta.conf | cut -f 2 -d '=' | cut -f 2 -d '"')

  # This is the name of the file we pull down from the server
  ARCHIVE_FILE="${ARCHIVE}.${FORMAT}"

  # the name of the file is obtained from meta.conf - look for manifests
  # This is the archive format, usually txz
  PACKAGE_FILE=$(grep 'manifests = ' meta.conf | cut -f 2 -d '=' | cut -f 2 -d '"')
fi

#
# I'm not sure of the historical reasons for removing these files
# perhaps to be use we're not using files from the previous fetch
#
#
$LOGGER -t $LOGGERTAG rm -f ${ARCHIVE_FILE} "${ARCHIVE}.tar"
rm -f ${ARCHIVE_FILE} "${ARCHIVE}.tar"
if [ $? -ne 0 ]
then
  $LOGGER -t $LOGGERTAG "FATAL error: unable to rm ${ARCHIVE_FILE} ${ARCHIVE}.tar - $0 terminating"
  exit 1
fi  

# grab the file we need
$LOGGER -t $LOGGERTAG fetch --quiet https://pkg.freebsd.org/$abi/$package_set/${ARCHIVE_FILE}
fetch --quiet https://pkg.freebsd.org/$abi/$package_set/${ARCHIVE_FILE}
if [ $? -ne 0 ]
then
  $LOGGER -t $LOGGERTAG "FATAL error: unable to fetch https://pkg.freebsd.org/$abi/$package_set/${ARCHIVE_FILE} - $0 terminating"
  exit 1
fi

# unpackage it
$LOGGER -t $LOGGERTAG tar -xf ${ARCHIVE_FILE}
tar -xf ${ARCHIVE_FILE}
if [ $? -ne 0 ]
then
  $LOGGER -t $LOGGERTAG "FATAL error: unable to tar -xf ${ARCHIVE_FILE} - $0 terminating"
  exit 1
fi

$LOGGER -t $LOGGERTAG $JQ -rc --arg ABI "$abi" --arg PACKAGE_SET "$package_set" '[$ABI, $PACKAGE_SET, .origin, .name, .version] | @tsv' from ${PACKAGE_FILE} into packagesite.tsv
$JQ -rc --arg ABI "$abi" --arg PACKAGE_SET "$package_set" '[$ABI, $PACKAGE_SET, .origin, .name, .version] | @tsv' < ${PACKAGE_FILE} > packagesite.tsv
if [ $? -ne 0 ]
then
  $LOGGER -t $LOGGERTAG "FATAL error: unable to run jq to get the tsv file - $0 terminating"
  exit 1
fi

# specifying the full path name to this script so it shows up better in the logs of that script
$LOGGER -t $LOGGERTA $SCRIPTDIR/import-via-copy-packagesite-all-raw-fields.py -i $WORKDIR/packagesite.tsv
$SCRIPTDIR/import-via-copy-packagesite-all-raw-fields.py -i $WORKDIR/packagesite.tsv
if [ $? -ne 0 ]
then
  $LOGGER -t $LOGGERTAG "FATAL error: unable to run import-via-copy-packagesite-all-raw-fields.py to import the file - $0 terminating"
  exit 1
fi

$LOGGER -t $LOGGERTAG "finished importing $abi/$package_set"

# this is the return value expected by import_packagesite.py - look for: result = os.popen(command).readlines()
echo Done

$LOGGER -t $LOGGERTAG "finishes"

exit 0
