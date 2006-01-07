<?php
	#
	# $Id: date.php,v 1.1.2.33 2006-01-07 21:29:10 dan Exp $
	#
	# Copyright (c) 1998-2004 DVL Software Limited
	#

	require_once($_SERVER['DOCUMENT_ROOT'] . '/include/common.php');
	require_once($_SERVER['DOCUMENT_ROOT'] . '/include/freshports.php');
	require_once($_SERVER['DOCUMENT_ROOT'] . '/include/databaselogin.php');

	require_once($_SERVER['DOCUMENT_ROOT'] . '/include/getvalues.php');
	require_once($_SERVER['DOCUMENT_ROOT'] . '/../classes/commits.php');

	# NOTE: All dates must be of the form: YYYY/MM/DD
	# this format can be achieved using the date('Y/m/d') function.

	#
	# Get the date we are going to work with.
	#
	if (IsSet($_GET['date'])) {
		$Date = AddSlashes($_GET['date']);
	} else {
		$Date = '';
	}

	$DateMessage = '';

	if ($Date == '' || strtotime($Date) == -1) {
		$DateMessage = 'date assumed';
		$Date = date('Y/m/d');
	}
	list($year, $month, $day) = explode('/', $Date);
	if (!CheckDate($month, $day, $year)) {
		$DateMessage = 'date adjusted to something realistic';
		$Date = date('Y/m/d');
	} else {
		$Date = date('Y/m/d', strtotime($Date));
	}

	$commits = new Commits($db);
	$last_modified = $commits->LastModified($Date);

	freshports_ConditionalGet($last_modified);

	freshports_Start($FreshPortsSlogan,
					$FreshPortsName . ' - new ports, applications',
					'FreeBSD, index, applications, ports');
	$Debug = 0;

	$ArchiveBaseDirectory = $_SERVER['DOCUMENT_ROOT'] . '/archives';

	function ArchiveFileName($Date) {
		$File = $ArchiveBaseDirectory . '/' . $Date . '.daily';
	}

	function ArchiveDirectoryCreate($Date) {
		$SubDir      = date('Y/m', strtotime($Date));
		$DirToCreate = $ArchiveBaseDirectory . '/' . $SubDir;
		system("mkdir -p $DirToCreate");
		
		return $DirToCreate;
	}

	function ArchiveExists($Date) {
		# returns file name for archive if it exists
		# empty string otherwise

		$File = ArchiveFileName($Date);
		if (!file_exists($File)) {
			$File = '';
		}

		return $File;
	}

	function ArchiveSave($Date) {
		# saves the archive away...
		
		ArchiveDirectoryCreate($Date);
		$File = ArchiveFileName($Date);
		
		

		
	}

	function ArchiveCreate($Date, $DateMessage, $db, $User) {
		GLOBAL $freshports_CommitMsgMaxNumOfLinesToShow;

		$commits = new Commits($db);
		$NumRows = $commits->Fetch($Date, $User->id);
	
		#echo '<br>NumRows = ' . $NumRows;

		$HTML = '';

		if ($NumRows == 0) {
			$HTML .= '<TR><TD COLSPAN="3" BGCOLOR="' . BACKGROUND_COLOUR . '" HEIGHT="0">' . "\n";
			$HTML .= '   <FONT COLOR="#FFFFFF"><BIG>' . FormatTime($Date, 0, "D, j M Y") . '</BIG></FONT>' . "\n";
			$HTML .= '</TD></TR>' . "\n\n";
			$HTML .= '<TR><TD>No commits found for that date</TD></TR>';
		}
		
		unset($ThisCommitLogID);
		for ($i = 0; $i < $NumRows; $i++) {
			$commit = $commits->FetchNth($i);
			$ThisCommitLogID = $commit->commit_log_id;
		
			if ($LastDate <> $commit->commit_date) {
				$LastDate = $commit->commit_date;
				$HTML .= '<TR><TD COLSPAN="3" BGCOLOR="' . BACKGROUND_COLOUR . '" HEIGHT="0">' . "\n";
				$HTML .= '   <FONT COLOR="#FFFFFF"><BIG>' . FormatTime($commit->commit_date, 0, "D, j M Y") . ' : ' . $NumRows . ' commits found </BIG>';
				if ($DateMessage) {
					$HTML .= ' (' . $DateMessage . ')';
				}
				
				$HTML .= '</FONT>' . "\n";
				$HTML .= '</TD></TR>' . "\n\n";
			}
		
			$j = $i;
		
			$HTML .= "<TR><TD>\n";
		
			// OK, while we have the log change log, let's put the port details here.
		
			# count the number of ports in this commit
			$NumberOfPortsInThisCommit = 0;
			$MaxNumberPortsToShow      = 10;
			while ($j < $NumRows && $commit->commit_log_id == $ThisCommitLogID) {
				$NumberOfPortsInThisCommit++;
		
				if ($NumberOfPortsInThisCommit == 1) {
					$HTML .= '<SMALL>';
					$HTML .= '[ ' . $commit->commit_time . ' ' . freshports_CommitterEmailLink($commit->committer) . ' ]';
					$HTML .= '</SMALL>';
					$HTML .= '&nbsp;';
					$HTML .= freshports_Email_Link($commit->message_id);
		
					if ($commit->EncodingLosses()) {
						$HTML .= '&nbsp;' . freshports_Encoding_Errors();
					}

					if (IsSet($commit->security_notice_id)) {
						$HTML .= ' <a href="/security-notice.php?message_id=' . $commit->message_id . '">' . freshports_Security_Icon() . '</a>';
					}

				}
		
				if ($NumberOfPortsInThisCommit <= $MaxNumberPortsToShow) {
		
					$HTML .= "<BR>\n";
		
					$HTML .= '<BIG><B>';
					$HTML .= '<A HREF="/' . $commit->category . '/' . $commit->port . '/">';
					$HTML .= $commit->port;
				
					$HTML .= ' ' . freshports_PackageVersion($commit->version, $commit->revision, $commit->epoch);
		
					$HTML .= "</A></B></BIG>\n";
		
					$HTML .= '<A HREF="/' . $commit->category . '/">';
					$HTML .= $commit->category. "</A>";
					$HTML .= '&nbsp;';
		
					if ($User->id) {
#						echo '$User->watch_list_add_remove=\'' . $User->watch_list_add_remove . '\'';

						if ($commit->onwatchlist) {
							$HTML .= ' '. freshports_Watch_Link_Remove($User->watch_list_add_remove, $commit->onwatchlist, $commit->element_id) . ' ';
						} else {
							$HTML .= ' '. freshports_Watch_Link_Add   ($User->watch_list_add_remove, $commit->onwatchlist, $commit->element_id) . ' ';
						}
					}
		
					// indicate if this port has been removed from cvs
					if ($commit->status == "D") {
						$HTML .= " " . freshports_Deleted_Icon_Link() . "\n";
					}
		
					// indicate if this port needs refreshing from CVS
					if ($commit->needs_refresh) {
						$HTML .= " " . freshports_Refresh_Icon_Link() . "\n";
					}
		
					if ($commit->date_added > Time() - 3600 * 24 * $DaysMarkedAsNew) {
						$MarkedAsNew = "Y";
						$HTML .= freshports_New_Icon() . "\n";
					}
		
					if ($commit->forbidden) {
						$HTML .= ' ' . freshports_Forbidden_Icon_Link($commit->forbidden) . "\n";
					}
		
					if ($commit->broken) {
						$HTML .= ' '. freshports_Broken_Icon_Link($commit->broken) . "\n";
					}
		
					if ($commit->deprecated) {
						$HTML .= ' '. freshports_Deprecated_Icon_Link($commit->deprecated) . "\n";
					}
		
					if ($commit->expiration_date) {
						if (date('Y-m-d') >= $commit->expiration_date) {
							$HTML .= freshports_Expired_Icon_Link($commit->expiration_date) . "\n";
						} else {
							$HTML .= freshports_Expiration_Icon_Link($commit->expiration_date) . "\n";
						}
					}

					if ($commit->ignore) {
						$HTML .= ' '. freshports_Ignore_Icon_Link($commit->ignore) . "\n";
					}
		
					$HTML .= freshports_CommitFilesLink($commit->message_id, $commit->category, $commit->port);
					$HTML .= "&nbsp;";
		
					$HTML .= htmlspecialchars($commit->short_description) . "\n";
				}
		
				$j++;
				$PreviousCommit = $commit;
				if ($j < $NumRows) {
					$commit = $commits->FetchNth($j);
				}
			} // end while
		
		
			if ($NumberOfPortsInThisCommit > $MaxNumberPortsToShow) {
				$HTML .= '<BR>' . freshports_MorePortsToShow($PreviousCommit->message_id, $NumberOfPortsInThisCommit, $MaxNumberPortsToShow);
			}
		
			$i = $j - 1;
		
			$HTML .= "\n<BLOCKQUOTE>";
		
			$HTML .= freshports_PortDescriptionPrint($PreviousCommit->commit_description, $PreviousCommit->encoding_losses, $freshports_CommitMsgMaxNumOfLinesToShow, freshports_MoreCommitMsgToShow($PreviousCommit->message_id, $freshports_CommitMsgMaxNumOfLinesToShow));
		
			$HTML .= "\n</BLOCKQUOTE>\n</TD></TR>\n\n\n";
		}

		return $HTML;
	}

?>

<?php
#echo "That date is " . $Date . '<br>';
#echo 'which is ' . strtotime($Date) . '<br>';

define('RELATIVE_DATE_24HOURS', 24 * 60 * 60);	# seconds in a day

$Today     = '<a href="/commits.php">Today\'s commits</a>';
$Yesterday = freshports_LinkToDate(strtotime($Date) - RELATIVE_DATE_24HOURS);
$Tomorrow  = freshports_LinkToDate(strtotime($Date) + RELATIVE_DATE_24HOURS);

if (strtotime($Date) + RELATIVE_DATE_24HOURS == strtotime(date('Y/m/d'))) {
	$Yesterday = freshports_LinkToDate(strtotime($Date) - RELATIVE_DATE_24HOURS);

	$DateLinks = '&lt; ' . $Today . ' | ' . $Yesterday . ' &gt;';
} else {
	$Today     = '<a href="/commits.php">Today\'s commits</a>';
	$Yesterday = freshports_LinkToDate(strtotime($Date) - RELATIVE_DATE_24HOURS);
	$Tomorrow  = freshports_LinkToDate(strtotime($Date) + RELATIVE_DATE_24HOURS);

	$DateLinks = '&lt; ' . $Today . ' | ' . $Tomorrow . ' | ' . $Yesterday . ' &gt;';
}
echo $DateLinks;
?>

<?php echo freshports_MainTable(); ?>

<TR><TD VALIGN="top" WIDTH="100%">

<?php

echo freshports_MainContentTable();

$HTML = ArchiveCreate($Date, $DateMessage, $db, $User);

echo $HTML;

echo '</table>';

echo $DateLinks;

?>

</td>

  <TD VALIGN="top" WIDTH="*" ALIGN="center">

	<?
	echo freshports_SideBar();
	?>

  </td>	
</tr>
</table>

<?
echo freshports_ShowFooter();
?>

</body>
</html>