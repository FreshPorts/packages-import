#!/bin/sh

. /usr/local/etc/freshports/config.sh

DIRBASE="/usr/home/dan/tmp"
psql="/usr/local/bin/psql -q --no-align --tuples-only --no-password "
query_abi="SELECT id FROM abi WHERE name = "
insert_abi="INSERT INTO abi (name) values ("
ABI="FreeBSD:11:i386 FreeBSD:11:amd64 FreeBSD:11:aarch64 FreeBSD:12:i386 FreeBSD:12:amd64 FreeBSD:12:aarch64 FreeBSD:13:i386 FreeBSD:13:amd64 FreeBSD:13:aarch64"

for abi in $ABI
do
  echo processing $abi
  mkdir -p $DIRBASE/$abi

#  echo    $psql -c "$query_abi '$abi'" --host=$HOST $DB $DBUSER_PACKAGER
  abi_id=`$psql -c "$query_abi '$abi'" --host=$HOST $DB $DBUSER_PACKAGER`
  
#  echo "we found '${abi_id}'"
  if [ "$abi_id" == "" ] ; then
#    echo we have to insert
#    echo    $psql -c "$insert_abi '$abi') ON CONFLICT DO NOTHING RETURNING id" --host=$HOST $DB $DBUSER_PACKAGER
    abi_id=`$psql -c "$insert_abi '$abi') ON CONFLICT DO NOTHING RETURNING id" --host=$HOST $DB $DBUSER_PACKAGER`
  fi
  
  for branch in "latest"
  do
    if [ ! -d $DIRBASE/$abi/$branch ] ; then
      echo mkdir $DIRBASE/$abi/$branch
      mkdir -p $DIRBASE/$abi/$branch
    fi
    echo going into $DIRBASE/$abi/$branch/
    cd $DIRBASE/$abi/$branch/


    fetch https://pkg.freebsd.org/$abi/$branch/packagesite.txz
    unxz packagesite.txz
    tar -xf packagesite.tar

    ls -l ./packagesite.yaml
    jq -rc "[${abi_id}, .origin, .name, .version] | @tsv" < ./packagesite.yaml > packagesite.csv
  
    ~/bin/import-via-copy-packagesite.py -i packagesite.csv
    cd -
  done
done
