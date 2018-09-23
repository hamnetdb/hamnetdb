#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Maintainer input form
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
push @INC,'.';
do "form.cgi" or die;

$suffix= "maintainer";
$table= "hamnet_$suffix";
$table_history= "${table}_hist";
$requiredPermission= $suffix;

($callsign,$fullname,$email,$comment,$permissions,$dp_accept)= &loadFormData
("callsign,fullname,email,comment,permissions,dp_accept");

if ($mustLoadFromDB) {
  $perm_as= ($permissions=~/as,/)?1:0;
  $perm_host= ($permissions=~/host,/)?1:0;
  $perm_site= ($permissions=~/site,/)?1:0;
  $perm_subnet= ($permissions=~/subnet,/)?1:0;
  $perm_maintainer= ($permissions=~/maintainer,/)?1:0;
  $perm_sysadmin= ($permissions=~/sysadmin,/)?1:0;
}
else {
  $perm_as= $query->param("perm_as");
  $perm_host= $query->param("perm_host");
  $perm_site= $query->param("perm_site");
  $perm_subnet= $query->param("perm_subnet");
  $perm_maintainer= $query->param("perm_maintainer");
  $perm_sysadmin= $query->param("perm_sysadmin");
  $passwd= $query->param("passwd");
  $do_notify= $query->param("do_notify");
}

if ($perm_sysadmin && (! $mySysPerm)) {
  &fatal(qq(No sysadmin permission, cannot escalate));
}

$caption= "Change maintainer '$callsign'";
$caption= "New maintainer" unless $id;
&beforeForm($caption);

print qq(
  <tr>
  <td valign="top" align="left" nowrap>Callsign:<br>
  <input type="text" name="callsign" value="$callsign" size=15$chtrack>
  <br>$br10
  </td>
  <td valign="top" align="left" nowrap>Real name:<br>
  <input type="text" name="fullname" value="$fullname" size=20$chtrack>
  </td>
  <td valign="top" align="left" nowrap>eMail:<br>
  <input type="text" name="email" value="$email" size=20$chtrack>
  </td>
  <td valign="top" align="left" nowrap>
  </td>
  </tr>
  <tr>
  <td valign="top" align="left" nowrap colspan=4>New password (empty: no change):<br>
  <input type="text" name="passwd" value="$passwd" size=15$chtrack>
  &nbsp;&nbsp;
  );

&checkBox("Generate new random password and notify user by email",
  "do_notify", $id?$do_notify:1);

print qq(
  </td>
  </tr>
  <tr><td colspan=4>
  <br>
  Permissions:
);

&checkBox("Edit AS &nbsp; ","perm_as",0,$perm_as);
&checkBox("Edit Sites &nbsp; ","perm_site",1,$perm_site);
&checkBox("Edit Subnets &nbsp; ","perm_subnet",1,$perm_subnet);
&checkBox("Edit Hosts &nbsp; ","perm_host",1,$perm_host);
&checkBox("Edit Maintainers &nbsp; ","perm_maintainer",0,$perm_maintainer);
&checkBox("Sysadmin &nbsp; ","perm_sysadmin",0,$perm_sysadmin) if $mySysPerm;

print qq(
  <br><br>
  );
&checkBox("Privacy term has been accepted (can only be set by user)", 
          "dp_accept", 0, $dp_accept);

print qq(
  </td>
  </tr>
  <tr><td colspan=4>
  <br>
  User role, e.g. 'Sysop &lt;callsign&gt;' or 'Maintainer ASxxxxx' or 
  any other helpful hint:<br>
  <textarea name="comment" class="txt" $chtrack
            style="width:100%; height:200px;">$comment</textarea>
  </td></tr>
);
&afterForm;
exit;


# --------------------------------------------------------------------------
# check and store values
sub checkValues {
  $callsign= lc $callsign;
  unless (length($callsign)>3 && length($callsign)<9 && $callsign=~/[0-9]/) {
    $inputStatus= "Callsign is missing or incorrect";
  }
  if ($callsign=~/[^0-9a-z]/) {
    $inputStatus= "Invalid callsign";
  }
  unless ($inputStatus) {
    if ($db->selectrow_array("select callsign from $table ".
          "where callsign='$callsign' and id<>'$id'")) {
      $inputStatus= "The maintainer '$callsign' exists already";
    }
  }
  unless ($fullname) {
    $inputStatus= "Full name: <FirstName> <LastName>";
  }

  $email= lc $email;
  unless ($email=~/.*[a-z].*\@.*[a-z0-9]\.[a-z]*$/i) {
    $inputStatus= "Email address does not look good";
  }
  if (length($comment)<10) {
    $inputStatus= "Please supply the user role in the comment field";
  }

  $permissions= "";
  $permissions.= "as," if $perm_as;
  $permissions.= "site," if $perm_site;
  $permissions.= "subnet," if $perm_subnet;
  $permissions.= "host," if $perm_host;
  $permissions.= "maintainer," if $perm_maintainer;
  $permissions.= "sysadmin," if $perm_sysadmin && $mySysPerm;

  if (! $inputStatus && $do_notify) {
    $passwd= &pwGenerate(8);
    my $name= $fullname;
    $name=~s/ .*$//;
    if ($callsign=~/^(d[a-p]|oe|hb[09])/i) {
      &sendmail("Dein Zugang zur Hamnet-DB",
        qq(Hallo $name,\n$username ).
        qq(hat Dir einen Login bei https://hamnetdb.net eingerichtet.\n\n).
        qq(Login: $callsign\n).
        qq(Passwort: $passwd\n\n).
        qq(Bitte vergib unter "Login" Dein eigenes Passwort.\n\n).
        qq(Solltest Du diese Mail nicht erwarten, ignoriere sie bitte.\n).
        qq(Moeglicherweise hat sich jemand bei der Eingabe vertippt.\n\n).
        qq(Viele Gruesse vom Hamnet-DB Team :-\)\n\n),
        $email);
    }
    else {
      &sendmail("Your Hamnet-DB access data",
        qq(Hello $name,\n$username ).
        qq(has created a login for you at https://hamnetdb.net\n\n).
        qq(Login: $callsign\n).
        qq(Password: $passwd\n\n).
        qq(Please change your password at item "Login".\n\n).
        qq(If you do not expect this notice please ignore and delete it.\n).
        qq(Possibly somebody has chosen your address by mistake.\n\n).
        qq(Your Hamnet-DB team :-\)\n\n),
        $email);
    }
  }

  my $pwField= "";
  if ($passwd) {
    $pwField= "passwd=password(".$db->quote($passwd)."), ";
  }

  my $dp;
  unless ($dp_accept) {
    $dp= "dp_accept=0,";
  }

  return  "comment=".$db->quote($comment).", ".$pwField.
          "callsign=".$db->quote($callsign).", ".
          "fullname=".$db->quote($fullname).", ".
          "permissions=".$db->quote($permissions).", ".$dp.
          "email=".$db->quote($email);
}
