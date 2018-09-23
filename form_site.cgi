#!/usr/bin/perl -w
# -------------------------------------------------------------------------
# Hamnet IP database - Site input form
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
# Hubertus Munz
# Lucas Speckbacher, OE2LSP
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
push @INC,'.';
do "form.cgi" or die;

$suffix= "site";
$table= "hamnet_$suffix";
$table_history= "${table}_hist";
$requiredPermission= $suffix;

$width="140px";


($name,$callsign,$longitude,$latitude,$elevation,$no_check,
      $radioparam,$comment,$maintainer,$rw_maint,$newCover,$hasCover)= &loadFormData
("name,callsign,longitude,latitude,elevation,no_check,radioparam,comment,maintainer,rw_maint,newCover,hasCover");

$newCover+= 0;
$hasCover+= 0;
$elevation+= 0;

#Coverage-Table: new or hist?
if ($newversion && $id) {
  $hamnet_coverage = "hamnet_coverage_hist";
}
else {
  $hamnet_coverage= "hamnet_coverage";
}




&checkMaintainerRW($rw_maint, $maintainer);
unless ($maintainer) {
  $rw_maint= 0;
}


$caption= "Change $suffix '$name'";
$caption= "New $suffix" unless $id;

if ($func eq "delete") {
  my $dep= &siteDependency($callsign);
  if ($dep) {
    $func= "store";
    $inputStatus= "Cannot delete: $dep";
  }
}
$locator= calcLocator($longitude,$latitude);
&beforeForm($caption);


my $Cover;

$elevation= "" if $elevation==0;
$callsign= "" if $callsign=~/^nocall/;

$mapHamnet=checkMapSource();



print qq(

  <tr>
  <td valign="top" align="left" nowrap colspan=1>Callsign:<br>
    <input type="text" name="callsign" value="$callsign" style="width:$width;"$chtrack>
   <br>
  </td>
  <td valign="top" align="left" nowrap colspan=1>Location Name:<br>
    <input type="text" name="name" value="$name" style="width:$width;" $chtrack>
  </td>
  <td colspan=4 valign="top" align="left" nowrap>
  Type of this site:
  <br>
);
if($mySysPerm || ($no_check == 5 && &checkMaintainerRW(1, $maintainer))) {
  &comboBox("", "no_check", $no_check, 
          "0::Hamnet-site",
          "1::Special hamnet-site (ignore position in map)",
          "4::ISM-site",
          "2::No hamnet on site (e.g. FM-repeater)",
          "3::Site without callsign (for planning)",
          "5::Virtual hamnet-site (e.g. Hamcloud)");
}
else {
  &comboBox("", "no_check", $no_check, 
          "0::Hamnet-site",
          "1::Special hamnet-site (ignore position in map)",
          "4::ISM-site",
          "2::No hamnet on site (e.g. FM-repeater)",
          "3::Site without callsign (for planning)");
}
print qq(
  </td>
  </tr>
  <tr>
  <td valign="top" align="left" nowrap colspan=1>
    Latitude (e.g. 48.0):<br>
    <input type="text" name="latitude" value="$latitude" style="width:$width;"
     $chtrack onkeyup="calcLocatorjs()" id="latitude">
  </td>
  <td valign="top" align="left" nowrap colspan=1>Longitude (e.g. 11.0):<br>
    <input type="text" name="longitude" value="$longitude" style="width:$width;"
      $chtrack onkeyup="calcLocatorjs()" id="longitude">
  </td>
  <td valign="top" align="left" nowrap colspan=1>or 10-digit Locator:<br>
  <input type="text" name="locator" value="$locator" style="width:$width;"  
    $chtrack onkeyup="calcCoordinates();" id="locator">
  </td>
  <td valign='top' style='padding-top: 8px;' colspan=1>
    <a href="javascript:hamnetdb.positionShow($mapHamnet)"><img src="map.png" height="30px" width="30px" /></a>
    <small style="display:inline-block">Hint: <br><a $mapHamnet 
      href="javascript:hamnetdb.positionShow($mapHamnet)">pick coordinates from map</a></small>
  </td>
</tr>
<tr>
<td valign="top" align="left" nowrap colspan=1>Meters above ground:<br>
    <input type="text" name="elevation" value="$elevation" 
      $chtrack style="width:$width;">
</td>

);
print qq(
<td colspan=3><br>);

&checkBox("Prepare Coverage?", "Cover", $hasCover, $Cover);

print qq(
  <small>See main page
    <a target="_blank" href="index.cgi?m=help#antenna">Help</a>
    for infos on radio propagation.
    </small>
  </td></tr>
</table>
<div style='margin:10px;'></div>
<script src="osm/leaflet.js"></script>
);

unless(checkMapSource())
{
  print qq(
    <script src="osm/es6-promise.auto.js"></script><script>ES6Promise.polyfill();</script>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyA58LI1avl5xzd8mj9LLidnBVhRHGoaAsA" async defer></script> 
    <script src="osm/Leaflet.GoogleMutant.js"></script>
  );
}


print qq(
<link rel="stylesheet" type="text/css" href="osm/leaflet.css" />
<link rel="stylesheet" type="text/css" href="osm/style-lf.css" />
<script type="text/javascript" src="osm/leaflet.ajax.js"></script>
<script src="osm/L.Control.MousePosition.js"></script>
<script src="osm/L.Control.MiniMap.js"></script>
<script src="osm/L.Control.Sidebar.js"></script>
<script src="osm/Permalink.js"></script>
<script src="osm/Permalink.Marker.js"></script>
<script src="osm/Permalink.Layer.js"></script>
<script src="osm/Permalink.Overlay.js"></script>
<script src="osm/L.Control.LSP.js"></script>
<script src="osm/hamnetdb-position.js"></script>
);


print qq(
<table width="100%">

  <tr><td colspan=8> 
  <h4>Hamnet User Access / Antenna Configuration </h4>
  </td> 
);

my $counter=0;


my $sth= $db->prepare("select name from hamnet_antennafiles order by name");
$sth->execute;
while (@line= $sth->fetchrow_array) {
  push(@antenna, "$line[0]");
}

print qq(
  <td style="display:none">
);

&comboBox("", "antenna_dummy", " ", "::-None-", @antenna);

print qq(
    </td>
  </tr>
);
############################################################################################################
my $rows=0;
my $lines= 0;
my $counter=1;
if($mustLoadFromDB){
  $accessh = $db->prepare("select tag,frequency,power,gain,cableloss,antennatype,azimuth,altitude from $hamnet_coverage where callsign='$callsign' and version='$version'");
  $accessh->execute();
  #necessary because number of lines unknown
  if(($tag,$frequency,$power,$gain,$cableloss,$antennatype,$azimuth,$altitude) = $accessh->fetchrow_array())
  {
    $lines=1;  
  }
}
else{
  if($query->param("addAnt"))
  {  
    $lines= $query->param("addAnt")-1;
  }
}



while($lines) 
{

  #Get access data (frequencies,power,gain,antennatype,closs,tag) from $hamnet_coverage or query
  $lines--; 
  unless($mustLoadFromDB)
  {

    $frequency=$query->param("frequency$counter");
    $azimuth=$query->param("azimuth$counter");
    $altitude=$query->param("altitude$counter");
    $antennatype=$query->param("antennatype$counter");
    $tag=$query->param("tag$counter");
    $power=$query->param("power$counter");
    $gain=$query->param("gain$counter");
    $cableloss=$query->param("cableloss$counter");

  }

  #For each user access there need to a different frequency (but might also be the same for every access point)
  $_freq="frequency$counter";
  $_tag="tag$counter";
  $_alt="altitude$counter";
  $_az="azimuth$counter";
  $_ant="antennatype$counter";
  $_tag="tag$counter";
  $_pow="power$counter";
  $_loss="cableloss$counter";
  $_gain="gain$counter";


  print qq(
  <tr id="plusUser$counter">
    <td valign="top" align="left" nowrap width="90px">
      &nbsp; &nbsp; Label:<br />
      <a id="delete$counter" href="javascript:hamnetdb.removeUserAccess($counter)"> 
        <img src="delete.png"> </a> 
      <input type="text" name="$_tag" value ="$tag" style="width:50px;"$chtrack>  
      
  </td>
  <td valign="top" align="left" nowrap width="110px">
    Frequency: <br />
    <input type="text" name="$_freq" value="$frequency" style="width:70px;"$chtrack>MHz
  </td valign="top" align="left" nowrap>
  <td valign="top" align="left" nowrap>
    Elevation: <br />
    <input type="text" name="$_alt" value="$altitude" style="width:60px;"$chtrack>°
  </td>
  <td valign="top" align="left" nowrap>
    Azimuth:<br />
    <input type="text" name="$_az" value="$azimuth" style="width:60px;"$chtrack>°
  </td>-
  <td valign ="top" align ="left"nowrap> 
    Power:<br />
    <input type="text" name="$_pow" value="$power" style="width:50px;"$chtrack>dBm
  </td>
  <td valign ="top" align ="left"nowrap> 
    Antennagain:<br />
    <input type="text" name="$_gain" value="$gain" style="width:50px;"$chtrack>dBi
  </td>
  <td valign ="top" align ="left"nowrap> 
    Cableloss:<br />
    <input type="text" name="$_loss" value="$cableloss" style="width:50px;"$chtrack>dB
  </td>
  
  <td valign="top" align="left" nowrap class="select_site_width">Antennatype:<br>
  );


  &comboBox("", "$_ant", $antennatype, "::-None-", @antenna);


  print qq(
       <br><a id="show$counter" href="javascript:hamnetdb.antennaShow($counter,'0');"> Show selected Pattern </a>
       </td>
    </tr>
  );
  $counter++;
  if($mustLoadFromDB)
  {
    if(($tag,$frequency,$power,$gain,$cableloss,$antennatype,$azimuth,$altitude) = $accessh->fetchrow_array())
    {
      $lines=1;  
    }
    else
    {
      last;
    }
    
  }
#  if($counter==5)
#  {
#    last;
#  }
  
}


print qq(
  <tr id="plusUser$counter"></tr>
  <tr id="menu"><td colspan=8>
  <a href="javascript:hamnetdb.addUserAccess($counter)">
     Add additional User Access / Antenna Configuration</a>
  </td>
  </tr>

  <tr><td colspan=8>
  <input type="hidden" name="addAnt" value="$counter">
  <a href="javascript:hamnetdb.edit('antenna')">Upload/Remove Antenna Pattern</a>
  </td>
</tr>
<tr><td>&nbsp;</td></tr>
<tr>
  <td  valign="top" align="left" nowrap colspan=8>
  Radio config parameters for user access (only for user information; leave empty without user access):<br>
  <input type="text" name="radioparam" value="$radioparam" style="width:100%"$chtrack>
  </td>
  </tr>
  <tr>
  <td valign="top" align="left" nowrap colspan=8>
      List of maintainers (callsigns, comma separated):<br>
  <input type="text" name="maintainer" value="$maintainer" style="width:100%"$chtrack>
  </td>
  </tr>
  <tr><td colspan=8>
);


if (&inList($username, $maintainer) || ($maintainer && $mySysPerm)) {
  &checkBox("Restrict write access to list of site maintainers",
            "rw_maint", 0, $rw_maint);
}

print qq(
  </td></tr>
  <tr><td colspan=8>
  <br>
  </td>
  </tr>
  <tr><td colspan=8>
  Comment area:<br>
  <textarea name="comment" class="txt" $chtrack
            style="width:100%; height:55px;">$comment</textarea>
  </td></tr></table><table width="100%">
);
&afterForm;
exit;

# --------------------------------------------------------------------------
# check and store values
sub checkValues 
{
  
  $Cover = $query->param("Cover");
  $callsign= lc $callsign;
  my $orig= lc $query->param("callsign_orig");
  if ($id && $orig && $callsign ne $orig) {
    $orig=~s/[^0-9a-z\-]//g;
    my $dep= &siteDependency($orig);
    if ($dep) {
      $inputStatus= "Cannot rename: $dep";
    }
  }

  $latitude= &degmin2dec($latitude);
  $longitude= &degmin2dec($longitude);
  if ($latitude<-180 || $latitude>180) 
  {
    $inputStatus= "Latitude is out of range";
  }
  if ($longitude<-180 || $longitude>180) {
    $inputStatus= "Longitude is out of range";
  }
  if (($longitude == 0 && $latitude == 0)|| $longitude eq "" || $latitude eq "")
  {
    $inputStatus= "Longitude and Latitude can't be 0, or Locator too short."
  }
  
  $rw_maint+= 0;

  if ($callsign eq "") {
    if ($no_check!=3) {
      $inputStatus= "Callsign is missing (maybe use type 'without callsign')";

    }
    else {
      if ($id) {
        $callsign= "nocall_$id";
      }
      else {
        $callsign= "nocall_".time;
      }
    }
  }
  elsif ($no_check==5) {
     #all ok 
     my $test = 0;
  }    
  else {
    unless ($callsign=~/^[a-z0-9]{3,6}-*\d*$/ && $callsign=~/[0-9][a-z]-*\d*/) {
      $inputStatus= "Callsign seems to have incorrect format";
    }
    if ($no_check==3) {
      $inputStatus= "Callsign is defined but site type is 'without callsign'";
    }
  }
  unless ($name) {
    $inputStatus= "Name is missing";
  }
  unless ($inputStatus) {
    if ($db->selectrow_array("select callsign from $table ".
          "where callsign='$callsign' and id<>'$id'")) {
      $inputStatus= "The site '$callsign' exists already";
    }
  }

  #virtual hamnet site only for sysadmin or maintainers
  if ($no_check == 5) {
    &checkMaintainerRW(1, $maintainer);    
  }

  if($Cover == 1){
    $hasCover = 1;
    if($ischanged ==1){
      #change in comment shall not envoke a new prediction...
      $newCover = 1;
    }

  }

  $maintainer= lc $maintainer;
  &checkMaintainerRW($rw_maint, $maintainer);
  $radioparam= &alignRadioparam($radioparam);

  &checkAntenna();


  return  "comment=".$db->quote($comment).", ".
          "callsign=".$db->quote($callsign).", ".
          "maintainer=".$db->quote($maintainer).", ".
          "latitude=".$db->quote($latitude).", ".
          "longitude=".$db->quote($longitude).", ".
          "elevation=".$db->quote($elevation).", ".
          "no_check=".$db->quote($no_check).", ".
          "rw_maint=".$db->quote($rw_maint).", ".
          "radioparam=".$db->quote($radioparam).", ".
          "name=".$db->quote($name).",".
          "newCover=".$db->quote($newCover).",".
          "hasCover=".$db->quote($hasCover);
}

sub deleteAccess
{
  $db->do("delete from hamnet_coverage where callsign='$callsign'");
}

sub addAccess
{
  $numAnt = $query->param("addAnt");

  my $vers_handle = $db->prepare("select version from hamnet_site where callsign='$callsign'");
  $vers_handle->execute();
  $version = $vers_handle->fetchrow_array();
  
  #update not possible, no index to refer to
  $db->do("delete from hamnet_coverage where callsign='$callsign'");
  
  for(my $k = 1; $k < $numAnt; $k++)
  {
    my $fr=$query->param("frequency$k");
    my $azi=$query->param("azimuth$k");
    my $alt=$query->param("altitude$k");
    my $ant=$query->param("antennatype$k");
    my $t=$query->param("tag$k");
    my $p=$query->param("power$k");
    my $g=$query->param("gain$k");
    my $c=$query->param("cableloss$k");
   
    $db->do("insert into hamnet_coverage ".
            "(site_id,callsign,altitude,azimuth,antennatype,gain,power,cableloss,frequency,tag,version,edited) ".
            "values ('$id','$callsign','$alt', '$azi', '$ant', '$g', '$p','$c','$fr','$t','$version',NOW())");
            
    $db->do("insert hamnet_coverage_hist select * ".
                             "from hamnet_coverage where callsign='$callsign'");  
  }
}


sub checkAntenna
{
  $numAnt = $query->param("addAnt"); #number of accesses
  $Cover = $query->param("Cover");
  @tags;

  if($Cover == 1 && $numAnt == 1)
  {
    $inputStatus="Add at least one User Access/Antenna Configuration!";
  }
 
 
  if(($no_check == 1 || $no_check == 2 || $no_check == 3) && ($Cover == 1 || $numAnt > 1 ))
  {
    $inputStatus="This site has no hamnet, so there can't be an antenne for an hamnet useraccess"; 
  }
  for(my $k = 1; $k<$numAnt; $k++)
  {
    #*************************Antenna- label*************************
    
    my $t=$query->param("tag$k");
    unless($inputStatus)
    {
      if($t =~ /:/)
      {
        $inputStatus="At least one antenna-Label seems to have incorrect format (No '_',':' or empty space allowed):  $t";
      }
      if($t =~/_/)
      {
        $inputStatus="At least one antenna-Label seems to have incorrect format (No '_',':' or empty space allowed): $t";
      }
      if($t =~/ /)
      {
        $inputStatus="At least one antenna-Label seems to have incorrect format (No '_',':' or empty space allowed):  $t";
      }
      unless($t)
      {
        $inputStatus="At least one antenna-Label seems to have incorrect format (No '_',':' or empty space allowed):  $t";
      }
        #$inputStatus="dreck";
        if ( grep { $_ eq $t} @tags )
        {
          $inputStatus="antenna-Label must be unique for this site!";
        }  
  
      push(@tags, $t);
      
    }      
    #*************FREQUENCY********************************

    my $fr=$query->param("frequency$k");

    unless($inputStatus)
    {
      if($fr =~/[^0-9]/)
      {
        $inputStatus="At least one invalid frequency: $fr";
      }
      if($fr =~/:/)
      {
        $inputStatus="At least one invalid frequency: $fr";
      }
      if($fr==0 || $fr eq "" || $fr eq " ")
      {
        $inputStatus="Enter all frequencies to determine Propagation.";
      }
      if($fr < 1000 || $fr > 10000)
      {
        $inputStatus="The Frequency $fr is out of range. See instructions. (VHF/UHF calcuation is impossible)"; 
      }
    }
#******************AZIMUTH****************************

    my $azi=$query->param("azimuth$k");

    unless($inputStatus)
    {
      if($azi < 0 || $azi > 360)
      {
        $inputStatus="At least One Azimuth angle is out of range. See instructions."; 
      }
      if($azi=~/[^0-9]/)
      {
        $inputStatus="At least one invalid azimuth angle: $azi";
      }
      if($azi =~/:/)
      {
        $inputStatus="At least one invalid azimuth angle: $azi";
      }
    }
#*********************ELEVATION***************************

    my $alt=$query->param("altitude$k");
    
    unless($inputStatus)
    {
      if($alt < -270 || $alt > 90)
      {
        $inputStatus="At least one elevation angle is out of range. See Instructions."; 
      }
      if($alt=~/[^0-9-]/)
      {
        $inputStatus="At least one invalid elevation angle: $alt";
      }
      if($alt =~/:/)
      {
        $inputStatus="At least one invalid elevation angle: $alt";
      }
    }
#***********************ANTENNATYPE***************************

    my $ant=$query->param("antennatype$k");
    unless($inputStatus)
    {
      if($ant eq "")
      {
        $inputStatus="There is no antennatype defined";
      }
    }
#***************************POWER***********************

    my $p=$query->param("power$k");
    unless($inputStatus)
    { 
      if($Cover == 1 && $p <= 0 )
      {
        $inputStatus="Enter only power values greater than 0 to determine Propagation.";
      }
      if($p=~/[^0-9-]/)
      {
        $inputStatus="At least one invalid power value: $p";
      }
      if($p =~/:/)
      {
        $inputStatus="At least one invalid power value: $p";
      }
    }
#*************************GAIN************************

    my $g=$query->param("gain$k");
    unless($inputStatus)
    {
      if($g < 0 || $g > 100)
      {
        $inputStatus="At least one Gain is out of range"; 
      }
      if($g=~/[^0-9]/)
      {
        $inputStatus="At least one invalid gain value: $g";
      }
      if($g=~/:/)
      {
        $inputStatus="At least one invalid gain value: $g";
      }
    }
#*************************CABLELOSS************************

    my $c=$query->param("cableloss$k");
    unless($inputStatus)
    {
      if($c < 0 || $c > 100)
      {
        $inputStatus="At least one Cableloss out of range"; 
      }
      if($c=~/[^0-9]/)
      {
        $inputStatus="At least one invalid cableloss value: $c";
      }
      if($c =~/:/)
      {
        $inputStatus="At least one invalid cableloss value: $c";
      }
    }
#*************************************************
  }
  
}
