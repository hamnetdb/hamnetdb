#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Host input form
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
do "form.cgi" or die;

$suffix= "host";
$table= "hamnet_$suffix";
$table_history= "${table}_hist";
$requiredPermission= $suffix;

($name,$ip,$rawip,$mac,$aliases,$typ,$radioparam,$site,$no_ping,$monitor,
  $comment,$rw_maint)= &loadFormData
  ("name,ip,rawip,mac,aliases,typ,radioparam,site,no_ping,monitor,comment,rw_maint");

$no_ping+= 0;
$monitor+= 0;

# If possible, fetch maintainer-list from site since a host has no maintainers
# Do it only if site is also locked, otherwise it would not have any effect
my $maintainer= "";
if ($site) {
  ($maintainer)= $db->selectrow_array(qq(select maintainer from hamnet_site
    where rw_maint>0 and callsign=).$db->quote($site));

  #$name= ".$site" unless $id;
  unless($id) {
      $name= ".$site" unless $ip;
  }
  #if($id1) {
  #  $name= ".$site"
  #}
  &checkMaintainerRW($rw_maint, $maintainer);
  
}
unless ($maintainer) {
  $rw_maint= 0;
}

if ($mustLoadFromDB) {
  if ($radioparam=~s/^ap *(bridge|)//i) {
    $radio_mode= "AP Bridge";
  }
  if ($radioparam=~s/^sta(tion|)//i) {
    $radio_mode= "Station";
  }
  if ($radioparam=~s/^ *wds//i) {
    $radio_mode.= " WDS";
  }
  if ($radioparam=~s/ *\(*nstreme\)*//i) {
    $radio_mode.= " (NStreme)";
  }
  if ($radioparam=~s/ *\(*airmax\)*//i) {
    $radio_mode.= " (AirMax)";
  }
  $radioparam=~s/^[\s,]*//;
  $radio_remarks= $radioparam;
}
else {
  $radio_mode= $query->param("radio_mode");
  $radio_remarks= $query->param("radio_remarks");
}

$caption= "Change $suffix '$name'";
$caption= "New $suffix $maintainer" unless $id;
&beforeForm($caption);

print qq(
  <tr>
  <td valign="top" align="left" nowrap>IP:<br>
  <input type="text" name="ip" value="$ip" size=12$chtrack>
  <br>$br10
  </td>
  <td colspan=2 valign="top" align="left" nowrap>Host name (end with .callsign):<br>
  <input type="text" name="name" value="$name" size=25$chtrack>
  </td>
  <td valign="top" align="left" nowrap>MAC of radio interface:<br>
  <input type="text" name="mac" value="$mac" size=15$chtrack>
  </td>
  </tr>
  <tr>
  <td valign="top" align="left" nowrap colspan="1" >Host type:<br>
);

$typ= "Service" unless $typ;

&comboBox("", "typ", $typ, 
          "Routing-Radio", "Routing-ISM", "Routing-Ethernet", "Routing-Tunnel",
          "Service");

print qq(
  <br>$br10
  </td>
  <td valign="top" align="left" nowrap colspan=2 class="select_max_width" >Belonging to site:<br>
);

my $sth= $db->prepare("select ".
         "callsign,name from hamnet_site order by callsign");
$sth->execute;
while (@line= $sth->fetchrow_array) {
  next if $line[0]=~/nocall/;
  push(@sites, "$line[0]::$line[0] - $line[1]");
}
&comboBox("", "site", $site, "::-None-", @sites);

print qq(
  </td>
  <td>
);

&checkBox("No ping check", "no_ping", 1, $no_ping);

&checkBox("Monitor", "monitor", 1, $monitor);
print qq(
  </td>
  </tr>
  <tr>
  <td valign="top" align="left" nowrap colspan=4>
     DNS aliases (CNAME, optional, end with .callsign):<br>
  <input type="text" name="aliases" value="$aliases" style="width:100%"$chtrack>
  </td>
  </tr>
  <tr>
  <td style="padding-top:15px;padding-bottom:15px"
      valign="top" align="left" nowrap colspan=4>
  Radio config parameters 
  (only site-specific parameters, for common see subnet):<br>
);

&comboBox("Mode:", "radio_mode", $radio_mode, "", 
  "AP Bridge (NStreme)",
  "AP Bridge (AirMax)",
  "AP Bridge",
  "Station WDS (NStreme)",
  "Station (AirMax)",
  "Station");

print qq(
  Remarks: <input type="text" name="radio_remarks" value="$radio_remarks" 
         style="width:400px"$chtrack>
  </td>
  </tr>
  <tr><td colspan=4 style='padding-bottom:10px'>
);

if (&inList($username, $maintainer) || ($maintainer && $mySysPerm)) {
  &checkBox("Restrict write access to list of site maintainers",
            "rw_maint", 1, $rw_maint);
}

print qq(
  </td></tr>
  <tr><td colspan=4>
  Comment area:<br>
  <textarea name="comment" class="txt" $chtrack
            style="width:100%; height:160px;">$comment</textarea>
  </td></tr>
);
&afterForm;
exit;


# --------------------------------------------------------------------------
# check and store values
sub checkValues {
  $name= lc $name;
  unless ($name) {
    $inputStatus= "Name is missing";
  }
  if ($name=~/[^0-9a-z\-\.]/) {
    $inputStatus= "Name contains invalid characters";
  }
  unless (&ipCheck($ip)) {
    $inputStatus= "IP is not a valid IP address";
  }
  $rw_maint+= 0;

  $radioparam= $radio_mode;
  $radioparam.= "," if $radio_remarks && $radioparam;
  $radioparam.= $radio_remarks;
  $radioparam= &alignRadioparam($radioparam);
  &checkMaintainerRW($rw_maint, $maintainer);
  if (! $site) {
    $inputStatus= "Host must be assigned to a site";
  }
  
  unless ($inputStatus) {
    #no callsign check for virtual site
    unless ($db->selectrow_array("select callsign, no_check from hamnet_site  ".
              "where callsign='$site' and no_check=5")){
      unless ($name=~/[a-z][0-9]+[a-z]+-*\d*$/) {
        $inputStatus= 
          "Host name must end with a callsign to be globally unique";
      } 
    }
  }

  if ($mac) {
    $mac= lc $mac;
    $mac=~s/[^0-9a-f]//g;
    if (length($mac)!=12) {
      $inputStatus= "Invalid mac address - empty or 12 hex digits";
    }
  }
  unless ($inputStatus) {
    if ($name=~/^\./) {
      $inputStatus= "first charater of Host name can't be '.' ";
    }
  }
    
  unless ($inputStatus) {
    if ($db->selectrow_array("select ip from $table ".
          "where ip='$ip' and id<>'$id'")) {
      $inputStatus= "The host '$ip' exists already";
    }
    if ($db->selectrow_array("select name from $table ".
          "where name='$name' and id<>'$id'")) {
      $inputStatus= "The host '$name' exists already";
    }
  }
  unless ($inputStatus) {
    $aliases= lc $aliases;
    if ($aliases) {
      my $al;
      foreach $alias (split(/[\s,;]+/, $aliases)) {
        if ($db->selectrow_array("select name from $table ".
            "where name='$alias' and id<>'$id'")) {
          $inputStatus= "The alias '$alias' exists already as host";
          last;
        }
        unless ($alias=~/[a-z][0-9]+[a-z]+$/) {
          $inputStatus= 
            "Alias '$alias' must end with a callsign to be globally unique";
          last;
        }
        if ($alias=~/[^0-9a-z\-\.]/) {
          $inputStatus= "Alias contains invalid characters";
          last;
        }
        $al.= "," if $al;
        $al.= $alias;
      }
      unless ($inputStatus) {
        $aliases= $al;
      }
    }
  }
  unless($inputStatus) {
    if ($typ eq "Routing-Radio"){
      if ($db->selectrow_array("select callsign, no_check from hamnet_site  ".
              "where callsign='$site' and no_check=4 or no_check=5")) {
            $inputStatus= "This type of site can't have host of type \"Routing-Radio\"";
      }
    }
    elsif ($typ eq "Routing-ISM"){
      if ($db->selectrow_array("select callsign, no_check from hamnet_site  ".
              "where callsign='$site' and no_check=5")) {
            $inputStatus= "This type of site can't have host of type \"Routing-ISM\"";
      }
    }
  }
  $rawip= &aton($ip);
  return  "comment=".$db->quote($comment).", ".
          "ip=".$db->quote($ip).", ".
          "typ=".$db->quote($typ).", ".
          "mac=".$db->quote($mac).", ".
          "aliases=".$db->quote($aliases).", ".
          "radioparam=".$db->quote($radioparam).", ".
          "site=".$db->quote($site).", ".
          "no_ping=".$db->quote($no_ping).", ".
          "monitor=".$db->quote($monitor).", ".
          "rw_maint=".$db->quote($rw_maint).", ".
          "rawip=".$db->quote($rawip).", ".
          "name=".$db->quote($name);
}
