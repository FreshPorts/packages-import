This file documents various procedures used when processing packages. Most
of these are manually procedures for fixing things.

# Redo an update

There was something wrong with the update process. You've fixed it. Now you
want to update the `packages` table.

This resets the `processed_date` field.

```
UPDATE packages_last_checked PLC
   SET processed_date = NULL
  FROM abi
 WHERE abi.name        IN ( 'FreeBSD:11:amd64', 'FreeBSD:11:i386', 'FreeBSD:12:amd64', 'FreeBSD:12:i386', 'FreeBSD:13:amd64', 'FreeBSD:13:i386' )
   AND abi.id          = PLC.abi_id
   AND PLC.package_set IN ( 'latest', 'quarterly');
```

This signals that there is work to be done. It is run on the ingress server.

```
echo touch /var/db/freshports/signals/new_repo_imported /var/db/freshports/signals/job_waiting | sudo su -fm freshports
```
