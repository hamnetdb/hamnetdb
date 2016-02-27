#!/usr/bin/perl 
# -------------------------------------------------------------------------
# Hamnet IP database - Return antenna-coverage of site
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
do "config.cgi" or die;
do "lib.cgi" or die;

my @input=(" "," ");

my @input = split(/_/,$query->param("x"));

my $site = $input[0];

my @coordinates= ();
my $status;
my @tags =();

$hamnet_coverage="hamnet_coverage";

my $newCoverh=$db->prepare("select newCover,version from hamnet_site where callsign='$site'");
$newCoverh->execute; 
($newCover,$version)=$newCoverh->fetchrow_array;

if($newCover ==1)
{
 $hamnet_coverage="hamnet_coverage_hist";
 $version = $version - 1;
}


if($input[1] eq "")
{

  my $tagh= $db->prepare("SELECT tag FROM $hamnet_coverage WHERE Callsign='$site' and version='$version'");
  $tagh->execute();

  while(my $tag = $tagh->fetchrow_array())
  {
    push(@tags,$tag);
  }
  $sth= $db->prepare("SELECT callsign,status,north,south,west,east FROM $hamnet_coverage WHERE Callsign = '$site' and status='ok'and version='$version'");

}
else
{
  @tags = $input[1];

  $sth= $db->prepare("SELECT Callsign,Status,North,South,West,East FROM $hamnet_coverage WHERE Callsign = '$site' AND Tag ='@tags' and status='ok' and version='$version'");

}

$sth->execute;
my @data = $sth->fetchrow_array();

$site = $data[0];
$status = @data[1];
$coordinates[0] = $data[2];
$coordinates[1] = $data[3];
$coordinates[2] = $data[4];
$coordinates[3] = $data[5];



#Coverage for this Site not available in Database
if($site eq "")
{
  print qq(Content-Type: text/plain\n\n);
  print qq(0);
}
else
{
#Parse JSON/GeoJSON File to Script

 print qq(Content-Type: text/plain\n\n);
 print qq({
    "North":$coordinates[0],
    "South": $coordinates[1], 
    "West":$coordinates[2], 
    "East":$coordinates[3],
    "Status":"$status",
    "Callsign":"$site",
    "Tag":"@tags"
  } \n\n);
}



