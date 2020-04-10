Let's import packge information from a FreeBSD repo's packagesite.yaml file:

To get the raw data:

fetch https://pkg.freebsd.org/FreeBSD:12:amd64/latest/packagesite.txz
unxz packagesite.txz
tar -xf unxz packagesite.tar


packagesite-convert-to-csv - takes data from STDIN and writes to a file in
                             your current directory: csv
                             runs in about 6 minutes

import-via-copy-packagesite.py - reads from csv and loads into a postgresql
                                 database

Both ready from this file:

$ cat /usr/local/etc/freshports/config.ini
#
# configuration items
#
[database]
DBNAME            = 'freshports.dev'
HOST              = pg.example.org

PACKAGER_DBUSER   = 'packager_dev'
PACKAGER_PASSWORD = '[redacted]'




Example:

$ head -5 packagesite.yaml | packagesite-convert-to-csv
$ cat csv
1	devel/py-pyasn1-modules	py37-pyasn1-modules	0.2.7
1	devel/py-pyasn1	py37-pyasn1	0.4.7
1	graphics/libexif	libexif	0.6.21_5
1	devel/pear-Structures_DataGrid	php72-pear-Structures_DataGrid	0.9.3
1	devel/p5-Thread-Apartment	p5-Thread-Apartment	0.51_1
