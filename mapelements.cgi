#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Generate list of map elements
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
use Fcntl qw(:flock);
do "lib.cgi" or die;

# Supply these parameters if we want to limit the result
my $only_as=     $query->param("only_as")+0;
my $only_hamnet= $query->param("only_hamnet")+0;
my $only_country=$query->param("only_country");
$only_country=~s/[^a-z]+//g;
my $no_hamnet=   $query->param("no_hamnet")+0;
my $no_tunnel=   $query->param("no_tunnel")+0;
my $no_radio=    $query->param("no_radio")+0;
my $no_ism=      $query->param("no_ism")+0;
my $radio=        $query->param("radio")+0;
my $geojson=     $query->param("geojson")+0;
#print qq(Content-Type: text/plain\nExpires: 0 \n\n);
# The result arrays which are rendered as JSON or GeoJSON
my @allSites= ();
my @allEdges= ();

# allow only one instance "semaphor"
check_process(1);

# Read realtime monitoring results for appropriate site-symbols
my %siteStatus= &hostsStatus(1, 1); # all hosts, group to sites

# -------------------------------------------------------------------------
# Determine country for AS
if ($only_country) {
  my $sth= $db->prepare(qq(select as_num,country from hamnet_as));
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $as= $line[$idx++];
    my $country= $line[$idx++];

    $as_country{$as}= $country;
  }
}

# -------------------------------------------------------------------------
# Determine sites for AS - HACK: prefer Service hosts by sorting
if ($only_country || $only_as) {
  my $sth= $db->prepare(qq(select hamnet_host.site,hamnet_subnet.as_parent 
    from hamnet_subnet
    left join hamnet_host on hamnet_host.rawip between begin_ip and end_ip 
    where hamnet_host.site<>'' 
    order by hamnet_host.typ
  ));
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $site= $line[$idx++];
    my $as= $line[$idx++];

    $site_as{$site}= $as;
  }
}
# -------------------------------------------------------------------------
# Fetch all sites
my $sth= $db->prepare(qq(
  select callsign,longitude,latitude,no_check,radioparam
  from hamnet_site
));
#  order by callsign
$sth->execute;

while (@line= $sth->fetchrow_array) {
  my $idx= 0;
  my $callsign= $line[$idx++];
  my $longitude= $line[$idx++];
  my $latitude= $line[$idx++];
  my $no_check= $line[$idx++];
  my $radioparam= $line[$idx++];

  if ($latitude<-180 | $latitude>180) {
    next;
  }
  if ($longitude<-180 | $longitude>180) {
    next;
  }

  $site_lat{$callsign}= $latitude;
  $site_long{$callsign}= $longitude;

  if ($only_as) {
    next if ($site_as{$callsign} != $only_as)
  }
  if ($only_country) {
    $site_country{$callsign}= $as_country{$site_as{$callsign}};
    next unless $site_country{$callsign} eq $only_country;
  }

  my $zIndex= 10;
  my $siteAdd= "";
  $siteAdd= "-user" if $radioparam;

  # The siteStatus contains complete image definition, just extract
  # the color since other symbols are used in the map context.
  if ($no_check>1 && $no_check<4) {
    $siteAdd= "-grey";
    $zIndex= 1;
  }
  elsif ($siteStatus{$callsign}=~/(green|red).png/) {
    if ($siteStatus{$callsign}=~/green/) {
      $siteAdd.= "-green";
      $zIndex= 20;
    }
    else {
      $siteAdd.= "-red";
      $zIndex= 5;
    }
  }
  $zIndex++ if $radioparam;

  my $zi= sprintf("%03d", $zIndex);
  my $useBounds= ($no_check==1)?0:1;
  my $hasHamnet= ($no_check<2 || $no_check==4)?1:0;
  my $as= 0;
  if($only_as || $only_country) {
    $as= $site_as{$callsign};
  }

  #my $country= $as_country{$site_as{$callsign}};
  next if (($only_hamnet && !$hasHamnet) || ($no_hamnet && $hasHamnet));

  push(@allSites, 
    "$zi;$callsign;$as;$latitude;$longitude;$siteAdd;$useBounds;".
    "$hasHamnet" #;$country
  );
}

# -------------------------------------------------------------------------
# Prepare edges extracted from transfer subnets
my $sth= $db->prepare(qq(select hamnet_host.ip,hamnet_subnet.ip, 
  hamnet_host.typ,hamnet_subnet.typ,
  hamnet_host.radioparam,hamnet_subnet.radioparam,
  hamnet_host.site,
  hamnet_subnet.begin_ip, hamnet_subnet.end_ip
  from hamnet_subnet
  left join hamnet_host on hamnet_host.rawip between begin_ip and end_ip
  where hamnet_subnet.typ like 'Backbone-%'
));
#as_parent,
$sth->execute;
while (@line= $sth->fetchrow_array) {
  my $idx= 0;
  my $host_ip= $line[$idx++];
  my $subnet_ip= $line[$idx++];
  my $host_typ= $line[$idx++];
  my $subnet_typ= $line[$idx++];
  my $host_radioparam= $line[$idx++];
  my $subnet_radioparam= $line[$idx++];
  #my $as_parent= $line[$idx++];
  my $site= $line[$idx++];
  my $begin_ip= $line[$idx++];
  my $end_ip= $line[$idx++];

  $all_host_types{$host_ip}= $host_typ;

  $type_count{$subnet_ip}{$host_typ}++ if $site;
  $all_hosts{$subnet_ip}{$host_ip}= 1;
  $host_site{$host_ip}= $site;
  $subnet_begin{$subnet_ip}= $begin_ip;
  $subnet_end{$subnet_ip}= $end_ip;
}

foreach $net (sort keys %all_hosts) {
  for $typ ("Routing-Radio", "Routing-ISM", "Routing-Tunnel", "Routing-Ethernet") {
    if ($type_count{$net}{$typ} == 2) {
      my @sites= ();
      foreach $host (sort keys %{$all_hosts{$net}}) {
        if ($all_host_types{$host} eq $typ) {
          push(@sites, $host_site{$host});
        }
      }
      if ($only_as) {
        next if ($site_as{$sites[0]} ne $only_as ||
                 $site_as{$sites[1]} ne $only_as)
      }
      if ($only_country) {
        next if ($site_country{$sites[0]} ne $only_country &&
                 $site_country{$sites[1]} ne $only_country)
      } 
      
      next if (($no_tunnel && $typ=~/tunnel/i) || ($no_tunnel && $typ=~/ethernet/i) || ($no_radio && $typ=~/radio/i) || ($no_ism&& $typ=~/ISM/i));

      #get rssi
      my $style=$typ;
      if ($radio) {
        #get worst rssi
        #get net boundary
#        my $begin_ip;
#        my $end_ip;
#        my $sth= $db->prepare(qq(select 
#          begin_ip, end_ip
#          from hamnet_subnet
#          where 
#          ip='$net'
#        ));
#        $sth->execute;
#        while (@line= $sth->fetchrow_array) {
#          my $idx= 0;
#          $begin_ip= $line[$idx++];
#          $end_ip= $line[$idx++];
#        }
        #left monitored host -> rssi
        my $monitor_left;
        my $sth= $db->prepare(qq(select 
          ip
          from hamnet_host
          where 
          monitor=1 and rawip > $subnet_begin{$net} and 
          rawip < $subnet_end{$net} and site='$sites[0]'
        ));
        $sth->execute;
        while (@line= $sth->fetchrow_array) {
          my $idx= 0;
          $monitor_left= $line[$idx++];
        }
        #right monitored host -> rssi
        my $monitor_right;
        $sql=qq(select 
          ip
          from hamnet_host
          where 
          monitor=1 and rawip > $subnet_begin{$net} and 
          rawip < $subnet_end{$net} and site='$sites[1]'
        );
        my $sth= $db->prepare($sql);
        $sth->execute;
        while (@line= $sth->fetchrow_array) {
          my $idx= 0;
          $monitor_right= $line[$idx++];
        }
        my $rssi; 
        my $rssi2; 
        $rssi=linkStatus($monitor_left,'rssi');
        $rssi2=linkStatus($monitor_right,'rssi');
        next if ((length($rssi) <2 ) && (length($rssi2) <2 ));
        if((length($rssi) >1 ) && (length($rssi2) >1 )) {
          $rssi = $rssi+0;
          $rssi2 = $rssi2+0;
          $rssi= $rssi2 if $rssi > $rssi2; #get worst side and apply style
          if   ($rssi>-66) {$style= 'hf1';} 
          elsif($rssi>-71) {$style= 'hf2';} 
          elsif($rssi>-76) {$style= 'hf3';} 
          elsif($rssi>-81) {$style= 'hf4';} 
          elsif($rssi>-86) {$style= 'hf5';} 
          elsif($rssi>-99) {$style= 'hf6';} 
          else             {$style= 'hf7';} 
        }
      } 
      push(@allEdges, "$style;$net;$sites[0];$sites[1]");
    }
  }
}

# -------------------------------------------------------------------------
# Prepare edges explicitely stored in the database
my $sth= $db->prepare(qq(select left_site,right_site,hamnet_edge.typ
  from hamnet_edge
));
$sth->execute;
while (@line= $sth->fetchrow_array) {
  my $idx= 0;
  my $left_site= $line[$idx++];
  my $right_site= $line[$idx++];
  my $typ= $line[$idx++];

  if ($only_country) {
    next if ($site_country{$left_site} ne $only_country &&
             $site_country{$right_site} ne $only_country)
  }
  next if (($no_tunnel && $typ=~/tunnel/i) || ($no_radio && $typ=~/radio/i) || ($no_ism && $typ=~/ISM/i) || ($radio));
  push(@allEdges, "$typ;$left_site:$right_site;$left_site;$right_site");
}

#only GeoJSON, old map no longer exists
# ------------------------ GeoJSON part ---------------------------------------
#if ($geojson) {
  print qq(Content-Type: text/plain\nExpires: 0 \n\n);
  
  &json_obj();
  &json_var("FeatureCollection","type")
    &json_obj("features", 1);
  foreach $edge (reverse sort @allEdges) {
    my @f= split(/;/, $edge);
    &json_obj();
      &json_var("Feature","type");
      &json_obj("geometry",0)
        &json_var("LineString","type");
        &json_obj("coordinates",1);
          &json_obj(0,1);
            my $site= $f[2];
            &json_var($site_long{$site},0);
            &json_var($site_lat{$site},0);
          &json_obj_end(1);
          &json_obj(0,1);
            my $site= $f[3];
            &json_var($site_long{$site},0);
            &json_var($site_lat{$site},0);
          &json_obj_end(1);
        &json_obj_end(1);
      &json_obj_end();
      &json_obj("properties",0);
        &json_var($f[2].":".$f[3], "callsign");
        &json_var($f[0], "style");
      &json_obj_end();
    &json_obj_end;
  }
  
  foreach $site (sort @allSites) {
    my @f= split(/;/, $site);
    &json_obj();
      &json_var("Feature","type");
      &json_obj("geometry",0)
        &json_var("Point","type");
        &json_obj("coordinates",1);
          &json_var($f[4],0);
          &json_var($f[3],0);
        &json_obj_end(1);
      &json_obj_end();
      &json_obj("properties",0);
        &json_var($f[1], "callsign");
        &json_var($f[2], "as");
        &json_var("site".$f[5], "style");
        &json_var($f[0]+0, "zIndex");
      &json_obj_end();
    &json_obj_end();
  }
  &json_obj_end(1);
  &json_obj_end();
#}
# ------------------------ JSON part ---------------------------------------
# else { 
#   print("Content-Type: application/json\nExpires: 0\n\n");
#   &json_obj();
#   &json_obj("edge", 1);
#   foreach $edge (reverse sort @allEdges) {
#     my @f= split(/;/, $edge);
#     &json_obj;
#     &json_var($f[0], "typ");
#     &json_var($f[1], "link");
#     &json_obj("left");
#     { 
#       my $site= $f[2];
#       &json_var($site, "site");
#       &json_var($site_lat{$site}, "latitude");
#       &json_var($site_long{$site}, "longitude");
#       &json_var($site_as{$site}, "as");
#     }
#     &json_obj_end;
#     &json_obj("right");
#     { 
#       my $site= $f[3];
#       &json_var($site, "site");
#       &json_var($site_lat{$site}, "latitude");
#       &json_var($site_long{$site}, "longitude");
#       &json_var($site_as{$site}, "as");
#     }
#     &json_obj_end;
#     &json_obj_end;
#   }
#   &json_obj_end(1);

#   &json_obj("site", 1);
#   foreach $site (sort @allSites) {
#     my @f= split(/;/, $site);
#     &json_obj();
#     &json_var($f[1], "callsign");
#     &json_var($f[2], "as");
#     &json_var($f[3], "latitude");
#     &json_var($f[4], "longitude");
#     &json_var("site".$f[5].".png", "icon");
#     &json_var($f[0]+0, "zIndex");
#     &json_var($f[6], "useBounds");
#     &json_var($f[7], "hasHamnet");
#     &json_var($f[8], "country");
#     &json_obj_end();
#   }
#   &json_obj_end(1);
#   &json_obj_end();
# }

sub check_process { 
  my $first= shift;

  unless ($first) {
    sleep(1);
  }
  open our $file, '<', $0 or die $!;
  flock $file, LOCK_EX or check_process(0);
  flock $file, LOCK_EX|LOCK_NB or die "Unable to lock file $!";
}