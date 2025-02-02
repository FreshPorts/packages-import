#!/bin/sh

abi=$1
package_set=$2

# get the name of this script
LOGGERTAG=${0##*/}

JQ=/usr/local/bin/jq

. /usr/local/etc/freshports/config.sh

$LOGGER -t $LOGGERTAG starting $0

# kmod is special on the url
if [ $package_set == "kmod" ]
then
  url_package_set="kmods_latest_2"
else
  url_package_set=$package_set
fi

# we need $package_set to be the right value here...
# after running this script, we'll have the right value for ARCHIVE_FILE
. $SCRIPTDIR/fetch-parse-meta.conf

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

$LOGGER -t $LOGGERTAG fetch --quiet https://pkg.freebsd.org/$abi/$url_package_set/${ARCHIVE_FILE}
fetch --quiet https://pkg.freebsd.org/$abi/$url_package_set/${ARCHIVE_FILE}
if [ $? -ne 0 ]
then
  $LOGGER -t $LOGGERTAG "FATAL error: unable to fetch https://pkg.freebsd.org/$abi/$url_package_set/${ARCHIVE_FILE} - $0 terminating"
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
