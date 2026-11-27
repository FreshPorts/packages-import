#!/usr/local/bin/python3.14
#
# Delete the packages of repos which have gone from pkg.freebsd.org.
# re https://github.com/FreshPorts/freshports/issues/449
#
# Every hour, check_repos_for_new_stuff.py asks pkg.freebsd.org for the
# date of each repo (ABI and package set, e.g. FreeBSD:14:armv6 latest).
# When it gets no date, usually a 404 because the repo is gone, the
# database records when that first happened in
# packages_last_checked.missing_since.  It clears that when a date comes
# back.
#
# This script calls PackagesDeleteForMissingRepos(), which deletes the
# packages rows of every repo missing for longer than the grace period
# (default 7 days).  Until then, the port pages showed those packages
# for as long as the ABI was listed, years in the case of
# FreeBSD:14:armv6 latest.  The grace period keeps a failed fetch, which
# also gives no date, from emptying a repo which is still there.
#
# Run daily by refresh-abi.sh (periodic daily/330.refresh-abi).  For each
# repo emptied, one line goes to stdout, so it shows in the daily
# periodic mail, and to the log.  A run which deletes nothing prints
# nothing.  When something is deleted, NOTIFY packages_imported makes
# fp-listen on the web servers clear their packages caches, as after an
# import.  Each deletion is also recorded in package_imports, with
# inserts and updates 0.
#
# When a repo comes back, the hourly check sees its date and the next
# import fills its packages again.
#
# By hand, as freshports:
#
#   cd /usr/local/libexec/freshports && ./packages-delete-missing-repos.py [--dry-run] [--log-dest stderr]
#
# --dry-run runs the delete inside a transaction, prints what it would
# remove, and rolls it back.  --log-dest stderr logs to stderr instead of
# syslog, for tests.
#

import argparse
import configparser  # for config.ini parsing
import logging
import logging.handlers
import os
import re            # for escaping the database passwords
import sys

from pathlib import Path

import psycopg2
import psycopg2.extras


def parse_args():
    parser = argparse.ArgumentParser(description='Delete the packages of repos missing from pkg.freebsd.org for longer than the grace period.')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='show what would be deleted, then roll back')
    parser.add_argument('-g', '--grace-days', type=int, default=7,
                        help='days a repo must have been missing before its packages are deleted (default 7; 0 only with --dry-run)')
    parser.add_argument('-l', '--log-dest', choices=['syslog', 'stderr'], default='syslog',
                        help="logging destination (default syslog)")
    args = parser.parse_args()
    # 0 is allowed only with --dry-run, to test against a repo which went
    # missing today
    if args.grace_days < 0 or (args.grace_days == 0 and not args.dry_run):
        parser.error('--grace-days must be at least 1 (0 only with --dry-run)')
    return args


def get_logger(log_dest):
    name   = os.path.basename(__file__)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if log_dest == 'syslog':
        handler = logging.handlers.SysLogHandler(address='/var/run/log', facility=logging.handlers.SysLogHandler.LOG_LOCAL3)
        handler.setFormatter(logging.Formatter(name + '[' + str(os.getpid()) + ']: %(message)s'))
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter('%(asctime)s ' + name + ': %(message)s'))
    logger.addHandler(handler)
    return logger


def main():
    args   = parse_args()
    logger = get_logger(args.log_dest)

    logger.info('starting%s, grace %d days', ' (dry run)' if args.dry_run else '', args.grace_days)

    config = configparser.ConfigParser()
    if not config.read('/usr/local/etc/freshports/config.ini'):
        logger.error('cannot read /usr/local/etc/freshports/config.ini')
        print(os.path.basename(__file__) + ': cannot read /usr/local/etc/freshports/config.ini', file=sys.stderr)
        return 1

    offline = Path(config['filesystem']['SIGNAL_OFFLINE'])
    if offline.is_file() and not args.dry_run:
        logger.info('exiting because the system is OFFLINE')
        return 0

    DSN = 'host=' + config['database']['HOST'] + \
          ' dbname=' + config['database']['DBNAME'] + \
          ' user=' + config['database']['PACKAGER_DBUSER'] + \
          ' password=' + re.escape(config['database']['PACKAGER_PASSWORD']) + \
          ' sslcertmode=disable'

    try:
        dbh  = psycopg2.connect(DSN)
        curs = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

        curs.execute('SELECT abi_name, package_set, missing_since, deletes FROM PackagesDeleteForMissingRepos(%s::interval)',
                     (str(args.grace_days) + ' days',))
        rows = curs.fetchall()

        total = 0
        for row in rows:
            total += row['deletes']
            line = '%s %s: %s %d packages, repo missing since %s' % (
                     row['abi_name'], row['package_set'],
                     'would delete' if args.dry_run else 'deleted',
                     row['deletes'], row['missing_since'].strftime('%Y-%m-%d %H:%M %Z'))
            print(line)
            logger.info(line)

        if args.dry_run:
            dbh.rollback()
        else:
            if total > 0:
                # fp-listen on the web servers clears the packages caches
                curs.execute('NOTIFY packages_imported')
            dbh.commit()

        dbh.close()

    except psycopg2.Error as e:
        logger.error('database error: %s', str(e).strip())
        print(os.path.basename(__file__) + ': database error: ' + str(e).strip(), file=sys.stderr)
        return 1

    logger.info('finishes: %d packages from %d repo%s%s', total, len(rows), '' if len(rows) == 1 else 's', ' (dry run, rolled back)' if args.dry_run else '')
    return 0


if __name__ == '__main__':
    sys.exit(main())
