<?
	# $Id: pkg_upload.php,v 1.5 2002-02-11 03:05:04 dan Exp $
	#
	# Copyright (c) 1998-2001 DVL Software Limited

	require("./include/common.php");
	require("./include/freshports.php");
	require("./include/databaselogin.php");

	require("./include/getvalues.php");

	freshports_Start("the place for ports",
					"$FreshPortsName - new ports, applications",
					"FreeBSD, index, applications, ports");
$Debug=0;

?>

<table width="<? echo $TableWidth ?>" border="0" ALIGN="center">
<tr><td VALIGN=TOP>
<TABLE WIDTH="100%">
<TR><TD bgcolor="#AD0040" height="30"><font color="#FFFFFF" size="+1">
<? echo $FreshPortsTitle; ?> -- Update your watch lists based on installed packages
</font></td>
<TR><TD>
			<?
		// make sure the POST vars are ok. 
		// check for funny stuff

		global $gDBG;
		$gDBG  = false;
		$clean = false;
		if (trim($pkg_info) != '') {

			require_once "pkg_utils.inc";

			$clean = (strpos($mode,"c") === false) ? false : true;
			$gDBG  = (strpos($mode,"d") === false) ? false : true;

			$retid = -1;
			if (IsLoginValid($user, $pw, $ret_id) || $visitor) {
				$filename = "/tmp/tmp_pkg_output.$user";
				if (!copy($pkg_info, $filename)) {
					?> <pre> Error writing file on server </pre> <?
					exit();
				}

				require_once "pkg_process.inc";

				#
				# $UserID is set by include/getvalues.php
				#
				if ($visitor) $ret_id = $UserID;

				$result = ProcessPackages($filename, $ret_id, $clean);

				epp("$user Your Ports Are: ");
				eppp($result['FOUND']);
				epp("<PRE>We were unable to be 100% certain about the following ports.");
			  	epp("It is most likely that you will want them, but you may wish to review.</PRE>");
				eppp($result['GUESS']);
			} else { ?>
				<pre>
					Invalid Username and/or Password
		 		</pre> 
		<?	}
		} else {
			if ($visitor) {
		?>

			<P>
			You can update your watch lists from the packges database on your computer.  Use
			the pkg_info command to output.
			</P>
			<FORM action='pkg_upload.php?file=1' method='post' enctype='multipart/form-data'>
				<TABLE>
					<!-- <TR><TD>Enter Your Username</TD></TR>  -->
					<!-- <TR><TD><INPUT type="text" name="user" value"" size=20></TD></TR> -->
					<!-- <TR><TD>&nbsp;</TD></TR> -->
					<TR><TD>Upload the output from pkg_info:</TD></TR>
					<TR><TD><INPUT type="file" name="pkg_info" size=40></TD></TR>
					<TR><TD><INPUT type="submit" name="upload" value="Upload" size=20></TD></TR>
				</TABLE>
			</FORM>

			<P>
			If you prefer, you can download the <A HREF="/freshports.tgz">FreshPorts port</A> which will upload
			the output for you.
			</P>
		<? 	} else { ?>
				<P>
				You must <A HREF="login.php">login</A> before you upload your package information.
				</P>
		<?
		 	} 
		}
		?>
</TD>
</TR>
</TABLE>
</td>
  <td valign="top" width="*">
    <?
		include("./include/side-bars.php");
    ?>
 </td>
</tr>


 </td>
</tr>
</table>

<TABLE WIDTH="<? echo $TableWidth; ?>" BORDER="0" ALIGN="center">
<TR><TD>
<? include("./include/footer.php") ?>
</TD></TR>
</TABLE>

	</BODY>
</HTML>
