#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Edge input form
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

$suffix= "edge";
$table= "hamnet_$suffix";
$table_history= "${table}_hist";
$requiredPermission= "subnet";

($left_site,$left_host,$right_site,$right_host,$typ,$radioparam,$comment)=
  &loadFormData
  ("left_site,left_host,right_site,right_host,typ,radioparam,comment");

$caption= "Change $suffix '$left_site:$right_site'";
$caption= "New $suffix" unless $id;
&beforeForm($caption);

print qq(
  <tr>
  <td valign="top" align="left">Left site:<br>
      <b style="font-size: 20px">$left_site</b>
      <input type="hidden" name="left_site" value="$left_site">
  </td>
  <td valign="top" align="left">Right site:<br>
      <b style="font-size: 20px">$right_site</b>
      <input type="hidden" name="right_site" value="$right_site">
  </td>
  </tr>
);

my $sth= $db->prepare(qq(select site,name,ip
    from hamnet_host 
    where site in ('$left_site','$right_site') order by name
));
$sth->execute;
while (@line= $sth->fetchrow_array) {
  if ($line[0] eq $left_site) {
    push(@left_hosts, "$line[2]::$line[1] - $line[2]");
  }
  if ($line[0] eq $right_site) {
    push(@right_hosts, "$line[2]::$line[1] - $line[2]");
  }
}
print qq(
  <tr>
  <td valign="top" align="left" nowrap>
  Left radio host (if any):<br>
);
&comboBox("", "left_host-300", $left_host, "-None-", @left_hosts);
print qq(
  </td>
  <td valign="top" align="left" nowrap>
  Right radio host (if any):<br>
);
&comboBox("", "right_host-300", $right_host, "-None-", @right_hosts);

print qq(
  </td>
  </tr>
  <tr>
  <td valign="top" align="left" nowrap colspan="1">Topology type:<br>
);

&comboBox("", "typ", $typ, "Radio",  "Ethernet",  "Tunnel", "ISM");

print qq(
  <br>
  </td>
  </tr>

  <tr>
  <td valign="top" align="left" nowrap colspan=2>
  <p>Radio config parameters 
  (Common parameters for whole edge, maybe site-specific see host):<br>
  <input type="text" name="radioparam" value="$radioparam" 
         style="width:100%"$chtrack>
  </td>
  </tr>
  <tr><td colspan=2>
  <p>Comment area:<br>
  <textarea name="comment" class="txt" $chtrack
            style="width:100%; height:170px;">$comment</textarea>
  </td></tr>
  <script>
  if ($id==0 && '$left_site' !='') {
    changed();
  }
  </script>
);
&afterForm;
exit;


# --------------------------------------------------------------------------
# check and store values
sub checkValues {
  $comment.= "";
  $radioparam= &alignRadioparam($radioparam);

  return  "comment=".$db->quote($comment).", ".
          "typ=".$db->quote($typ).", ".
          "left_site=".$db->quote($left_site).", ".
          "left_host=".$db->quote($left_host).", ".
          "right_site=".$db->quote($right_site).", ".
          "right_host=".$db->quote($right_host).", ".
          "radioparam=".$db->quote($radioparam);
}

