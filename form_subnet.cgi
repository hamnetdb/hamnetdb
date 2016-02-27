#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Subnet input form
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

$suffix= "subnet";
$table= "hamnet_$suffix";
$table_history= "${table}_hist";
$requiredPermission= $suffix;

($ip,$typ,$as_num,$as_parent,$dhcp_range,$radioparam,$comment,$rw_maint)= 
  &loadFormData
  ("ip,typ,as_num,as_parent,dhcp_range,radioparam,comment,rw_maint");

if ($mustLoadFromDB) {
  if ($ip=~m#([\d\.]+)/(\d+)#) {
    $base_ip= $1;
    $bits= $2;
  }
}
else {
  $base_ip= $query->param("base_ip");
  $bits= $query->param("bits");
  $as_parent= $query->param("as");
}

# If possible, fetch maintainer-list from AS since a subnet has no maintainers
# Do it only if AS is also locked, otherwise it would not have any effect
my $maintainer= "";
if ($as_parent>0) {
  ($maintainer)= $db->selectrow_array(qq(select maintainer from hamnet_as
    where rw_maint>0 and as_num=).$db->quote($as_parent));

  &checkMaintainerRW($rw_maint, $maintainer);
}        
unless ($maintainer) {
  $rw_maint= 0;
}

$caption= "Change $suffix '$ip'";
$caption= "New $suffix" unless $id;
&beforeForm($caption);

print qq(
  <tr>
  <td valign="top" align="left" nowrap>Base IP:<br>
  <input type="text" name="base_ip" value="$base_ip" size=20$chtrack id="base_ip" onkeyup="calcfromIP();"> / 
  </td>
  <td valign="top" align="left" nowrap>Address mask:<br>
  <select name="bits" onchange="calcfromIP();"  >
);

my $netmask= 0xffffffff;
for ($power= 1; $power <= 16; $power++) {
  my $restbits= (32-$power);
  print("<option value=\"$restbits\"");
  if ($bits == $restbits || (!$bits && $restbits==29)) {
    print(" selected");
  }
  $num= 1 << $power;
  $num= ($num/1024)."k" if $num>1024;
  $netmask<<=1;
  my $amask= &ntoa($netmask);
  print(">$restbits &nbsp;&nbsp;&nbsp; ($amask = $num IPs)\n");
}

print qq(
  </select></td>
  <td></td>
  </tr>
  <tr>
    <td><small id="netaddr_limits"></small></td>
    <td colspan="1"><a href="javascript:hamnetdb.ipcalcShow();">Show full IP-calculator</a></td></tr>
  <tr>
  <td valign="top" align="left" nowrap>Type of network:<br>
);

&comboBox("", "typ", $typ, "Backbone-Network", "Site-Network", 
   "Service-Network", "User-Network", "AS-Backbone", "AS-User/Services",
   "AS-Packet-Radio");

$as_num= "" unless $as_num;

print qq(
  <td valign="top" align="left" nowrap>
  User-access DHCP-range (last ip digit start-end or empty):<br>
  <input type="text" name="dhcp_range" value="$dhcp_range" size=20$chtrack>
  </td>
  <td></td>
  </tr>
  <tr>
  <td valign="top" align="left" nowrap>Parent AS:<br>
  );
  $as_parent= &asCombo(0,0,1,$as_parent);
print qq(
  </td>
  <td valign="top" align="left" nowrap>Own AS number (only useful for type 'Site-Network'):<br>
  <input type="text" name="as_num" value="$as_num" size=10$chtrack>
  </td>
  <td></td>
  </tr>
  <tr>
  <td valign="top" align="left" nowrap colspan=4>
  <p>Radio config parameters 
  (Only common parameters for whole subnet, for site-specific see host):<br>
  <input type="text" name="radioparam" value="$radioparam" style="width:100%"$chtrack>
  </td>
  </tr>
  <tr><td colspan=4>
);

if (&inList($username, $maintainer) || ($mySysPerm && $maintainer)) {
  &checkBox("Restrict write access to list of parent AS maintainers",
            "rw_maint", 1, $rw_maint);
}

print qq(
  </td></tr>
  <tr><td colspan=3>
  <p>Comment area:<br>
  <textarea name="comment" class="txt" $chtrack
            style="width:100%; height:170px;">$comment</textarea>
  </td></tr>
);
&afterForm;
exit;


# --------------------------------------------------------------------------
# check and store values
sub checkValues {
  $as_num=~s/as *//i;
  $as_num+=0;
  if ($as_num && $as_num<64512) {
    $inputStatus= "Own AS must be above 64512 or empty";
  }
  $as_parent=~s/as *//i;
  $as_parent+=0;
  if ($as_parent && $as_parent<64512) {
    $inputStatus= "Parent AS must be above 64512 or empty";
  }
  if ($base_ip=~/^(\d+\.\d+\.\d+\.\d+)\/(\d+)$/) {
    $base_ip= $1;
    $bits= $2;
  }
  $ip= "$base_ip/$bits";

  unless (&ipCheck($base_ip)) {
    $inputStatus= "The base IP is not a valid IP address";
  }
  unless ($base_ip) {
    $inputStatus= "The base IP is missing";
  }
  unless ($bits) {
    $inputStatus= "The netmask is missing";
  }
  unless ($inputStatus) {
    $netmask= 0;
    for ($i= 0; $i < 32; $i++) {
      if ($i >= (32-$bits)) {
        $netmask|= (1 << $i);
      }
    }
    if (&aton($base_ip) != (&aton($base_ip) & $netmask)) {
      $base_ip= &ntoa(&aton($base_ip) & $netmask);

      $inputStatus= "The base IP was aligned to $base_ip, store again";
    }
  }
  unless ($inputStatus) {
    $ip= $base_ip."/".$bits;

    if ($db->selectrow_array("select ip from $table ".
          "where ip='$ip' and id<>'$id'")) {
      $inputStatus= "The network '$ip' exists already";
    }
    $begin_ip= &aton($base_ip);
    $end_ip=   $begin_ip + (1<<(32-$bits));
  }
  if ($dhcp_range) {
    unless ($dhcp_range=~/^\d+\-\d+$/) {
      $inputStatus= "DHCP range must be <begin>-<end> of last IP digit";
    }
  }
  
  $radioparam= &alignRadioparam($radioparam);

  $rw_maint+= 0;
  &checkMaintainerRW($rw_maint, $maintainer);

  return  "comment=".$db->quote($comment).", ".
          "ip=".$db->quote($ip).", ".
          "typ=".$db->quote($typ).", ".
          "dhcp_range=".$db->quote($dhcp_range).", ".
          "radioparam=".$db->quote($radioparam).", ".
          "rw_maint=".$db->quote($rw_maint).", ".
          "begin_ip=$begin_ip,".
          "end_ip=$end_ip,".
          "as_parent=$as_parent,".
          "as_num=$as_num";
}
