#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Run checks of live network
#
# Remark: This program calls agents by ssh and relies on an installed
# fping with setuid root and a key-based ssh connecton to the agent.
# The agent hosts have to be defined in config.cgi
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
# Lucas Speckbacher, OE2LSP, http://www.radlherr.de
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
# search for sites coordinates and proxy nominatim => json for OSM-search
use lib qw(.);

use JSON;
use LWP::UserAgent;
do "lib.cgi" or die;

my $in= $query->param("q");
$search= $db->quote($in);
$dbsearch= $db->quote('%'.$in.'%');

my @sites;


print("Content-Type: application/json\n\n");

my $sth= $db->prepare("select callsign, name, longitude, latitude from hamnet_site where name like $dbsearch or callsign like $dbsearch ORDER by callsign, name LIMIT 10");
$sth->execute;
while (@line= $sth->fetchrow_array) 
{
  $callsign= $line[0];
  $name= $line[1];
  $lon= $line[2];
  $lat= $line[3];

  my $teil = {'lon' => $lon.'', 'lat' => $lat.'', 'display_name' => $callsign.' | '.$name };
  push(@sites, $teil);
}

my $json = JSON->new->utf8->pretty->encode(\@sites);
my $nominatimResult= get_nominatim("https://nominatim.openstreetmap.org/search?format=json&q=$search");
my @decoded_json = @{decode_json($nominatimResult)};

foreach my $entry (@decoded_json) { 
  push(@sites,$entry);
}

my $json = JSON->new->utf8->pretty->encode(\@sites);
print "$json\n";


#{"place_id":"198256193",
#  "licence":"Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
# "osm_type":"relation","osm_id":"1585661","boundingbox":["47.7526974","47.8065181","13.143272","13.2199784"],
# "lat":"47.7906849","lon":"13.175644",
# "display_name":"Ebenau, Salzburg-Umgebung, Salzburg, 5323, Austria",
# "class":"boundary",
# "type":"administrative",
# "importance":0.49359754255688904,
# "icon":"https://nominatim.openstreetmap.org/images/mapicons/poi_boundary_administrative.p.20.png"}


sub get_nominatim{
  $url=shift;
 
  my $ua      = LWP::UserAgent->new(); 
  $ua->timeout(120);
  my $request = HTTP::Request->new(GET => $url);

  my $response = $ua->request($request);
  if ($response->is_success) {
    my $message = $response->decoded_content;
    #print "Received reply: $message\n";
    return $message;
  }
  else {
    print "HTTP POST error code: ", $response->code, "\n";
    print "HTTP POST error message: ", $response->message, "\n";
  }

}
