Add try..catch around all SQL calls.  That way we can catch SQL errors and
not introduce endless loops because the script failed and didn't remove the
signal upon exit.
