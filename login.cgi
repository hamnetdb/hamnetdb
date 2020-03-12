#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Session management
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
do "lib.cgi" or die;
$cookiePath="/";

#
if ($query->param("dp_accept")) {
  if ($username) {
    $db->do("update hamnet_maintainer set dp_accept=1 ".
    "where callsign=".$db->quote($username));
  }
  print qq(Expires: 0\n).
        qq(Status: 302 Moved\n).
        qq(Location: $baseUri/?m=Login\&okMsg=Privacy+term+was+accepted\n\n);
  exit;
}
if ($query->param("logout")) {
  if ($sessionToken && $username) {
    $db->do("update hamnet_session set is_valid=0 ".
    "where token=".$db->quote($sessionToken));
  }
  print qq(Expires: 0\n).
        qq(Status: 302 Moved\n).
        qq(Set-Cookie: HAMNETDB_SESSION=; path=$cookiePath;\n).
        qq(Location: $baseUri/?m=Login\&errMsg=You+are+logged+out\n\n);
  exit;
}
$pw= $query->param("pw");
if ($query->param("newpw") && $username) {
  my $newpw= $query->param("newpw");
  my $newagain= $query->param("newagain");

  if ($newpw ne $newagain) {
    print qq(Expires: 0\n).
          qq(Status: 302 Moved\n).
          qq(Location: $baseUri/?m=Login&errMsg=Passwords+do+not+match.\n\n);
    exit;
  }
  $fullname= "";
  ($fullname)= $db->selectrow_array(
    "select fullname from hamnet_maintainer".
    " where callsign=".$db->quote($username).
    " and passwd=password(".$db->quote($pw).")");
  unless ($fullname) {
    print qq(Expires: 0\n).
          qq(Status: 302 Moved\n).
          qq(Location: $baseUri/?m=Login&errMsg=Old+password+is+incorrect.\n\n);
    exit;
  }
  if ($sessionToken && $username) {
    $db->do("update hamnet_maintainer set ".
      "passwd=password(".$db->quote($newpw).") ".
      "where callsign='$username'");
  }
  print qq(Expires: 0\n).
        qq(Status: 302 Moved\n).
        qq(Location: $baseUri/?m=Login&okMsg=Password+changed\n\n);
  exit;
}

if ($query->param("forgotpw")) {
  my $callsign= $query->param("callsign");
  my $email= $query->param("email");

  $fullname= "";
  ($fullname)= $db->selectrow_array(
    "select fullname from hamnet_maintainer".
    " where callsign=".$db->quote($callsign).
    " and email=".$db->quote($email));
  unless ($fullname) {
    print qq(Expires: 0\n).
          qq(Status: 302 Moved\n).
          qq(Location: $baseUri/?m=Login&errMsg=).
          qq(Could+not+find+callsign+and+email+address.\n\n);
    exit;
  }
  my $newpw= &pwGenerate(8);
  $db->do("update hamnet_maintainer set ".
    "passwd=password(".$db->quote($newpw).") ".
    "where callsign='$callsign'");

  $fullname=~s/ .*$//;
  if ($callsign=~/^(d[a-p]|oe|hb[09])/i) {
    &sendmail("Dein neues Hamnet-DB Passwort",
      qq(Hallo $fullname,\n).
      qq(Du hast auf https://hamnetdb.net ein neues Passwort angefordert.\n\n).
      qq(Es ist: $newpw\n\n).
      qq(Bitte vergib unter "Login" Dein eigenes Passwort.\n\n).
      qq(Viele Gruesse vom Hamnet-DB Team :-\)\n\n),
      $email);
  }
  else {
    &sendmail("Your new Hamnet-DB Password",
      qq(Hello $fullname,\n).
      qq(You have requested a new password on https://hamnetdb.net\n\n).
      qq(It is: $newpw\n\n).
      qq(Please change your password at item "Login".\n\n).
      qq(Your Hamnet-DB team :-\)\n\n),
      $email);
  }
 
  print qq(Expires: 0\n).
        qq(Status: 302 Moved\n).
    qq(Location: $baseUri/?m=Login&okMsg=New+password+sent+to+your+email\n\n);
  exit;
}

$login= lc $query->param("login");
$ip= $ENV{REMOTE_ADDR};
$login=~s/[^0-9a-z]//g;

# Store persistent login as long lasting session and cookie
$persist= $query->param("persist");
$cookieExp= "";
$sessionExp= "10 hour";
if ($persist) {
  $cookieExp= " expires=".(gmtime(time+365*86400)).";";
  $sessionExp= "12 month";
}

$fullname= "";
($fullname)= $db->selectrow_array(
  "select fullname from hamnet_maintainer".
  " where callsign=".$db->quote($login).
  " and passwd=password(".$db->quote($pw).")");

if ($fullname) {
  $sessionToken= &pwGenerate(20)."_".time;
  if ($db->do(qq(insert hamnet_session set 
     callsign='$login',last_ip='$ip',ip='$ip',token='$sessionToken',
     last_act=now(),begin=now(), is_valid=1,
     expires=date_add(now(),interval $sessionExp)))) {
  }
  else {
    print qq(Expires: 0\n).
          qq(Status: 302 Moved\n).
          qq(Set-Cookie: HAMNETDB_SESSION=; path=$cookiePath/;\n).
          qq(Location: $baseUri/?m=Login&errMsg=Cannot+store+session.\n\n);
    exit;
  }
  if ($login=~/^x/i && $login!~/dg8ngn/i ){
    print qq(Expires: 0\n).
          qq(Status: 302 Moved\n).
          qq(Set-Cookie: HAMNETDB_SESSION=; path=$cookiePath/;\n).
          qq(Location: $baseUri/?m=Login&errMsg=Not+possible+due+to+maintanance.+Please+try+again+later\n\n);
  }

  $db->do(qq(update hamnet_maintainer set
     last_login=now() where callsign='$login'));

  print qq(Expires: 0\n).
        qq(Status: 302 Moved\n).
        qq(Set-Cookie: HAMNETDB_SESSION=$sessionToken; path=$cookiePath;$cookieExp\n).
        qq(Location: $baseUri/?login=$login\n\n);
}
else {
  print qq(Expires: 0\n).
        qq(Status: 302 Moved\n).
        qq(Set-Cookie: HAMNETDB_SESSION=; path=$cookiePath/;\n).
        qq(Location: $baseUri/?m=Login&errMsg=Login+incorrect.\n\n);
}
