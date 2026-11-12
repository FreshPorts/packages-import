This file documents various procedures used when processing packages. Most
of these are manually procedures for fixing things.

# Redo an update

There was something wrong with the update process. You've fixed it. Now you
want to update the `packages` table.

Do this for one ABI and package set at a time: reset it, run the two
scripts, then move on to the next.

`report-notification-packages.pl` handles only one ABI and package set per
run; it logs a single `report_log_package_notifications` row for them.  That
is why `import_packagesite.py` runs both scripts after each repo it imports
(see #590).  Reset several at once and the report mixes them under one ABI.

Running the report sends the "new package" email again to everyone
subscribed to that ABI and package set.  Leave out
`&& ./report-notification-packages.pl` if you don't want that.

For each ABI and package set, first reset its `processed_date` field:

```
UPDATE packages_last_checked PLC
   SET processed_date = NULL
  FROM abi
 WHERE abi.name        = 'FreeBSD:13:amd64'
   AND abi.id          = PLC.abi_id
   AND PLC.package_set = 'latest';
```

Then, on the ingress server, update the `packages` table from that repo and
send the notices.  `UpdatePackagesFromRawPackages.py` works on every repo
whose `processed_date` is NULL, which is now only the one you reset:

```
echo 'cd /usr/local/libexec/freshports && ./UpdatePackagesFromRawPackages.py && ./report-notification-packages.pl' | sudo su -fm freshports
```

Repeat for the next ABI and package set.

This used to touch `signals/new_repo_imported`, for job-waiting.pl to run
the same scripts once for every reset repo.  That flag was dropped in
August 2024 (b2b5c831), when `import_packagesite.py` started running both
scripts itself after each import; nothing watches it any more.
