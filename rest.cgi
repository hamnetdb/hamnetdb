#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Simple REST Interface
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
# Bernd Strehhuber, DM8BS
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
do "lib.cgi" or die;
#
# Queries by Call from Hamnet Sites

if ($query->param('m') eq "querycall") {
  print("Content-Type: application/json\nExpires: 0\n\n");
  &json_obj();
  my $callsign=lc($query->param('call'));
  if ($callsign =~ /^[a-z]{1,2}[0-9][a-z]{1,3}(-\d{1,2})?$/ || $callsign =~ /^nocall_\d+$/) {
    my $search = $db->quote($callsign);
    my $sth= $db->prepare(qq(
      select callsign,latitude,longitude,elevation from hamnet_site
           where callsign=$search));
    $sth->execute;
    if ($sth->rows == 0) {
      &json_var("No site found","error");
    } 
    elsif ($sth->rows > 1) {
      # This should never happen
      &json_var("More than one site found","error");
    } 
    elsif ($sth->rows == 1) {
      my $result = $sth->fetchrow_hashref(); 
      &json_obj("querycall_result", 0);
      &json_var($result->{'callsign'}, "callsign");
      &json_var($result->{'latitude'}, "latitude");
      &json_var($result->{'longitude'}, "longitude");
      &json_var($result->{'elevation'}, "elevation");
      &json_obj_end(0);
    }          
  } 
  else {
    &json_var("Wrong callsign Format","error");
  }
  &json_obj_end();
} 
else {
  # Wrong use of Rest API -> Redirect .)
  print qq(Status: 302 Moved\n).
        qq(Location: $baseUri\n\n);
}

exit 0;
