#!/usr/bin/perl
# ---------------------------------------------------------------
# Hamnet IP database - General utilities
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
#
# Licensed under the Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commercial projects
# - you must leave author and license conditions
# ---------------------------------------------------------------
#
use DBI;
use CGI;
use POSIX qw(strftime);
use POSIX qw(fmod);


# Incorporate styles into page, is faster and always consistent
my $css;
if (open(CSS,"<hamnetdb.css")) {
  $css= join("", <CSS>);
  close(CSS);
  $css=~s/\s+/ /gs;       # remove whitespaces
  $css=~s/\/\*.*?\*\///g; # remove comment
}
# Do the same with JS parts
my $js;
if (open(JS,"<hamnetdb.js")) {
  $js= join("", <JS>);
  close(JS);
  $js=~s/\/\/.*$//mg;     # remove single line content
  $js=~s/^\s+//mg;        # remove leading whitespaces
  $js=~s/\/\*.*?\*\///gs; # remove comment
}
$htmlRel= qq(
  <style type="text/css">
  $css
  </style>
  <script language='JavaScript'>
  $js
  </script>
);

do "config.cgi" or &fatal(qq(Cannot read <b>config.cgi</b><br><br>
  <h3>Solution:</h3>
  - copy <b>config.cgi.sample</b> to <b>config.cgi</b><br>
  - edit <b>config.cgi</b>: Fill in your database credentials.
));

$db= DBI->connect("DBI:mysql:database=$db_name;host=$db_host;charset=utf8",
                  $db_user, $db_pass) or &fatal(qq(
  Cannot open database <b>$db_name</b></b><br><br>
  <h3>Solution:</h3>
  - create MySQL database <b>$db_name</b> and a user with all rights<br>
  - edit <b>config.cgi</b>: Fill in your database credentials.<br><br>
  Current configured user name: <b>$db_user</b> on host: <b>$db_host</b><br>
));
$db->{mysql_auto_reconnect}= 1;

# Sometimes the current URI is needed for redirects etc.
$baseUri= $ENV{"REQUEST_URI"};
$baseUri=~s/\?.*//;
$baseUri=~s/\/[^\/]*$//;

# Prepare search field
$query=  new CGI;
$search= $query->param("q");
$search=~s/^\s+//;
$search=~s/\s+$//;
$searchIsIP=   0;
$searchIsMAC=  0;
$searchIsNet=  0;
$searchIsVLAN= 0;
if ($search) {
  $search= lc $search;
  my $searchMAC= $search;
  $searchMAC=~s/[\.:-]//g;
  if ($search=~/^\d+\.\d+\.\d+\.\d+$/) {
    $searchIsIP= 1;
  }
  elsif ($search=~/^\d+\.\d+\.\d+\.\d+\/\d+$/) {
    $searchIsNet= 1;
  }
  elsif ($searchMAC=~/^[a-f0-9]{12}$/) {
    $searchIsMAC= $searchMAC;
    $search=      $searchMAC;
  }
  if ($search=~/\*/) {
    $search=~s/\*//;
  }
}

# Maintain hamnetdb-Session
$sessionToken= "";
if ($ENV{"HTTP_COOKIE"}=~/HAMNETDB_SESSION=([^;]+)/) {
  $sessionToken= $1;
}
$username= "";
($username)= $db->selectrow_array("select callsign from hamnet_session ".
  "where is_valid=1 and expires>now() and token=".$db->quote($sessionToken));

$myFullname= "";
$myEmail= "";
$myPermissions= "";
$mySysPerm= 0;
$myComment= "";
$myCall_public= 0;
$myDp_accept= 0;
if ($username) {
  my $sth= $db->prepare("select fullname,email,permissions, ".
          "comment, call_public, dp_accept ".
          "from hamnet_maintainer where callsign='$username'");
  $sth->execute or &fatal(qq(
    Cannot select from DB <b>$db_name</b>.<br>
    Are the tables created using <b>hamnetdb.sql</b>?
  ));
  if (@line= $sth->fetchrow_array) {
    $myFullname= $line[0];
    $myEmail= $line[1];
    $myPermissions= $line[2];
    $myComment= $line[3];
    $myCall_public = $line[4];
    $myDp_accept= $line[5];
    $db->do("update hamnet_session set last_act=now(),last_ip=".
       $db->quote($ENV{REMOTE_ADDR})." where token=".$db->quote($sessionToken));
    $mySysPerm= ($myPermissions=~/sysadmin,/)?1:0;
  }
}
$ipPattern= "(\\d+\\.\\d+\\.\\d+\\.\\d+)";

if (open(V,"<VERSION.txt")) {
  $hamnetdb_version= (<V>)[0];
  $hamnetdb_version=~s/\s$//g;
  close(V);
}
1;

# -----------------------------------------------------------------------------
# List utilities
sub listHeader {
  my $caption= shift;

  if ($caption) {
    print("<b>${caption}:</b><br>\n");
  }
  print qq(<table class='list' width="100%"><tr class='listheader'>);
}
sub listHeaderEnd {
  print("</tr>");
}

# -----------------------------------------------------------------------------
# Show completed list
sub listOut {
  my $search= shift;
  my $linecount= 0;
  my $allLines= ($ENV{"REQUEST_URI"}=~/showAllLines/)?1:0;

  foreach $line ($srev?(reverse sort @_):(sort @_)) {
    $line=~s/\n/ /g; $line=~s/^.*:\}//g; $line.="\n";
    my $y= "<b style='background-color:yellow'>";
    if (!$search || $line=~/FOUND/) {
      print($line);
      $linecount++;
    }
    elsif ($line=~s/(>[^<]*)($search)/$1$y$2<\/b>/gi) {
      print($line);
      $linecount++;
    }
    last if ($maxLines && $linecount>=$maxLines && !$allLines);
  }
  print qq(<tr><td colspan="4" style="background:white;border:0">);
  if ($linecount==0) {
    print qq(No entries.);
  }
  elsif ($linecount==1) {
    print qq(1 entry.);
  }
  else {
    if ($linecount>=$maxLines && !$allLines) {
      my $uri= $ENV{"REQUEST_URI"};
      if ($uri=~/\?/) {
        $uri.= "&showAllLines=1";
      }
      else {
        $uri.= "?showAllLines=1";
      }
      my $allLines= int(@_);
      print qq(First $linecount entries shown, 
               <a href='$uri'><b>show all $allLines entries</b>.</a>);
    }
    else {
      print qq($linecount entries.);
    }
  }
  print qq(</td></tr></table>);
}

# -----------------------------------------------------------------------------
# Sort utilities
sub sortInit {
  unless ($sortqFirst) {
    $qstring= $ENV{"QUERY_STRING_UNESCAPED"};
    $qstring= $ENV{"QUERY_STRING"} unless $qstring;
    $qstring=~s/[^0-9a-z_\-\?\&\=\.\/]//gi;
    $qstring=~s/&*sort=([a-z0-9]*)//i;
    $scrit= $1;
    if ($sortDefault && (!$scrit)) {
      $scrit= $sortDefault;
    }
    $srev= undef;
    if ($scrit=~/^(.*)(r)$/) {
      $scrit= $1;
      $srev=  $2;
    }
    $sortqFirst= 1;
  }
}
# -----------------------------------------------------------------------------
sub sortq {
  my $crit=   shift;
  my $phrase= shift;
  my $tdadd=  shift;
  my $col=    "0000000000";
  my $title= "Sort by $phrase";
  my $sname= $0;

  $sname=~s/.*\/[^\/]+$//;
  my $stdrev= "";
  if ($crit=~/^(.*)(r)$/) {
    $crit= $1;
    $stdrev= $2;
  }
  if ($scrit eq $crit) {
    if ($srev) {
      $col=    "c00000";
      $stdrev= "";
    }
    else {
      $col=    "208020";
      $stdrev= "r";
    }
  }
  $title= "Sort by $phrase descending" if $stdrev;
  if ($crit eq "") {
    print qq(<td nowrap $tdadd><b>).
          qq($phrase</b>$add</td>\n);
  }
  else {
    print qq(<td nowrap $tdadd><b><a title="$title" class="h" 
                 href="$sname?$qstring&sort=$crit$stdrev"><font 
                 color="#$col">$phrase</font></a></b>$add</td>\n);
  }
}

# -----------------------------------------------------------------------------
# Crop string and escape html entities
sub maxlen {
  my $txt= shift;
  my $len= shift;

  $txt=~s/\n/ - /g;
  $txt=~s/\r//g;
  $txt=~s/- *-/-/g;
  $txt=~s/ *$//g;
  $txt=~s/ - *$//g;
  $txt=~s/^ - *//g;
  $txt=~s/&/&amp;/g;
  $txt=~s/</&lt;/g;
  $txt=~s/>/&gt;/g;

  if (length($txt) > $len) {
    $len-= 2;
    $txt=~ m/(.{$len})(.*)/;
    $txt= $1."..";
    $txt=~s/[\xC2\xC3]\.\.$/../;  # cropped utf-8 chars
  }
  return $txt;
}

# -----------------------------------------------------------------------------
sub ipInSubnet {
  my $ip= shift;
  my $subnet= shift;

  return 2 if $ip eq $subnet;
  return 0 unless $subnet=~/\//;

  $ip= &aton($ip);
  if ($ip && $subnet=~/([\d\.]+)\/(\d+)/) {
    my $minaddress= &aton($1);
    my $maxaddress= $minaddress + (1<<(32-$2));

    return 1 if ($ip >= $minaddress && $ip < $maxaddress);
  }
  return 0;
}

# -----------------------------------------------------------------------------
# IP address to integer range for database usage
sub ipRange {
  my $subnet= shift;
  my $field=  shift;
  my $where= undef;

  if ($subnet=~/^\d+\.\d+\.\d+\.\d+$/) {
    $where= " and $field='".&aton($subnet)."'";
  }
  elsif ($subnet=~/^\d+\.[\d\.\/]*$/) {
    $subnet=~s/\/(\d+)//;
    my $bits= $1+0;
    $subnet=~s/\.$//;
    my $begin= $subnet;
    while (! ($begin=~/\d+\.\d+\.\d+\.\d+/)) {
      $begin.= ".0";
    }
    $begin= &aton($begin);
    my $end= $subnet;
    if ($bits>0) {
      $end= $begin + (1<<(32-$bits));
    }
    else {
      while (! ($end=~/\d+\.\d+\.\d+\.\d+/)) {
        $end.= ".255";
      }
      $end= &aton($end);
    }
    $where= " and ($field>$begin and $field<$end)";
  }
  return $where;
}

# -----------------------------------------------------------------------------
# Syntactical check of IP address
sub ipCheck {
  my $ip= shift;
  if ($ip=~/^[\d\.]+$/) {
    if ($ip eq &ntoa(&aton($ip))) {
      return 1;
    }
  }
  return 0;
}

# -----------------------------------------------------------------------------
# IP address to text
sub ntoa {
  my $n= shift;
  my $a= "";

  for ($i= 3; $i>=0; $i--) {
    $a.= ($n>>($i*8)) & 255;
    if ($i) {
      $a.= ".";
    }
  }
  return $a;
}

# -----------------------------------------------------------------------------
# IP address to integer
sub aton {
  my $a= shift;

  if ($a =~ /([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)/) {
    return ($1<<24) + ($2<<16) + ($3<<8) + $4;
  }
  return 0;
}


# -----------------------------------------------------------------------------
# html header for popup windows
sub htmlWinHead {
  my $title= shift;
  $title=~s/<[^>]+>//g;
  my $wasChanged= $query->param("wasChanged")+0;

  print qq(Content-Type: text/html\nExpires: 0\n\n<!DOCTYPE html>
  <html><head>
  <script language="JavaScript" src="jquery.js"></script> 
  $htmlRel
  <title>$title</title>
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
  <script language="JavaScript">
  var isChanged= $wasChanged;
  function checkClose() {
    if (isChanged) {
      return 'Input has been changed. "OK" to discard changes!';
    }
  }
  function changed() {
    if (isChanged==0) {
      isChanged= 1;
      var chspan= document.getElementById('changedtext');
      if (chspan) {
        chspan.style.visibility= 'visible'; 
        chspan.innerHTML= '<font color=red><b>Changed</b></font>';
      }
      document.main.onbeforeunload= checkClose;
    }
  }
  function unchanged() {
    if (isChanged) {
      isChanged= 0;
    }
  }
  function checkAbort() {
    if (isChanged) {
      if (! confirm('Input data has been changed.\\n\\nDiscard your changes?')){
        return false;
      }
    }
    unchanged();
    window.close();
  }
  </script>
  </head><body style="margin:0"><div class='popup'>
  );
}
sub htmlWinFoot {
  print qq(
    </div></body></html>
  );
}

# -----------------------------------------------------------------------------
# refresh opener window, try to conserve the position
sub refreshOpener {
  print qq(
    <script language="JavaScript">
    if (opener && !opener.closed) {
      if (opener.document.main && opener.document.main.waschanged) {
        opener.document.main.waschanged.value=1;
        opener.document.main.func.value='reload';
        opener.document.main.submit();
      }
      else if (opener.doGlobalRefreshTimeout) {
        opener.doGlobalRefreshTimeout();
      }
      else {
        var ypos= 0;
        if (opener.window.pageYOffset) {
          ypos= opener.window.pageYOffset; // Mozilla
        }
        else if (opener.document.body && opener.document.body.scrollTop) {
          ypos= opener.document.body.scrollTop;  // IE
        }
        var ref= opener.location.href;
        ref= ref.replace(/&wasChanged=1/, "");
        ref= ref.replace(/&ypos=[0-9]*/, "");
        if (ypos && ypos>0) {
          if (ref.match(/\\?/)) {
            ref= ref+'&ypos='+ypos;
          }
          else {
            ref= ref+'?ypos='+ypos;
          }
        }
        if (ref.match(/\\?/)) {
          ref= ref+'&wasChanged=1';
        }
        opener.location.replace(ref);
      }
    }
    </script>
  );
}

# -----------------------------------------------------------------------------
# checks if window has an opener and close it
sub checkWinClose {
  my $func= shift;
  if ($func eq "close")  {
    print qq(Content-Type: text/html

      <html><body>);
    &refreshOpener;
    print qq(
      <script language="JavaScript">
        window.close();
      </script>
      </body></html>);
    exit;
  }
}


# -----------------------------------------------------------------------------
sub button {
  $phrase= shift;
  $href= shift;

  print("<button type=\"button\" onClick=\"window.location.href=".
        "'$href'\">$phrase</button>\n");
}

# -----------------------------------------------------------------------------
# logarithmic timespan 
sub timespan {
  my $timespan= shift;
  my $ret;
  if ($timespan>1000000000 || $timespan<-10000000) {
    $ret= "&nbsp;";
  }
  elsif ($timespan < 180) {
    $ret= $timespan."s";
  }
  elsif ($timespan < (120*60)) {
    $ret= int($timespan/60)."m";
  }
  elsif ($timespan < (48*3600)) {
    $ret= int($timespan/3600)."h";
  }
  else {
    $ret= int($timespan/(3600*24))."d";
  }
  return $ret;
}

# -----------------------------------------------------------------------------
# combo box
sub comboBox {
  my $phrase=  shift;
  my $name=    shift;
  my $default= shift;
  my $onchange= "";
  unless ($comboAdd=~/onchange=/i) {
    $onchange= " onchange='changed()'";
    if ($name=~/^(.*)\+$/) {      # Automatisch nachladen bei Änderung
      $name= $1;
      $onchange= " onchange='changed();document.main.submit()'";
    }
  }
  my $width= "";
  if ($name=~/^(.*)\-(\d*)$/) { # Keine Leerzeichen danach und feste Breite
    $name= $1;
    $width= qq(style="width:${2}px;");
  }
  my @items= @_;
  my $selected= $query->param($name);
  unless ($selected) {
    $selected= $default;
  }
  if ($default=~/^(.*)\+$/) {
    $selected= $1;
  }
  print("$phrase <select name=\"$name\"$onchange $comboAdd $width>\n");
  foreach $item (@items) {
    my $val= "";
    if ($item=~/^(.*)::(.*)$/) {
      $val= " value='$1'";
      $item= $2;
    }
    my $sel= "";
    $sel= " selected" if $item eq $selected || $val eq " value='$selected'";
    print("<option$sel$val>$item\n");
  }
  print qq(</select>);
  return $selected;
}

# -----------------------------------------------------------------------------
# multi select combo box
sub comboBoxMulti {
  my $name=    shift;
  my $default= shift;
  my $width=   shift;
  my $height=  shift;
  my @items= @_;
  my $selected= $query->param($name);
  my $onchange= "";
  $onchange= " onchange='changed()'";
  if ($name=~/^(.*)\+$/) {      # Automatisch nachladen bei Änderung
    $name= $1;
    $onchange= " onchange='changed();document.main.submit()'";
  }
  unless ($selected) {
    $selected= $default;
  }
  my %selval=();
  foreach $val (split(/[,:]/, $selected)) {
    $selval{$val}= 1;
  }
  print("<select name=\"$name\" $onchange multiple ".
    "style=\"width:$width; height:$height;\">\n");
  foreach $item (@items) {
    $sel= $selval{$item}?" selected":"";
    print("<option$sel>$item\n");
  }
  print("</select>\n");
  return $selected;
}

# -----------------------------------------------------------------------------
sub checkBox {
  my $phrase= shift;
  my $name=   shift;
  my $default=shift;  # Default-Wert wenn Formular leer ist
  my $hardval=shift;  # Wert, der auf jeden Fall übernommen wird

  my $onchange= " onclick='changed()'";
  if ($name=~/^(.*)\+$/) {
    $name= $1;
    $onchange= " onclick='document.main.submit()'";
  }

  my $val= ($query->param($name) ne "");
  $val= $default if $default ne undef && $query->param("nodefaults")==0;
  $val= $hardval if $hardval ne undef;
  my $checked= $val?" checked":"";
  
  print 
    qq(<nobr><input type="checkbox" value="1" id="_$name" name="$name"$checked).
    qq($onchange><label for="_$name">$phrase&nbsp;</label>&nbsp;</nobr>);
  return $val;
}

# -----------------------------------------------------------------------------
sub radioBut {
  my $phrase= shift;
  my $name=   shift;
  my $val=    shift;
  my $selval= shift;

  my $onchange= " onclick='changed()'";
  if ($name=~/^(.*)\+$/) {
    $name= $1;
    $onchange= " onclick='document.main.submit()'";
  }
  my $checked= $val eq $selval?" checked":"";
  
  print qq(<nobr><input type="radio" value="$val" id="_$name$val" name="$name").
    qq($checked$onchange><label for="_$name$val">$phrase&nbsp;</label></nobr>);
}

# -----------------------------------------------------------------------------
sub textBox {
  my $phrase= shift;
  my $name=   shift;
  my $size=   shift;
  $size= 10   unless ($size);
  my $defok=  shift;
  my $val;
  if ($defok) {
    $val= shift;
  }
  else {
    $val= $query->param($name);
  }
  print("$phrase <input type=\"text\" size=\"$size\" name=\"$name\" ".
        "value=\"$val\" onchange='changed()'>&nbsp;&nbsp;\n");
  return $val;
}

# -----------------------------------------------------------------------------
sub searchBox {
  $globalTab= 1;
  print qq(
  Search
  <script language="JavaScript">
    function clearSearch() {
      document.main.q.value= '';
      document.main.q.focus();
    }
  </script>
  <input type="text" name="q" value="$search" style="width:100px;"><button 
    type="button" onclick="clearSearch()" title="Suchbegriff leeren"
    style="width:25px; height:22px;"><img width=11 height=13
    src="delete.png" border=0></button>
  );
}

# -----------------------------------------------------------------------------
sub dispBut {
  print qq( &nbsp;
    <button style="width:90px;height:24px;" type="submit"><nobr><img 
    src="display.png" border=0 width=16 height=14 align="absmiddle"> 
    Refresh</nobr></button>&nbsp;
  );
}
 
# -----------------------------------------------------------------------------
sub newBut {
  my $object= shift;
  my $lw= lc $object;
  my $p= ucfirst $object;
  $p= uc $p if length($p)<3;

  print qq( &nbsp;
  <button type="button" style="height:24px;xwidth:120px;"
    onclick="hamnetdb.edit('$lw',0)"><nobr><img src="add.png" 
    width=14 height=15 border=0 align="absmiddle">
    New $p</nobr></button>&nbsp;
  ) if $username && ($myPermissions=~/$object,/);
}

# -----------------------------------------------------------------------------
# Check if an object is only writable for its maintainers
sub checkMaintainerRW {
  my $rw_maint= shift;
  my $maintainer= shift;

  if ($rw_maint == 0) {                  # Object is not locked to maintainer
    return 1;
  }
  if ($maintainer eq "") {               # Maintainer list is empty, no lock
    return 1;
  }
  if ($mySysPerm) {                      # Sysadmins are always permitted
    return 1;
  }
  if (&inList($username,$maintainer)) {  # I an within the maintainer list
    return 1;
  }
  &fatal("Object is only writable for maintainers, you are not listed");
}

# -----------------------------------------------------------------------------
# Check if a name is within a whitespace or comma separated list of names
sub inList {
  my $name= shift;
  my $list= shift;

  foreach $n (split(/[\s,;]+/, $list)) {
    if ((lc $n) eq (lc $name)) { 
      return 1;
    }
  }
  return 0;
}

# -----------------------------------------------------------------------------
# A sub-menu for switching function details
sub subMenu {
  my $phrase= shift;
  my @vals= @_;
  my $varName= "sel$phrase";
  if ($phrase=~/^(.*):(.*)$/) {
    $varName= $1;
    $phrase= $2;
  }
  $varName=~s/[^a-zA-Z]//;

  my $sel= $query->param($varName);
  unless ($showFuncDef{$varName}) {
    print qq(
      <script language="JavaScript">
        function show$varName(val) {
          document.main.$varName.value= val;
          document.main.submit();
        }
      </script>);
  }
  print qq($phrase:&nbsp;) if $phrase;
  foreach $cmd (@vals) {
    my $val= $cmd;
    if ($cmd=~/^(.*):(.*)$/) {
      $val= $1;
      $phrase= $2;
    }
    if ($val=~s/\+$//) {
      $sel= $val unless $sel;
    }
    my $col= ($val eq $sel)?" subselected":"";
    print qq(
      <a href="javascript:show$varName('$val')" class="submenu$col">$phrase</a>
    );
  }
  unless ($showFuncDef{$varName}>0) {
    $sel=~s/[^a-z0-9\-\_\ ]//gi;
    print qq(
      <input type="hidden" name="$varName" value="$sel">);
    $showFuncDef{$varName}= 1;
  }
  return $sel;
}

# -----------------------------------------------------------------------------
sub fieldset {
  my $caption= shift;
  my $ret= qq(<fieldset width="100%" ).
           qq(style="padding:10px; padding-top:0px; margin=0px;">);
  $ret.= qq(<legend>$caption</legend>) if $caption;
  return $ret;
}
sub fieldsetEnd {
  return "</fieldset>";
}

# -----------------------------------------------------------------------------
# generate random text and numbers
sub pwGenerate {
  my $length= shift;
  $length= 8 unless $length;
  my $res= "";

  do {
    $res= "";
    while (length($res)<$length) {
      my $ch= chr(ord('0')+int(rand(10)));
      my $rndnum= int(rand(30));
      $ch= chr(ord('a')+$rndnum) if $rndnum<26;
      $res.= $ch unless $res=~/$ch/;
    }
  }
  while (! ($res=~/^[a-z].*[0-9].*$/));

  return ucfirst $res;
}

# -----------------------------------------------------------------------------
# unix-time of file modification
sub filetime {
  my $fn= shift;
  my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
      $atime,$mtime,$ctime,$blksize,$blocks)= stat($fn);
  return $mtime;
}

# -----------------------------------------------------------------------------
sub urlencode {
  my $out= shift;
  $out=~s/([\000-\+\{-\377])/sprintf("%%%02x", ord($1))/ge;
  return $out;
}

# -----------------------------------------------------------------------------
# Send a mail to one or more receivers
sub sendmail {
  my $subject= shift;
  my $text= shift;
  my @to= @_;
  my $toline= join(" ", @to);
  my $tolist= join(",", @to);
  
  if (open(ERR,
    "|/usr/sbin/sendmail -finfo\@hamnetdb.net -FHamnet-DB $toline")){
    print ERR "To: $tolist\n";
    print ERR "Subject: $subject\n\n";
    print ERR $text;
    print ERR "\n\n";
    close(ERR);
  }
}

# -----------------------------------------------------------------------------
# AS selection control
sub asCombo {
  my $refresh= shift;
  my $all= shift;
  my $none= shift;
  my $def= shift;
  my $add= shift;

  my @asval= ();
  push(@asval, "-All-") if $all;
  push(@asval, "-None-") if $none;
  my $showAll= 0;
  $showAll=1 if $none;

  my $sth= $db->prepare(qq(
    select hamnet_as.as_num,hamnet_as.name,hamnet_as.comment,
    hamnet_as.country
    from hamnet_as 
    left join hamnet_subnet on hamnet_as.as_num=as_parent
    where hamnet_subnet.begin_ip is not null or $showAll
    group by hamnet_as.as_num
    order by hamnet_as.as_num
  ));
  # 10.2.16 dl8mbt: aus performancegruenden deaktiviert
  #  left join hamnet_host on rawip between begin_ip and end_ip
  #  where hamnet_host.name is not null or $showAll
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $c= &maxlen($line[2], 40);
    $c= " | $c" if $c;
    push(@asval, "$line[0]::$line[0] $line[3] | $line[1]$c");
  }
  $comboAdd= "style='width:25%;overflow:hidden;'";
  $comboAdd= $add if $add;
  my $val= &comboBox("","as".($refresh?"+":""), $def."+", @asval);
  $comboAdd= "";
  return $val;
}

# -----------------------------------------------------------------------------
# JSON helper functions
@json_sent= ();
$json_level= 0;

sub json_obj {
  my $name= shift;
  my $arr= shift;
  print qq(,\n) if $json_sent[$json_level];
  print qq(\n"$name":) if $name;
  print($arr?"\n[\n":"\n{\n");
  $json_level++;
  $json_sent[$json_level]= 0;
}
sub json_obj_end {
  my $arr= shift;
  print $arr?"\n]\n":"\n}\n";
  $json_level--;
  $json_sent[$json_level]= 1;
}
sub json_var {
  my $val= shift;
  my $name= shift;
  $val=~s/\\/\\\\/g;
  $val=~s/"/\\"/g;
  print qq(,\n) if $json_sent[$json_level];
  print qq("$name":) if $name;
  if ($val=~/^[\d\.]+$/) {
    print qq( $val);
  }
  else {
    print qq( "$val");
  }
  $json_sent[$json_level]= 1;
}

# ---------------------------------------------------------------------------
sub prepareWhere {
  my $search= shift;
  my $s= $search;
  my $ip;

  if ($db->selectrow_array(
    qq(select id from hamnet_as where country=).$db->quote($search))) {
    $asWhere= "country='$search'";
    return ("as", $search);
  }
  if ($db->selectrow_array(
    qq(select id from hamnet_site where callsign=).$db->quote($search))) {
    $search= "site:$search";
  }
  elsif ($db->selectrow_array(
    qq(select id from hamnet_maintainer where callsign=).$db->quote($search))){
    return ("maintainer", $s);
  }
  elsif (($ip)= $db->selectrow_array(
    qq(select ip from hamnet_host where name=).$db->quote($search))){
    $search= $ip;
    $s= $ip;
  }

  if ($search=~/^site:(.*)$/) {
    $hostWhere= "site='$1'";
    &mkSubnetFromHostWhere;
    &mkAsFromSubnetWhere;
    return ("site",$s);
  }

  if ($search=~/^$ipPattern$/) {
    my $ip= $1;
    $hostWhere= "hamnet_host.ip='$ip'";
    &mkSubnetFromHostWhere($ip);
    &mkAsFromSubnetWhere;
    return ("host",$s);
  }

  if ($search=~/^$ipPattern\/(\d+)$/) {
    my $base_ip= $1;
    my $bits= $2;
    my $netmask= 0;
    for ($i= 0; $i < 32; $i++) {
      if ($i >= (32-$bits)) {
        $netmask|= (1 << $i);
      }
    }
    $begin_ip= &aton($base_ip);
    $end_ip=   $begin_ip + (1<<(32-$bits));

    $hostWhere= "(rawip>=$begin_ip and rawip<$end_ip)";

    my %sites= ();
    $sth= $db->prepare("select site from hamnet_host where $hostWhere");
    $sth->execute;
    while (@line= $sth->fetchrow_array) {
      $sites{$line[0]}= 1;
    }
    $siteWhere= "(";
    for $site (keys %sites) {
      $siteWhere.= "callsign='$site' or ";
    }
    $siteWhere.= "0)";

    $subnetWhere= "(end_ip>$begin_ip and begin_ip<$end_ip)";
    &mkAsFromSubnetWhere;
    return ("subnet",$s);
  }
  return (&prepareWhereAS($search),$s);
}

# ---------------------------------------------------------------------------
sub prepareWhereAS {
  my $search= shift;
  
  if ($search=~/^(as|)(\d\d\d\d\d(\d\d\d\d\d)?)$/i) {
    my $as= $2;

    # merge potentially existent child AS into the view 
    my $childs= "";
    ($childs)= $db->selectrow_array("select ".
      "group_concat(as_num separator ',') ".
      "from hamnet_as where as_root='$as'");
    if ($childs) {
      $asWhere= "as_num in ($as,$childs)";
      $subnetWhere= "as_parent in ($as,$childs)";
    }
    else {
      $asWhere= "as_num='$as'";
      $subnetWhere= "as_parent='$as'";
    }

    # Search for subnets that belong to this AS
    my $sth= $db->prepare("select begin_ip,end_ip from hamnet_subnet ".
                          "where $subnetWhere");
    $sth->execute;
    $hostWhere= "(";
    while (@line= $sth->fetchrow_array) {
      $hostWhere.= "(rawip>=$line[0] and rawip<$line[1]) or ";
    }
    $hostWhere.= "0)";

    # Now collect all sites found in hosts, but omit routing-endpoints
    my %sites= ();
    $sth= $db->prepare("select site from hamnet_host where $hostWhere ".
                       "and typ not like 'Routing%'");
    $sth->execute;
    while (@line= $sth->fetchrow_array) {
      $sites{$line[0]}= 1;
    }
    $siteWhere= "(";
    for $site (keys %sites) {
      $siteWhere.= "callsign='$site' or ";
    }
    $siteWhere.= "0)";
    return "as";
  }
  return "";
}

# ---------------------------------------------------------------------------
sub mkSubnetFromHostWhere {
  my $ip= shift;
  my $found= 0;
  $subnetWhere= "(";
  my %sites= ();
  my $sth= $db->prepare("select rawip,site from hamnet_host ".
                        "where $hostWhere");
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    $subnetWhere.= "(begin_ip<=$line[0] and end_ip>$line[0]) or ";
    $sites{$line[1]}= 1;
    $found++;
  }
  $subnetWhere.= "0)";
  $siteWhere= "(";
  for $site (keys %sites) {
    $siteWhere.= "callsign='$site' or ";
  }
  $siteWhere.= "0)";
  unless ($found) {
    if ($ip) {
      my $rawip= &aton($ip);
      $subnetWhere= "(begin_ip<=$rawip and end_ip>=$rawip)";
    }
  }
}

# ---------------------------------------------------------------------------
sub mkAsFromSubnetWhere {
  $asWhere= "as_num in (";
  my $sth= $db->prepare("select as_parent from hamnet_subnet ".
                        "where $subnetWhere");
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    $asWhere.= "$line[0],";
  }
  $asWhere.= "0)";
  return "as";
}

# ---------------------------------------------------------------------------
sub siteDependency {
  my $site= shift;
  if ($site) {
    my $sth= $db->prepare("select left_site,right_site from hamnet_edge ".
                          "where left_site='$site' or right_site='$site'");
    $sth->execute;
    if (@line= $sth->fetchrow_array) {
      return "Site '$site' found in Edge $line[0]:$line[1]";
    }

    $sth= $db->prepare("select name,ip from hamnet_host where site='$site'");
    $sth->execute;
    if (@line= $sth->fetchrow_array) {
      return "Site '$site' found in Host $line[0] ($line[1])";
    }
  }
  return undef;
}

# ---------------------------------------------------------------------------
sub asDependency {
  my $as= shift;
  if ($as) {
    my $sth= $db->prepare("select ip from hamnet_subnet ".
                          "where as_parent='$as'");
    $sth->execute;
    if (@line= $sth->fetchrow_array) {
      return "AS$as found in Subnet $line[0]";
    }
  }
  return undef;
}

# ---------------------------------------------------------------------------
# Escape meta characters in comment
sub escComment {
  my $comment= shift;

  $comment=~s/&/&amp;/g;
  $comment=~s/</&lt;/g;
  $comment=~s/>/&gt;/g;
  $comment=~
    s/(https*:\/\/\S+\.[a-z0-9]+\/*\S*)/<a target="_blank" href="$1">$1<\/a>/gs;
  $comment=~s/\n/<br>/g;

  return $comment;
}

# ---------------------------------------------------------------------------
# Show an icon to edit if appropriate rights are given
sub editIcon {
  my $m= shift;
  my $id= shift;
  my $notd= shift;
  my $res= "";
  my $mp= $m;
  $mp= "subnet" if $mp eq "edge";

  if ($myPermissions=~/$mp,/) {
    $res= qq(<a href="javascript:hamnetdb.edit('$m',$id)"><img 
       width=11 height=14 align="absmiddle" title="Edit"
       src="edit.png" border=0></a>);
    $res= "<td width='11'>$res</td>" unless $notd;
  }
  
  return $res;
}

# ---------------------------------------------------------------------------
# Show an icon to add object with predefined field
sub addIcon {
  my $m= shift;
  my $fill= shift;
  my $res= "";
  my $mp= $m;
  $mp= "subnet" if $mp eq "edge";

  if ($myPermissions=~/$mp,/) {
    $res= qq( <a href="javascript:hamnetdb.edit('$m',0,'$fill')"><img 
       width=14 height=14 align="top" title="Add new $m"
       src="add.png" border=0></a>);
  }
  return $res;
}

# ---------------------------------------------------------------------------
# Convert MAC address to usual printout in colon-separated hex bytes
sub macColon {
  my $mac= shift;
  if ($mac=~/^(..)(..)(..)(..)(..)(..)$/) {
    return "$1:$2:$3:$4:$5:$6";
  }
  return $mac;
}

# ---------------------------------------------------------------------------
# Print text and if not empty: wrap line before
sub brprint {
  my $c= shift;
  if ($c) {
    print "<br>$c\n";
  }
}

# ---------------------------------------------------------------------------
# Try to edit some standards into radio parameter input
sub alignRadioparam {
  my $c= shift;
  $c=~s/([0-9])\s*MHz/$1MHz/gi;
  $c=~s/([0-9])\s*dBm/$1dBm/gi;
  $c=~s/([0-9])\s*dBi/$1dBi/gi;
  $c=~s/\s*,\s*/,/g;
  return $c;
}

# ---------------------------------------------------------------------------
# deg°mm'ss" or deg°mm.mm' to decimal-degrees
sub degmin2dec {
  my $deg= shift;
  $deg=~s/,/./g;
  $deg=~s/ //g;
  if ($deg=~/^([\d\.]+)°([\d\.]+)'([\d\.]*)/) {
    $deg= $1 + ($2*(1/60.0)) + ($3*(1/3600.0));
  }
  return $deg;
}

# ---------------------------------------------------------------------------
# decimal-degrees to deg°mm.mm'
sub dec2min {
  my $dec= shift;
  my $rest= $dec-int($dec);
  my $min= sprintf("%0.2f", ($rest*60));

  return int($dec)."°$min'";
}

# ---------------------------------------------------------------------------
# decimal-degrees to deg°mm'ss"
sub dec2minsec {
  my $dec= shift;

  my $rest= $dec-int($dec);
  my $min= int($rest*60);

  $rest-= ($min/60);
  my $sec= $rest*3600;

  return sprintf("%d°%02d'%02d\"", $dec, $min, $sec);
}

# ---------------------------------------------------------------------------
# Calculate distance between two geo-coordinates
# Thanks to http://www8.nau.edu/cvm/latlon_formula.html
sub distance {
  my $lat1= shift;
  my $long1= shift;
  my $lat2= shift;
  my $long2= shift;

  my $r= 6371;          # km average WGS84 radius
  my $pi= atan2(1,1)*4;

  $lat1=  $lat1  * ($pi/180);
  $long1= $long1 * ($pi/180);
  $lat2=  $lat2  * ($pi/180);
  $long2= $long2 * ($pi/180);

  sub acos {
    my $x= shift;
    if ($x>=1) {
      return 0;
    }
    return atan2(sqrt(1 - $x**2), $x);
  }

  return &acos(cos($lat1)*cos($long1)*cos($lat2)*cos($long2) + 
               cos($lat1)*sin($long1)*cos($lat2)*sin($long2) + 
               sin($lat1)*sin($lat2)) * $r;
}

# ---------------------------------------------------------------------------
# Calculate bearing angle from one point to another
# Adopted as a mixture from several internet sources
sub bearing {
  my $lat1=  shift;
  my $long1= shift;
  my $lat2=  shift;
  my $long2= shift;

  if ($lat1==$lat2 && $long1==$long2) {
    return "";
  }
  if ($lat1==0 || $long1==0 || $lat2==0 || $long2==0) {
    return "";
  }

  my $pi= atan2(1,1)*4;
  my $a= (90-$lat1) * ($pi/180);
  my $b= (90-$lat2) * ($pi/180);
  my $c= &acos(cos($a)*cos($b) + sin($a)*sin($b)*
               cos(abs($long2-$long1) * ($pi/180)));

  my $d= &acos((cos($b) - cos($c)*cos($a)) / (sin($c)*sin($a)));

  if ($long1 == $long2) {
    if ($lat1 < $lat2) {
      $d= 0;
    } else {
      $d= $pi;
    }
  }

  my $bearing= 0;
  if ($d != 0) {
    $bearing= 360-$d*(180/$pi);
  }
  if ((($long2 - $long1) > 0) || (($long2 == $long1) && ($lat2 < $lat1))) {
    $bearing= 360-$bearing;
  }

  return sprintf("%0.1f°", $bearing);
}

# ---------------------------------------------------------------------------
# Determine the monitoring status for a selection of hosts
sub hostsStatus {
  my $hostWhere= shift;
  my $useSite= shift;
  my $field= "ip";
  $field= "site" if $useSite;

  my %hostOk= ();
  my %hostsStatus= ();
  my $sth= $db->prepare(qq(
    select status,hamnet_host.$field,no_ping,
    unix_timestamp(ts),unix_timestamp(since),message,agent,value
    from hamnet_host
    left join hamnet_check on hamnet_check.ip=hamnet_host.ip
    where $hostWhere
    order by ts
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $status=  $line[$idx++];
    my $field=   $line[$idx++];
    my $no_ping= $line[$idx++];
    my $ts=      $line[$idx++];
    my $since=   "since ".&timespan(time-$line[$idx++]);
    my $message= $line[$idx++];
    my $agent=   $line[$idx++];
    my $value=   $line[$idx++];

    my $color= "grey";
    my $title= "Not checked within last 2 hours.";

    if ($ts>(time-7200) && !$no_ping) {
      if ($status==1) {
        if ($hostOk{$field}==0 || $value<$hostOk{$field}) {
          $hostOk{$field}= $value;
          $value=~s/\..*//;
          $title= "ONLINE $since - ${value}ms at $agent";
          $color= "green";
        }
        else {
          next;
        }
      }
      elsif ($hostOk{$field}) {
        next;
      }
      elsif ($agent && $status==0) {
        $title= "OFFLINE $since at $agent: $message";
        $color= "red";
      }
    }
    $hostsStatus{$field}= 
      "<img align='absmiddle' src='ball-$color.png' title='$title'>";
  }
  return %hostsStatus;
}

# ---------------------------------------------------------------------------
# Determine the link status for a selection of hosts
sub linkStatus {
  my $ip= shift;
  my $type= shift;


  my $result="-";
  my $sth= $db->prepare(qq(
    select 
    status,hamnet_host.ip,hamnet_host.monitor,
    unix_timestamp(ts),unix_timestamp(since),message,agent,value
    from hamnet_host
    left join hamnet_check on hamnet_check.ip=hamnet_host.ip
    where hamnet_check.ip="$ip" and hamnet_check.service="$type"
    order by ts
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $status=  $line[$idx++];
    my $field=   $line[$idx++];
    my $monitor= $line[$idx++];
    my $ts=      $line[$idx++];
    my $since=   "since ".&timespan(time-$line[$idx++]);
    my $message= $line[$idx++];
    my $agent=   $line[$idx++];
    my $value=   $line[$idx++];

    if ($ts>(time-7200)) {
      if ($status==1) {
        $result= "$value";
      }
    }
  }
  return $result;
}
# ---------------------------------------------------------------------------
# Determine the link status for a selection of hosts
sub bgpStatus {
  my $ip= shift;
  my $type= shift;


  my $result="-";
  my $sth= $db->prepare(qq(
    select 
    status,hamnet_host.ip,hamnet_host.routing,
    unix_timestamp(ts),unix_timestamp(since),message,agent,value
    from hamnet_host
    left join hamnet_check on hamnet_check.ip=hamnet_host.ip
    where hamnet_check.ip="$ip" and hamnet_check.service="$type"
    order by ts
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $status=  $line[$idx++];
    my $field=   $line[$idx++];
    my $monitor= $line[$idx++];
    my $ts=      $line[$idx++];
    my $since=   "since ".&timespan(time-$line[$idx++]);
    my $message= $line[$idx++];
    my $agent=   $line[$idx++];
    my $value=   $line[$idx++];

    if ($ts>(time-7200)) {
      if ($status==1) {
        $result= "$value";
      }
    }
  }
  return $result;
}
# ---------------------------------------------------------------------------
# End program if it fails unrecoverable in an early stage 
sub fatal {
  my $reason= shift;
  print qq(Content-Type: text/html\n\n<!DOCTYPE html>\n<html><head>
  $htmlRel
  <h2 style='color:red'>Hamnet-DB Fatal Error</h2>
  $reason
  </body></html>);
  die($reason);
}
sub calcLocator
{
  my $lon= $_[0];
  my $lat= $_[1];
  my $locator = "";

  $lat += 90;
  $lon += 180;
  $locator.= chr(65 + int($lon / 20));
  $locator.= chr(65 + int($lat / 10));
  $lon = fmod($lon,20);
  $lon += 20 if $lon < 0;
  $lat = fmod($lat, 10);
  $lat += 10 if $lat < 0;
  
  $locator.= chr(48 + int($lon / 2));
  $locator.= chr(48 + int($lat / 1));
  $lon = fmod($lon,2);
  $lon += 2 if $lon < 0;
  $lat = fmod($lat, 1);
  $lat += 1 if $lat < 0;
  
  $locator.= chr(65 + int($lon * 12));
  $locator.= chr(65 + int($lat * 24));
  $lon = fmod($lon, ( 1.0 / 12.0));
  $lon +=  1 / 12 if $lon < 0;
  $lat = fmod($lat, ( 1.0 / 24.0));
  $lat += 1 / 24 if $lat < 0;
  
  $locator.= chr(48 + int($lon * 120));
  $locator.= chr(48 + int($lat * 240));
  $lon = fmod($lon, (1 / 120));
  $lon +=  1 / 120 if $lon < 0;
  $lat = fmod($lat,( 1 / 240));
  $lat += 1 / 240 if $lat < 0;
  
  $locator.= chr(65 + int($lon * 120 * 24));
  $locator.= chr(65 + int($lat * 240 * 24));
  $lon = fmod($lon, ( 1 / 120 / 24));
  $lon +=  1 / 120 / 24 if $lon < 0;
  $lat = fmod($lat,(1 / 240 / 24));
  $lat += 1 / 240 / 24 if $lat < 0;
  if(($locator=~ /[A-Z0-9]/) &&  $locator !~ /JJ00AA00AA/ )#($lat>-180 && $lat<180 && $lon>-180 && $lon<180)) 
  {
    #return $lon
    return $locator;
  }
  return "";
}
sub updateCallsign
{
  #my $db = shift;
  my $oldcall= shift;
  my $newcall= shift;
  $db->do("UPDATE hamnet_coverage ".
      "SET callsign='$newcall', status='' WHERE callsign='$oldcall'"); 
  #$db->do("UPDATE hamnet_coverage_hist ".
  #                "SET callsign='$newcall' WHERE callsign='$oldcall'"); 
  $db->do("UPDATE hamnet_edge ".
                  "SET left_site='$newcall' WHERE left_site='$oldcall'"); 
  $db->do("UPDATE hamnet_edge_hist ".
                  "SET left_site='$newcall' WHERE left_site='$oldcall'"); 
  $db->do("UPDATE hamnet_edge ".
                  "SET right_site='$newcall' WHERE right_site='$oldcall'"); 
  $db->do("UPDATE hamnet_edge_hist ".
                  "SET right_site='$newcall' WHERE right_site='$oldcall'"); 
  
  $db->do("UPDATE hamnet_host ".
                  "SET name=REPLACE(name, '$oldcall', '$newcall') WHERE (name REGEXP '\\.$oldcall\$') AND site='$oldcall' ");
  $db->do("UPDATE hamnet_host_hist ".
                  "SET name=REPLACE(name, '$oldcall', '$newcall') WHERE (name REGEXP '\\.$oldcall\$') AND site='$oldcall' ");

  $db->do("UPDATE hamnet_host ".
                  "SET site='$newcall' WHERE site='$oldcall'"); 
  $db->do("UPDATE hamnet_host_hist ".
                  "SET site='$newcall' WHERE site='$oldcall'"); 
}
sub checkMapSource
{
  if ($clientIP=~/^44\./) 
  {
    return 1;
  }
  return 0;
}

# ---------------------------------------------------------------------------
# Create a list of call signs that may be displayed due to data protection
# requirements
sub loadPrivacyWhitelist {
  # site callsigns are by definition always public
  my $sth= $db->prepare("select callsign from hamnet_site");
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    $privacyWhitelist{$line[0]}= 1;
  }
  # user callsigns need to be distinguished
  my $sth= $db->prepare("select callsign,call_public from hamnet_maintainer ".
                        "where dp_accept=1");
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    $privacyWhitelist{$line[0]}= 1 if $line[1] || $username;
  }
}

# ---------------------------------------------------------------------------
# Anonymize (i.e. shorten) all callsigns that are not whitelisted
sub anonymizeCallsign {
  my $calls= shift;
  my $res= "";
  foreach $call (split(/[ \,]+/, $calls)) {
    if ($privacyWhitelist{$call}) {
      $call=~s/..$/../;
    }
    $res.= "," if $res;
    $res.= $call;
  }
  return $res;
}


$tldName{"af"}= "Afghanistan";
$tldName{"al"}= "Albania";
$tldName{"dz"}= "Algeria";
$tldName{"as"}= "American Samoa";
$tldName{"ad"}= "Andorra";
$tldName{"ao"}= "Angola";
$tldName{"ai"}= "Anguilla";
$tldName{"aq"}= "Antarctica";
$tldName{"ag"}= "Antigua and Barbuda";
$tldName{"ar"}= "Argentina";
$tldName{"am"}= "Armenia";
$tldName{"aw"}= "Aruba";
$tldName{"au"}= "Australia";
$tldName{"at"}= "Austria";
$tldName{"az"}= "Azerbaijan";
$tldName{"bs"}= "The Bahamas";
$tldName{"bh"}= "Bahrain";
$tldName{"bd"}= "Bangladesh";
$tldName{"bb"}= "Barbados";
$tldName{"by"}= "Belarus";
$tldName{"be"}= "Belgium";
$tldName{"bz"}= "Belize";
$tldName{"bj"}= "Benin";
$tldName{"bm"}= "Bermuda";
$tldName{"bt"}= "Bhutan";
$tldName{"bo"}= "Bolivia";
$tldName{"ba"}= "Bosnia and Herzegovina";
$tldName{"bw"}= "Botswana";
$tldName{"bv"}= "Bouvet Island";
$tldName{"br"}= "Brazil";
$tldName{"io"}= "British Indian Ocean Territory";
$tldName{"vg"}= "British Virgin Islands";
$tldName{"bn"}= "Brunei";
$tldName{"bg"}= "Bulgaria";
$tldName{"bf"}= "Burkina Faso";
$tldName{"mm"}= "Burma";
$tldName{"bi"}= "Burundi";
$tldName{"cv"}= "Cabo Verde";
$tldName{"kh"}= "Cambodia";
$tldName{"cm"}= "Cameroon";
$tldName{"ca"}= "Canada";
$tldName{"ky"}= "Cayman Islands";
$tldName{"cf"}= "Central African Republic";
$tldName{"td"}= "Chad";
$tldName{"cl"}= "Chile";
$tldName{"cn"}= "China";
$tldName{"cx"}= "Christmas Island";
$tldName{"cc"}= "Cocos (Keeling) Islands";
$tldName{"co"}= "Colombia";
$tldName{"km"}= "Comoros";
$tldName{"cd"}= "Congo, Democratic Republic of the";
$tldName{"cg"}= "Congo, Republic of the";
$tldName{"ck"}= "Cook Islands";
$tldName{"cr"}= "Costa Rica";
$tldName{"ci"}= "Cote d'Ivoire";
$tldName{"hr"}= "Croatia";
$tldName{"cu"}= "Cuba";
$tldName{"cw"}= "Curacao";
$tldName{"cy"}= "Cyprus";
$tldName{"cz"}= "Czechia";
$tldName{"dk"}= "Denmark";
$tldName{"dj"}= "Djibouti";
$tldName{"dm"}= "Dominica";
$tldName{"do"}= "Dominican Republic";
$tldName{"ec"}= "Ecuador";
$tldName{"eg"}= "Egypt";
$tldName{"sv"}= "El Salvador";
$tldName{"gq"}= "Equatorial Guinea";
$tldName{"er"}= "Eritrea";
$tldName{"ee"}= "Estonia";
$tldName{"et"}= "Ethiopia";
$tldName{"fk"}= "Falkland Islands (Islas Malvinas)";
$tldName{"fo"}= "Faroe Islands";
$tldName{"fj"}= "Fiji";
$tldName{"fi"}= "Finland";
$tldName{"fr"}= "France";
$tldName{"fx"}= "France, Metropolitan";
$tldName{"gf"}= "French Guiana";
$tldName{"pf"}= "French Polynesia";
$tldName{"tf"}= "French Southern and Antarctic Lands";
$tldName{"ga"}= "Gabon";
$tldName{"gm"}= "Gambia, The";
$tldName{"ps"}= "Gaza Strip";
$tldName{"ge"}= "Georgia";
$tldName{"de"}= "Germany";
$tldName{"gh"}= "Ghana";
$tldName{"gi"}= "Gibraltar";
$tldName{"gr"}= "Greece";
$tldName{"gl"}= "Greenland";
$tldName{"gd"}= "Grenada";
$tldName{"gp"}= "Guadeloupe";
$tldName{"gu"}= "Guam";
$tldName{"gt"}= "Guatemala";
$tldName{"gg"}= "Guernsey";
$tldName{"gn"}= "Guinea";
$tldName{"gw"}= "Guinea-Bissau";
$tldName{"gy"}= "Guyana";
$tldName{"ht"}= "Haiti";
$tldName{"hm"}= "Heard Island and McDonald Islands";
$tldName{"va"}= "Holy See (Vatican City)";
$tldName{"hn"}= "Honduras";
$tldName{"hk"}= "Hong Kong";
$tldName{"hu"}= "Hungary";
$tldName{"is"}= "Iceland";
$tldName{"in"}= "India";
$tldName{"id"}= "Indonesia";
$tldName{"ir"}= "Iran";
$tldName{"iq"}= "Iraq";
$tldName{"ie"}= "Ireland";
$tldName{"im"}= "Isle of Man";
$tldName{"il"}= "Israel";
$tldName{"it"}= "Italy";
$tldName{"jm"}= "Jamaica";
$tldName{"jp"}= "Japan";
$tldName{"je"}= "Jersey";
$tldName{"jo"}= "Jordan";
$tldName{"kz"}= "Kazakhstan";
$tldName{"ke"}= "Kenya";
$tldName{"ki"}= "Kiribati";
$tldName{"kp"}= "Korea, North";
$tldName{"kr"}= "Korea, South";
$tldName{"kw"}= "Kuwait";
$tldName{"kg"}= "Kyrgyzstan";
$tldName{"la"}= "Laos";
$tldName{"lv"}= "Latvia";
$tldName{"lb"}= "Lebanon";
$tldName{"ls"}= "Lesotho";
$tldName{"lr"}= "Liberia";
$tldName{"ly"}= "Libya";
$tldName{"li"}= "Liechtenstein";
$tldName{"lt"}= "Lithuania";
$tldName{"lu"}= "Luxembourg";
$tldName{"mo"}= "Macau";
$tldName{"mk"}= "Macedonia";
$tldName{"mg"}= "Madagascar";
$tldName{"mw"}= "Malawi";
$tldName{"my"}= "Malaysia";
$tldName{"mv"}= "Maldives";
$tldName{"ml"}= "Mali";
$tldName{"mt"}= "Malta";
$tldName{"mh"}= "Marshall Islands";
$tldName{"mq"}= "Martinique";
$tldName{"mr"}= "Mauritania";
$tldName{"mu"}= "Mauritius";
$tldName{"yt"}= "Mayotte";
$tldName{"mx"}= "Mexico";
$tldName{"fm"}= "Micronesia, Federated States of";
$tldName{"md"}= "Moldova";
$tldName{"mc"}= "Monaco";
$tldName{"mn"}= "Mongolia";
$tldName{"me"}= "Montenegro";
$tldName{"ms"}= "Montserrat";
$tldName{"ma"}= "Morocco";
$tldName{"mz"}= "Mozambique";
$tldName{"na"}= "Namibia";
$tldName{"nr"}= "Nauru";
$tldName{"np"}= "Nepal";
$tldName{"nl"}= "Netherlands";
$tldName{"an"}= "Netherlands Antilles";
$tldName{"nc"}= "New Caledonia";
$tldName{"nz"}= "New Zealand";
$tldName{"ni"}= "Nicaragua";
$tldName{"ne"}= "Niger";
$tldName{"ng"}= "Nigeria";
$tldName{"nu"}= "Niue";
$tldName{"nf"}= "Norfolk Island";
$tldName{"mp"}= "Northern Mariana Islands";
$tldName{"no"}= "Norway";
$tldName{"om"}= "Oman";
$tldName{"pk"}= "Pakistan";
$tldName{"pw"}= "Palau";
$tldName{"pa"}= "Panama";
$tldName{"pg"}= "Papua New Guinea";
$tldName{"py"}= "Paraguay";
$tldName{"pe"}= "Peru";
$tldName{"ph"}= "Philippines";
$tldName{"pn"}= "Pitcairn Islands";
$tldName{"pl"}= "Poland";
$tldName{"pt"}= "Portugal";
$tldName{"pr"}= "Puerto Rico";
$tldName{"qa"}= "Qatar";
$tldName{"re"}= "Reunion";
$tldName{"ro"}= "Romania";
$tldName{"ru"}= "Russia";
$tldName{"rw"}= "Rwanda";
$tldName{"bl"}= "Saint Barthelemy";
$tldName{"sh"}= "Saint Helena, Ascension, and Tristan da Cunha";
$tldName{"kn"}= "Saint Kitts and Nevis";
$tldName{"lc"}= "Saint Lucia";
$tldName{"mf"}= "Saint Martin";
$tldName{"pm"}= "Saint Pierre and Miquelon";
$tldName{"vc"}= "Saint Vincent and the Grenadines";
$tldName{"ws"}= "Samoa";
$tldName{"sm"}= "San Marino";
$tldName{"st"}= "Sao Tome and Principe";
$tldName{"sa"}= "Saudi Arabia";
$tldName{"sn"}= "Senegal";
$tldName{"rs"}= "Serbia";
$tldName{"sc"}= "Seychelles";
$tldName{"sl"}= "Sierra Leone";
$tldName{"sg"}= "Singapore";
$tldName{"sx"}= "Sint Maarten";
$tldName{"sk"}= "Slovakia";
$tldName{"si"}= "Slovenia";
$tldName{"sb"}= "Solomon Islands";
$tldName{"so"}= "Somalia";
$tldName{"za"}= "South Africa";
$tldName{"gs"}= "South Georgia and the Islands";
$tldName{"es"}= "Spain";
$tldName{"lk"}= "Sri Lanka";
$tldName{"sd"}= "Sudan";
$tldName{"sr"}= "Suriname";
$tldName{"sj"}= "Svalbard";
$tldName{"sz"}= "Swaziland";
$tldName{"se"}= "Sweden";
$tldName{"ch"}= "Switzerland";
$tldName{"sy"}= "Syria";
$tldName{"tw"}= "Taiwan";
$tldName{"tj"}= "Tajikistan";
$tldName{"tz"}= "Tanzania";
$tldName{"th"}= "Thailand";
$tldName{"tl"}= "Timor-Leste";
$tldName{"tg"}= "Togo";
$tldName{"tk"}= "Tokelau";
$tldName{"to"}= "Tonga";
$tldName{"tt"}= "Trinidad and Tobago";
$tldName{"tn"}= "Tunisia";
$tldName{"tr"}= "Turkey";
$tldName{"tm"}= "Turkmenistan";
$tldName{"tc"}= "Turks and Caicos Islands";
$tldName{"tv"}= "Tuvalu";
$tldName{"ug"}= "Uganda";
$tldName{"ua"}= "Ukraine";
$tldName{"ae"}= "United Arab Emirates";
$tldName{"uk"}= "United Kingdom";
$tldName{"us"}= "United States";
$tldName{"um"}= "United States Minor Outlying Islands";
$tldName{"uy"}= "Uruguay";
$tldName{"uz"}= "Uzbekistan";
$tldName{"vu"}= "Vanuatu";
$tldName{"ve"}= "Venezuela";
$tldName{"vn"}= "Vietnam";
$tldName{"vi"}= "Virgin Islands";
$tldName{"vg"}= "Virgin Islands (UK)";
$tldName{"vi"}= "Virgin Islands (US)";
$tldName{"wf"}= "Wallis and Futuna";
$tldName{"ps"}= "West Bank";
$tldName{"eh"}= "Western Sahara";
$tldName{"ws"}= "Western Samoa";
$tldName{"ye"}= "Yemen";
$tldName{"zm"}= "Zambia";
$tldName{"zw"}= "Zimbabwe";
$tldName{"xx"}= "HAMCLOUD";

1;
