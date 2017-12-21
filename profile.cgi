#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Show terrain profile using heywhatsthat.com
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
do "lib.cgi" or die;
#
print("Content-Type: text/html\nExpires: 0\n\n");

my $width= $query->param("width")+0;
my $right= $query->param("right");
my $left= $query->param("left");

my $sth= $db->prepare(qq(
  select callsign,id,name,latitude,longitude,elevation
  from hamnet_site where callsign in (?,?)
));
$sth->execute($left,$right);

while (@line= $sth->fetchrow_array) {
  my $idx= 0;
  my $callsign= $line[$idx++];
  $siteId{$callsign}=   $line[$idx++];
  $siteName{$callsign}= $line[$idx++];
  $siteLat{$callsign}=  $line[$idx++];
  $siteLong{$callsign}= $line[$idx++];
  $siteElev{$callsign}= $line[$idx++];
}

unless ($siteId{$left} && $siteId{$right}) {
  print("<h3>Not all sites where found</h3>");
  exit;
}

#$width= 800  if $width<400;
$width= 3200 if $width>3200;
$height= 250;

#$hwtimg= "http://profile.heywhatsthat.com/bin/profile-0904.cgi".
# "?pt0=$siteLat{$left},$siteLong{$left},c00000,$siteElev{$left}".
# "&pt1=$siteLat{$right},$siteLong{$right},c00000,$siteElev{$right}".
# "&axes=1&metric=1&groundrelative=1&curvature=1&freq=5800".
# "&width=$width&height=$height&src=hamnetdb.net";

$hwtimg= "calc_profile.cgi".
 "?lat_a=$siteLat{$left}&lon_a=$siteLong{$left}&ant_a=$siteElev{$left}".
 "&lat_b=$siteLat{$right}&lon_b=$siteLong{$right}&ant_b=$siteElev{$right}".
 "&f=5800".
 "&w=$width&h=$height";

#<div style='float:right;margin-top:5px;font-size:80%'>
#  Profile image is Copyright 2012 Michael Kosowsky. 
#  All rights reserved. Used with permission. For more information visit
#  <a target='blank' href='http://www.heywhatsthat.com/'>HeyWhatsThat</a>.
#  </div>

print qq(
  <img src="$hwtimg" width=$width height=$height>
);

