#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - interactive traceroute
#
# Lucas Speckbacher, OE2LSP
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
# action
#   trace
#   chktrace 
#   startele
#   stopele
#
# ?
# test start feature
# test stop ping

push @INC,'.';

use JSON;
use LWP::UserAgent;
do "lib.cgi" or die;

my $action= $query->param("m");
my $debug= $query->param("d")+0;
my $start= $query->param("start");
my $stopIP= $query->param("stopIP");
my $stopSite= $query->param("stop");
$stopIP =~ s/\/.*//; #cut off anything else

my $url= $monitoring_API;
#if ($action eq "chktrace") {
  print("Content-Type: text/html\nExpires: 0\n\n");
#}
#else 
#{
#  print qq(Content-Type: application/json filename=hamnetdb-map.json\n\n);
#}

unless ($myPermissions=~/$t,/) {
  print "not allowed without login";
  die;
}

my @startSites= &getStartSites();

#check source site and destination IP for frontend 
if ($action eq "chktrace") {
  #site 2 target-IP
  my $startIP= chkstart($start);
  my $errorMsg;
  unless ($startIP) {
    $errorMsg= "start point invalid"
  }
  #check stop IP
  if (!$errorMsg && length($stopIP >= 7)) {
    my $ip= chkstopip($stopIP);
    unless ($ip) {
      $errorMsg= "stop IP-address not valid";
    }
  }
  #use stopsite
  if (!$errorMsg && length($stopIP) < 7) {
    $stopIP=GetIpForSite($stopSite);
    unless ($stopIP) {
      $errorMsg= "stop point not valid"
    }
  }
  unless ($errorMsg) {
    print "ok";
  }
  else {
    print $errorMsg;
  }
}

#perform traceroute
if ($action eq "trace") {
  #check source & destination
  #   ip->host->site
  #print mapelelements
  my $startIP= chkstart($start);
  my $errorMsg;
  unless ($startIP) {
    $errorMsg= "start point invalid"
  }

  #check stop IP
  if (!$errorMsg && length($stopIP >= 7)) {
    my $ip= chkstopip($stopIP);
    unless ($ip) {
      $errorMsg= "stop IP-address not valid";
    }
  }

  #use stopsite
  if (!$errorMsg && length($stopIP) < 7) {
    $stopIP=GetIpForSite($stopSite);
    unless ($stopIP) {
      $errorMsg= "stop point not valid"
    }
  }
  my @traces_out;
  #start site 
  $start_param= GetSiteForIP($startIP);
  if ($debug) {
    print "\nTo:$stopIP\n",$startIP," ",$start_param->{'site'}," ",$start_param->{'lat'}," ",$start_param->{'lon'},"\n";
  }
  $row->{'site'}= $start_param->{'site'};
  $row->{'lon'}= $start_param->{'lon'};
  $row->{'lat'}= $start_param->{'lat'};
  $row->{'ip'}= $startIP;
  push @traces_out, $row;

  #api call

  my $url_trace= $url."/tools/traceroute/$startIP/$stopIP/1";
  my $response_trace=  get_api_data($url_trace);
  my $decoded_json= decode_json($response_trace);

  foreach my $entry (@{$decoded_json->{'hops'}}) { 
    unless ($entry->{'status'} eq "Ok" || $entry->{'status'} eq "Unstable") {
      $errorMsg= $entry->{'status'}."; ".$entry->{'info'}."   +++\n";
      if ($debug) {
        print "error128: ",$entry->{'status'},$entry->{'info'},"   ---\n";
      }
      next;
    }
    my $row = {};
    $site_param= GetSiteForIP($entry->{'address'});
    if ($debug) {
      print $entry->{'address'}," ";
      print $site_param->{'site'}," ",$site_param->{'lat'}," ",$site_param->{'lon'},"\n";
    }
    $row->{'site'}= $site_param->{'site'};
    $row->{'lon'}= $site_param->{'lon'}+0;
    $row->{'lat'}= $site_param->{'lat'}+0;
    $row->{'ip'}= $entry->{'address'};
    next if ($row->{'lon'} == 0 && $row->{'lat'} == 0);
    push @traces_out, $row;
  }
  if ($errorMsg) {
    print "Error: ",$errorMsg;
  }
  #print $url_trace;
  
  traceOut(@traces_out);
}

if ($action eq "startele")
{
  elementsOut(@startSites);
}

if ($action eq "stopele")
{
  my @stopsites= &getStopSites();
  elementsOut(@stopsites);
}

##what for?
sub siteToStartIp {
  #??  
}

sub GetSiteForIP {
  my $ip_in= shift;
  my $row= {};

  $sql= qq(select h.site, s.longitude, s.latitude 
    from `hamnet_host` as h 
    join hamnet_site as s 
      on h.site = s.callsign
    where h.ip = '$ip_in' 
    limit 1
  );
  my $sth= $db->prepare($sql);
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    $row->{'site'}= $line[$idx++];
    $row->{'lon'}= $line[$idx++];
    $row->{'lat'}= $line[$idx++];
    return $row;
  }
  return 0;
}

sub GetIpForSite {
  my $site= shift; 
  my $ip;
  #first try router.CALL
  #OR first IP from Site-Network
  my $sql= qq(select h.ip, h.name, h.aliases from hamnet_host as h
    join hamnet_check as c 
      on h.ip = c.ip
    where (h.name= "router.$site" 
      or h.aliases like "%router.$site%")
      and c.ts > (unix_timestamp(NOW())-7200)
    limit 1);
  my $sth= $db->prepare($sql);
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $ip= $line[$idx++];
    my $name= $line[$idx++];
    my $aliases= $line[$idx++];
    if ($name eq "router.$site") {
      return $ip;
    }
    if ($aliases =~ /(,|^)router\.$site(,|\z)/) {
      return $ip;
    }
  }
  #print "no router.call\n";
  $sql= qq(select h.ip, s.typ 
    from `hamnet_host` as h 
    join hamnet_subnet as s 
      on h.rawip < s.end_ip and h.rawip > s.begin_ip
    join hamnet_check as c 
      on h.ip = c.ip
    where h.site = '$site' 
      and c.ts > (unix_timestamp(NOW())-7200)
    order by FIELD(s.typ, "Backbone-Network","User-Network","Service-Network","Site-Network") asc, h.rawip asc
    limit 1
  );
  my $sth= $db->prepare($sql);
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    $ip= $line[$idx++];
    return $ip;
  }
  return 0;
}

#check if start site is vaild
sub chkstart {
  my $site= shift; 
  foreach my $row (@startSites) {
    if ($row->{'site'} eq $site) {
      return $row->{'ip'};
    }
  }
  return 0;
}

#check stop ip
sub chkstopip {
  my $ip_chk= shift;
  my $ip;
  $sql= qq(select ip, site
        from hamnet_host  
        where 
          ip = '$ip_chk' 
  );
  my $sth= $db->prepare($sql);
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    $ip= $line[$idx++];
    return 1;
  }
  return 0;
}
sub getStartSites {
  my @sites_out;
  my $sql= qq(select h.site, s.longitude, s.latitude, h.ip 
    from `hamnet_host` as h 
    join hamnet_site as s on h.site = s.callsign
    join hamnet_check as c on c.ip = h.ip
    where c.service = "traceroute" and 
      unix_timestamp(c.ts) > (unix_timestamp(NOW())-129600*2)
  );
  my $sth= $db->prepare($sql);
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $row;
    $row->{'site'}= $line[$idx++];
    $row->{'lon'}= $line[$idx++];
    $row->{'lat'}= $line[$idx++];
    $row->{'ip'}= $line[$idx++];
    $row->{'action'}= "tracestart";
    push @sites_out, $row;
  }
  return @sites_out;
}
sub getStopSites {
  my @sites_out;
  my $sql= qq(select h.site, s.longitude, s.latitude, h.ip 
    from `hamnet_host` as h 
    join hamnet_site as s on h.site = s.callsign
    join hamnet_check as c on c.ip = h.ip
    where unix_timestamp(c.ts) > (unix_timestamp(NOW())-7200)
    and c.status
    group by h.site
  );
  my $sth= $db->prepare($sql);
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $row;
    $row->{'site'}= $line[$idx++];
    $row->{'lon'}= $line[$idx++];
    $row->{'lat'}= $line[$idx++];
    $row->{'ip'}= $line[$idx++];
    $row->{'action'}= "tracestop";
    push @sites_out, $row;
  }
  return @sites_out;
}
sub getStartSitesApi {
  #http://monitoring.hc-i.r1.ampr.org/api/v1/tools/hostsSupportingFeature/traceroute
  #{
  #  "description": "RouterOS RB750Pr2",
  #  "contact": "",
  #  "location": "",
  #  "name": "router.db0zm",
  #  "uptime": null,
  #  "model": "RB750Pr2",
  #  "version": "6.45.1",
  #  "maximumSnmpVersion": "Ver1",
  #  "address": "44.225.20.193",
  #  "errorDetails": [],
  #  "supportedFeatures": [
  #    "Rssi",
  #    "BgpPeers",
  #    "Traceroute"
  #  ],
  #  "defaultApi": "VendorSpecific",
  #  "lastDataUpdate": "2019-12-31T00:14:08.317254"
  #},
  my @sites_out;
  my $url_startsites= $url."/tools/hostsSupportingFeature/traceroute";
  my $response_startsites=  get_api_data($url_startsites);
  my @decoded_json= @{decode_json($response_startsites)};
  foreach my $entry (@decoded_json) { 
    my $row= {};
    #print $entry->{'address'},"\n";
    $IP= $entry->{'address'},"\n";
    
    $sql= qq(select s.callsign, s.longitude, s.latitude, h.ip
            from hamnet_site as s
            join hamnet_host as h 
              on h.site = s.callsign
            join hamnet_check as c 
              on c.ip = h.ip
          where 
            h.ip = '$IP' and 
            UNIX_TIMESTAMP(c.ts) > (UNIX_TIMESTAMP(CURRENT_TIMESTAMP())-7200)
          limit 1
      );
    my $sth= $db->prepare($sql);
    $sth->execute;
    while (@line= $sth->fetchrow_array) {
      my $idx= 0;
      $row->{'site'}= $line[$idx++];
      $row->{'lon'}= $line[$idx++];
      $row->{'lat'}= $line[$idx++];
      $row->{'ip'}= $line[$idx++];
#      print $row->{'site'},"\n";
    }
    push @sites_out, $row;
  } 
  return @sites_out;
}
sub elementsOut {
  my @sites_out= @_; 

  &json_obj();
  &json_var("FeatureCollection","type")
  &json_obj("features", 1);
  foreach my $row (@sites_out) {
    my @f= split(/;/, $site);
    &json_obj();
      &json_var("Feature","type");
      &json_obj("geometry",0)
        &json_var("Point","type");
        &json_obj("coordinates",1);
          &json_var($row->{'lon'},0);
          &json_var($row->{'lat'},0);
        &json_obj_end(1);
      &json_obj_end();
      &json_obj("properties",0);
        &json_var($row->{'site'}, "callsign");
        &json_var($row->{'action'}, "action");
        &json_var("site-trace", "style");
        &json_var(0, "zIndex");
      &json_obj_end();
    &json_obj_end();
  }
  &json_obj_end(1);
  &json_obj_end();
}

sub traceOut {
  my @traces_out= @_; 

  &json_obj();
  &json_var("FeatureCollection","type")
  &json_obj("features", 1);

  &json_obj();
    &json_var("Feature","type");
    &json_obj("geometry",0)
      &json_var("LineString","type");
      &json_obj("coordinates",1);
        foreach $row (@traces_out) {
          &json_obj(0,1);
            &json_var($row->{'lon'},0);
            &json_var($row->{'lat'},0);
          &json_obj_end(1);
        }
      &json_obj_end(1);
    &json_obj_end();
    &json_obj("properties",0);
      &json_var(trace, "style");
  &json_obj_end();
  &json_obj_end();
  &json_obj_end(1);    
  &json_obj_end();
}