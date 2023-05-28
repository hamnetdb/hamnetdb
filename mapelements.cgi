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
push @INC,'.';
use Fcntl qw(:flock);
use Time::HiRes;
do "lib.cgi" or die;

# Supply these parameters if we want to limit the result
my $only_as=     $query->param("only_as")+0;
my $only_hamnet= $query->param("only_hamnet")+0;
my $only_country= $query->param("only_country");
my $only_radio= $query->param("only_radio");
$only_country=~s/[^a-z]+//g;
my $no_hamnet=   $query->param("no_hamnet")+0;
my $no_tunnel=   $query->param("no_tunnel")+0;
my $no_radio=    $query->param("no_radio")+0;
my $no_ism=      $query->param("no_ism")+0;
my $radio=       $query->param("radio")+0;
my $bgp=         $query->param("bgp")+0;
my $sponsor=     $query->param("sponsor")+0;
my $geojson=     $query->param("geojson")+0;
#print qq(Content-Type: text/plain\nExpires: 0 \n\n);
# The result arrays which are rendered as JSON or GeoJSON
my @allSites= ();
my @allEdges= ();
# allow only one instance "semaphor" otherwise deadlock
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
    left join hamnet_host on hamnet_host.rawip between begin_ip and end_ip-1 
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
  select callsign,longitude,latitude,no_check,radioparam,elevation
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
  my $elevation= $line[$idx++];

  if ($latitude<-180 | $latitude>180) {
    next;
  }
  if ($longitude<-180 | $longitude>180) {
    next;
  }

  $site_lat{$callsign}= $latitude;
  $site_long{$callsign}= $longitude;
  $site_no_check{$callsign}= $no_check;
  $site_radioparam{$callsign}= $radioparam;
  $site_elevation{$callsign}= $elevation;
  push(@allCallsigns,"$callsign");
}

# -------------------------------------------------------------------------
# Prepare edges extracted from transfer subnets
my $sth= $db->prepare(qq(select hamnet_host.ip,hamnet_subnet.ip, 
  hamnet_host.typ,hamnet_subnet.typ,
  hamnet_host.radioparam,hamnet_subnet.radioparam,
  hamnet_host.site,
  hamnet_subnet.begin_ip, hamnet_subnet.end_ip-1
  from hamnet_subnet
  left join hamnet_host on hamnet_host.rawip between begin_ip and end_ip-1
  where hamnet_host.ip is not null and hamnet_subnet.typ like 'Backbone-%'
));
#as_parent,
#
$sth->execute;
while (@line= $sth->fetchrow_array) {
#while (0) {
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
#if (0) {
  for $typ ("Routing-Radio", "Routing-ISM", "Routing-Tunnel", "Routing-Ethernet") {
    if ($type_count{$net}{$typ} == 2) {

#into sql?          
      my @sites= ();
      foreach $host (sort keys %{$all_hosts{$net}}) {
        if ($all_host_types{$host} eq $typ) {
           push(@sites, $host_site{$host});
        }
      }
   
      #skip virtual hosts like HC
      if ($site_no_check{$sites[0]} == 5 ) {
        $virtual_peer{$sites[1]}= 1;
        next;
      }
      if ($site_no_check{$sites[1]} == 5) {
        $virtual_peer{$sites[0]}= 1;
        next;
      } 
          
      next if (($no_tunnel && $typ=~/tunnel/i) ||
                ($no_tunnel && $typ=~/ethernet/i) ||
                ($no_radio && $typ=~/radio/i) || 
                ($no_ism&& $typ=~/ISM/i));

      if ($only_as) {
        next if ($site_as{$sites[0]} ne $only_as ||
                 $site_as{$sites[1]} ne $only_as)
      }
      if ($only_country) {
        next if ($site_country{$sites[0]} ne $only_country &&
                 $site_country{$sites[1]} ne $only_country)
      } 

      #get RSSI
      my $style=$typ;
      if (( $only_radio || $radio ) && ( $typ=~/radio/i || $typ=~/ISM/i)) {
        my $rssi= 0;      
        #get worst rssi
        #left monitored host -> rssi
        my $monitor_left;
        my $sth= $db->prepare(qq(select 
          host.ip, ck.value
          from hamnet_host as host
          join hamnet_check as ck on ck.ip = host.ip
          where 
            ck.service = 'rssi' and
             ((host.rawip > $subnet_begin{$net} and
               host.rawip < $subnet_end{$net} and host.site='$sites[0]')
            OR
               (host.rawip > $subnet_begin{$net} and
               host.rawip < $subnet_end{$net} and host.site='$sites[1]'))
            AND
            unix_timestamp(ck.ts) > (unix_timestamp(NOW())-7200)
          ORDER BY 
            ck.ts
          LIMIT 2  
        ));
        $sth->execute;
        while (@line= $sth->fetchrow_array) {
          my $idx= 0;
          $monitor_left= $line[$idx++];
          $rssi_tmp= $line[$idx++];
          $rssi= $rssi_tmp if $rssi_tmp < $rssi; 
        }
        next if ($rssi == 0 && $only_radio);
        if (length($rssi) >1 ) {
          $rssi = $rssi+0;
          #$rssi= $rssi2 if $rssi > $rssi2; #get worst side and apply style
          if   ($rssi>-66) {$style= 'hf1';} 
          elsif($rssi>-71) {$style= 'hf2';} 
          elsif($rssi>-76) {$style= 'hf3';} 
          elsif($rssi>-81) {$style= 'hf4';} 
          elsif($rssi>-86) {$style= 'hf5';} 
          elsif($rssi>-99) {$style= 'hf6';} 
          else             {$style= 'hf7';} 
        }
      }
      #print qq(Content-Type: text/plain\nExpires: 0 \n\n);
      if ($bgp && ($typ=~/radio/i || $typ=~/ISM/i)) {
        my $monitor_left;
        my $rssi= 0;
        my $sth= $db->prepare(qq(select 
          host.ip, ck.value
          from hamnet_host as host
          join hamnet_check as ck on ck.ip = host.ip
          where 
            ck.service = 'routing' and 
            ((host.rawip > $subnet_begin{$net} and 
             host.rawip < $subnet_end{$net} and host.site='$sites[0]')
            OR
              (host.rawip > $subnet_begin{$net} and
              host.rawip < $subnet_end{$net} and host.site='$sites[1]'))
            AND
              unix_timestamp(ck.ts) > (unix_timestamp(NOW())-7200)
          ORDER BY
            ck.ts
          LIMIT 2      
        ));
        $sth->execute;
        while (@line= $sth->fetchrow_array) {
          my $idx= 0;
          $monitor_left= $line[$idx++];
          $rssi= $line[$idx++];
        }
        next if (!$rssi);
          if (length($rssi) >=1) {
            if ($rssi <= 400) {
              $style = "bgpbad";
          } 
          else {
            $style = "bgp";
          }
        }
      } 
      if ($sponsor && ($typ=~/radio/i || $typ=~/ISM/i)) {
        my $monitor_left;
        my $rssi= 0;
        my $sth= $db->prepare(qq(select 
          host.ip, ck.value
          from hamnet_host as host
          join hamnet_check as ck on ck.ip = host.ip
          where 
            ck.service = 'sponsor' and 
            ((host.rawip > $subnet_begin{$net} and 
             host.rawip < $subnet_end{$net} and host.site='$sites[0]')
            OR
              (host.rawip > $subnet_begin{$net} and
              host.rawip < $subnet_end{$net} and host.site='$sites[1]'))
          ORDER BY
            ck.ts
          LIMIT 2      
        ));
        $sth->execute;
        while (@line= $sth->fetchrow_array) {
          my $idx= 0;
          $monitor_left= $line[$idx++];
          $rssi= $line[$idx++];
        }
        next if (!$rssi);
          if (length($rssi) >=1) {
            if ($rssi <= 400) {
              $style = "sponsor";
          } 
        }
      } 
      push(@allEdges, "$style;$net;$sites[0];$sites[1]");
    }
  }
}
# TIME only_as || only_country into SQL-query?
# -------------------------------------------------------------------------
# Prepare sites
foreach my $callsign (@allCallsigns) { 
  if ($only_as) {
    next if ($site_as{$callsign} != $only_as)
  }
  if ($only_country) {
    $site_country{$callsign}= $as_country{$site_as{$callsign}};
    next unless $site_country{$callsign} eq $only_country;
  }
  next if ($site_no_check{$callsign} == 5); #hamcloud
  my $hasHamnet= ($site_no_check{$callsign}<2 || $site_no_check{$callsign}==4)?1:0;
  next if (($only_hamnet && !$hasHamnet) || ($no_hamnet && $hasHamnet));
  
  my $zIndex= 10;
  my $siteAdd= "";
  $siteAdd= "-user" if $site_radioparam{$callsign};

  # The siteStatus contains complete image definition, just extract
  # the color since other symbols are used in the map context.
  if ($site_no_check{$callsign}>1 && $site_no_check{$callsign}<4) {
    $siteAdd= "-grey";
    $zIndex= 1;
  }
  elsif ($siteStatus{$callsign}=~/(green|red).png/) {
    if ($siteStatus{$callsign}=~/green/) {
      if ($virtual_peer{$callsign}) {
        $siteAdd.= "-blue";
        $zIndex= 20;
      }
      else {
        $siteAdd.= "-green";
        $zIndex= 20;
      }
    }
    else {
      $siteAdd.= "-red";
      $zIndex= 5;
    }
  }
  $zIndex++ if $radioparam;

  my $zi= sprintf("%03d", $zIndex);
  my $useBounds= ($site_no_check{$callsign}==1)?0:1;
  my $as= 0;
  if($only_as || $only_country) {
    $as= $site_as{$callsign};
  }

  #my $country= $as_country{$site_as{$callsign}};

  push(@allSites, 
    "$zi;$callsign;$as;$site_lat{$callsign};$site_long{$callsign};$siteAdd;$useBounds;".
    "$hasHamnet;$site_elevation{$callsign}" #;$country
  );
}
# -------------------------------------------------------------------------
# Prepare edges explicitely stored in the database
if(!$sponsor && !$bgp && !$only_radio) {
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
    next if (($no_tunnel && $typ=~/tunnel/i) || ($no_radio &&
             $typ=~/radio/i) || ($no_ism && $typ=~/ISM/i) || ($only_radio));
    push(@allEdges, "$typ;$left_site:$right_site;$left_site;$right_site");
  }
}

# -------------------------------------------------------------------------
# Print all out (as JSON)
#print qq(Content-Type: text/plain\nExpires: 0 \n\n);
print qq(Content-Type: application/json filename=hamnetdb-map.json\n\n);

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

# TIME 100-200ms
foreach $site (sort @allSites) {
#if (0) {
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
      &json_var($f[8], "anthight");
      &json_var("site".$f[5], "style");
      &json_var($f[0]+0, "zIndex");
    &json_obj_end();
  &json_obj_end();
}
&json_obj_end(1);
&json_obj_end();

sub check_process { 
  my $first= shift;

  unless ($first) {
    #sleep(1);
    usleep(100000);
  }
  open our $file, '<', $0 or die $!;
  flock $file, LOCK_EX or check_process(0);
  #flock $file, LOCK_EX|LOCK_NB or die "Unable to lock file $!";
}

