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
push @INC,'.';
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
#left
#$width= 800  if $width<400;
$width= 4000+0 if ($width>4000);
$height= 250;


unless($profile_path_program)
{
  $hwtimg="https://hamnetdb.net/";
}

$hwtimg.= "rftools/calc_profile.cgi".
 "?lat_a=$siteLat{$left}&lon_a=$siteLong{$left}&ant_a=$siteElev{$left}".
 "&lat_b=$siteLat{$right}&lon_b=$siteLong{$right}&ant_b=$siteElev{$right}".
 "&f=5800&wood=30&name_a=$left&name_b=$right".
 "&w=$width&h=$height";

print qq(
  <img src="$hwtimg" width=$width height=$height>
);

