# 2020-04-12

Current status - we have hover text for each repo/ABI combination.

## check_repos_for_new_stuff.py

* Checks each ABI (both latest and quarterly) for new repos
* invokes `get_packagesite.txz_date`
* Pull data from `GetReposToReview()` in database
* updates the `repo_date` column of the `packages_last_checked` table
* usually invoked via `./check_repos_for_new_stuff.py`
* runs in about 3 seconds when checking all 15 repos


## get_packagesite.txz_date

* invoked by `check_repos_for_new_stuff.py`
* shell script to grab last modified date of `packagesite.txz` from web page
* does not get the actual last modified from headers, parses web page
* see http://pkg.freebsd.org/FreeBSD:12:aarch64/ for example
* could be modified to use HEAD and get the actual value from the file


## import_packagesite.py

* imports some data from `packagesite.yaml`
* gets list of ABI/package-set values from `PackagesGetReposNeedingImports()`
* invokes `fetch-extract-parse-import-one-abi.sh` to do the import
* calls `PackagesLastCheckedSetImportDate()` to mark the import as completed
* usually invoked via `echo /usr/local/libexec/freshports/import_packagesite.py | sudo su -l freshports`
* runs in about 70 seconds importing 15 repos


## fetch-extract-parse-import-one-abi.sh

* invoked by `import_packagesite.py`
* fetches `packagesite.txz`
* extracts `origin`, `name`, `version` into a TSV file: `packagesite.tsv`
* invokes `import-via-copy-packagesite-all-raw-fields.py` to populate the `packages_raw` table

## import-via-copy-packagesite-all-raw-fields.py

* invoked by `fetch-extract-parse-import-one-abi.sh`
* connects to database and uses `COPY` to load `packagesite.tsv` into the `packages_raw` table

# now deprecated

## import-raw-abi.sh

* shell script to extract values from `packagesite.txz` and convert to tab delimited file
* invokes `import-via-copy-packagesite-all-raw-fields.py` to populate the `packages_raw` table

# Older stuff

Some stuff from 2020-04-11 and before

THIS JUST IN, re https://twitter.com/DLangille/status/1248635433275330560

Combined suggestions from Fosstodon & from bsd.network:

```
$ time jq -rc '[1, .origin, .name, .version] | @tsv' < ~/tmp/FreeBSD\:12\:amd64/latest/packagesite.yaml > packagesite.csv

real0m1.351s
user0m1.295s
sys0m0.055s

$ time ./import-via-copy-packagesite.py

real0m1.731s
user0m0.131s
sys0m0.008s

The data get in there fast enough.
```

Next step, go from that raw data into normalized form.  That should be easier & faster now that it's in a [#PostgreSQL] database [on #FreeBSD].

Thank you.


proof-of-concept for importing packagesite.yaml into FreshPorts.  The steps are:

1. From each line of 32500-line yaml file, extract 3 fields creating a csv file
1. load cvs file into db

Step 2 takes seconds.

I need help / advice with step 1 which takes 3 minutes.


Let's import packge information from a FreeBSD repo's packagesite.yaml file:

To get the raw data:

```
fetch https://pkg.freebsd.org/FreeBSD:12:amd64/latest/packagesite.txz
unxz packagesite.txz
tar -xf packagesite.tar
```


packagesite-convert-to-csv - takes data from STDIN and writes to a file in
                             your current directory: csv
                             runs in about 6 minutes

import-via-copy-packagesite.py - reads from csv and loads into a postgresql
                                 database

Both ready from this file:

```
$ cat /usr/local/etc/freshports/config.ini
#
# configuration items
#
[database]
DBNAME            = 'freshports.dev'
HOST              = pg.example.org

PACKAGER_DBUSER   = 'packager_dev'
PACKAGER_PASSWORD = '[redacted]'
```




Example:

```
$ head -5 packagesite.yaml | packagesite-convert-to-csv
$ cat csv
1	devel/py-pyasn1-modules	py37-pyasn1-modules	0.2.7
1	devel/py-pyasn1	py37-pyasn1	0.4.7
1	graphics/libexif	libexif	0.6.21_5
1	devel/pear-Structures_DataGrid	php72-pear-Structures_DataGrid	0.9.3
1	devel/p5-Thread-Apartment	p5-Thread-Apartment	0.51_1
```
