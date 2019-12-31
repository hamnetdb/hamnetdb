#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - test monitoring parameters
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
# Lucas Speckbacher, OE2LSP
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#

#//check login
#check subnet
	#2 sites
	#je 1 monitoring host
	#	=> get IPs
#check ping
#check monitoring

#print sites, IPs 

use lib qw(.);

use JSON;
use LWP::UserAgent;
#do "lib.cgi" or die;
$table= "none";
do "form.cgi" or die;
my $caption= "Hamnet-RSSI debugging";
&beforeForm($caption);

my $failed= 0;
my $left_call;
my $left_monitor;
my $right_call;
my $right_monitor;
my $url= $monitoring_API;

print qq(</table></form>);

my $ip_test= $query->param("id");
my $system= $query->param("sys");
$ip_test =~ s/\/.*//; #cut off /29 or anything else

if ($system eq "routing") {
  print "<h3>Router:</h3><span class='checkstatus'>".$ip_test."</span><br>\n";
   
  #if routing enabled
  if (checkRoutingFlag($ip_test)) {
    print "<h3>Monitoring - Routing:</h3>enabled<br>\n";     
  }
  else {
    print "<h3>Monitoring - Routing:</h3>not enabled<br>\n";     
    $failed=1;  
  }
  #if ping
  unless ($failed) {
   print qq(<h3>Ping:</h3>\n);
    my $url_ping= $url."/linktest/ping/".$ip_test."?EnableCaching=false&Timeout=0:0:5&Retries=2";
    my $response_ping=  get_api_data($url_ping);
    my $ok;
    my $decoded_json= decode_json($response_ping);
    $ok= $decoded_json->{'status'};

    if ($ok eq "Success") {
       print "ok";
    }
    else {
      $failed= 1;
      print "failed";
    }
    print "</span><br>";
  }
  #if api 
  unless ($failed) {
    print qq(<h3>Features:</h3>\n);
    my $url_function= $url."/linktest/info/".$ip_test."?EnableCaching=false&Timeout=0:0:5&Retries=2";
    #print $url_function,"<br>";
    my $response_function=  get_api_data($url_function);
    my $ok, $error_msg;
    my $feature_bgp = "not available";
    my $feature_traceroute = "not available";
    my $decoded_json= decode_json($response_function);
    #$ok= $decoded_json->{'status'};
    #$right_rssi= $decoded_json->{'details'}->[0]->{'rxLevel2at1'};
    my @features = @{$decoded_json->{'supportedFeatures'};};
    my @error_rssi = @{$decoded_json->{'errorDetails'};};
    foreach my $f ( @error_rssi ) {
      $error_msg= $error_msg.$f."<br>";
      $failed= 1;
    }
    foreach my $f ( @features ) {
       #print $f.'<br>';
       if ($f eq "BgpPeers") {
         $feature_bgp= "successfully tested";
       }
       if ($f eq "Traceroute") {
	 $feature_traceroute= "successfully tested";       
       }    
    }			    
    print "<b>BGP</b> ",$feature_bgp,"<br>";
    print "<b>Traceroute</b> ",$feature_traceroute,"<br>";
    if ($failed) {
      print "<br>no active features could be found<br>\n";
    }     

    print "</span><br>";
  }
  #number bgp peers
  unless ($failed) {
    print qq(<h3>BGP-peers details</h3>\n);
    my $url_function= $url."/bgp/peers/".$ip_test."?EnableCaching=false&Timeout=0:0:5&Retries=2";
    #print $url_function;
    my $response_function=  get_api_data($url_function);
    my $peer_cnt, $error_msg, $prefix_cnt;
    my $decoded_json= decode_json($response_function);
    $ok= $decoded_json->{'status'};
    my @peers = @{$decoded_json->{'bgpPeers'};};
    my @error_rssi = @{$decoded_json->{'errorDetails'};};
    foreach my $f (@peers) {
      if ($f->{'peeringState'} eq "established" ) {
	$prefix_cnt+= $f->{'prefixCount'};
        $peer_cnt++;
      }
    }
    print "<b>active direct BGP peers</b> ",$peer_cnt,"<br>";
    print "<b>prefix count in total</b> ",$prefix_cnt,"<br>";
  }
}	
if ($system eq "rssi") {
  $result_link= showLinkByIP($ip_test);
  $result_text_link= status2Text($result_link);
  unless ($result_link) {
    $failed= 1;
  }
  print "<h3>Link:</h3><span class='checkstatus'>".$result_text_link."</span><br>\n";

#print link info
  unless ($failed) {
    print qq(<span class='checkstatus'>&nbsp;&nbsp;&nbsp;<b>Left Site:</b> $left_call
      <b>Right Site:</b> $right_call </span><br> );
  }

  unless ($failed) {
    $result_monitor= showLinkRSSIIP($ip_test);
    print "<h3>Monitoring enabled:</h3>".$result_monitor."<br>\n";
  }

  unless ($failed) {
    print qq(<span class='checkstatus'>&nbsp;&nbsp;&nbsp;<b>Left IP:</b>$left_monitor  
      <b>Right IP</b> $right_monitor</span><br>\n);
    my $left_url_ping= $url."/ping/".$left_monitor."?EnableCaching=false&Timeout=0:0:5&Retries=2";
    my $right_url_ping= $url."/ping/".$right_monitor."?EnableCaching=false&Timeout=0:0:5&Retries=2";
    my $left_response_ping=  get_api_data($left_url_ping);
    my $right_response_ping=  get_api_data($right_url_ping);

    my $left_ok;
    my $right_ok;
  
    my $decoded_json= decode_json($left_response_ping);
    $left_ok= $decoded_json->{'status'};
  
    my $decoded_json= decode_json($right_response_ping);
    $right_ok= $decoded_json->{'status'};
  
    print qq(<h3>Ping $left_monitor </h3><span class='checkstatus'>);
    if ($left_ok eq "Success") {
      print "ok"; 
    }
    else {
      $failed= 1;
      print "failed";
    }
    print qq(</span><br><h3>Ping $right_monitor </h3><span class='checkstatus'>);
    if ($right_ok eq "Success") {
    print "ok"; 
    }
    else {
      $failed= 1;
      print "failed";
    }
    print "</span><br>";
  }

  unless ($failed) {
    my $left_url_snmp= $url."/info/".$left_monitor."?EnableCaching=false&Timeout=0:0:3&Retries=2";
    my $right_url_snmp= $url."/info/".$right_monitor."?EnableCaching=false&Timeout=0:0:3&Retries=2";
    my $left_response_snmp=  get_api_data($left_url_snmp);
    my $right_response_snmp=  get_api_data($right_url_snmp);

    my $left_ok;
    my $right_ok;

    my $decoded_json_left= decode_json($left_response_snmp);
    $left_ok= $decoded_json_left->{'model'};

    my $decoded_json_right= decode_json($right_response_snmp);
    $right_ok= $decoded_json_right->{'model'};

    print qq(<h3>SNMP $left_monitor </h3><span class='checkstatus'>\n);
    if (length($left_ok) > 3) {
      print "ok";
    }
    else {
      $failed= 1;
      print "failed";
    }
    print qq(</span><br><h3>SNMP $right_monitor </h3><span class='checkstatus'>);
    if (length($right_ok) > 3) {
      print "ok";
    }
    else {
      $failed= 1;
      print "failed";
    }
    print "</span><br>";
  }



  unless ($failed) {
    my $url_rssi= $url."/link/".$left_monitor."/".$right_monitor."?EnableCaching=false&Timeout=0:0:2&Retries=2";
    my $response_rssi=  get_api_data($url_rssi);
  
    print	"<h3>RSSI:</h3>\n";

    my $left_rssi= 0;
    my $right_rssi= 0;

    my $decoded_json= decode_json($response_rssi);
    $left_rssi= $decoded_json->{'details'}->[0]->{'rxLevel1at2'};
    $right_rssi= $decoded_json->{'details'}->[0]->{'rxLevel2at1'};
    my @error_rssi = @{$decoded_json->{'errorDetails'};};
  
    my $error_msg= "";
    foreach my $f ( @error_rssi ) {
      $error_msg= $error_msg.$f."<br>";
      $failed= 1;
    }
    $left_rssi+0;
    $right_rssi+0;

    print qq(<b>Left Site:</b> );
    if ($left_rssi ne 0 ) {
      print $left_rssi."dBm";
    }
    else {
      $failed= 1;
      print "failed";
    }
    print "<br><b>Right Site:</b>";
    if ($right_rssi ne 0 ) {
      print $right_rssi."dBm";
    }
    else {
      $failed= 1;
      print "failed";
    }
    print "<br>";
    if ($failed) {
      print qq(<b>Error Message:</b> $error_msg<br>failed);
    }
    else {
      print "ok";
    } 
 
  }
}
#
# {
#   "address": "44.143.47.74",
#   "roundtripTime": "00:00:00.0600000",
#   "timeToLive": null,
#   "dontFragment": null,
#   "bufferSize": 0,
#   "status": "Success",
#   "errorDetails": []
# }
# 
# {
#   "details": [
#     {
#       "macString1": "4C:5E:0C:80:E6:07",
#       "macString2": "00:21:A4:35:5A:D8",
#       "address1": "44.143.47.74",
#       "address2": "44.143.47.77",
#       "modelAndVersion1": "RB912UAG-5HPnD v 6.36.3",
#       "modelAndVersion2": "RB411GL v 6.43.2",
#       "rxLevel1at2": -67.46098108956133,
#       "rxLevel2at1": -66.8755739720566,
#       "linkUptime": "5.15:31:45",
#       "sideOfAccessPoint": 1
#     }
#   ],
#   "errorDetails": []
# }
#
#errorDetails	
#0	"HamnetSnmpException: Timeout talking to device '44.143.47.76' during applicability check\nCollected Errors:\nSnmpAbstraction.AlixDetectableDevice: SnmpException talking to device '44.143.47.76' during applicability check: Request has reached maximum retries.\nCollected Exceptions:\nRequest has reached maximum retries."
# 1	"SnmpException: Request has reached maximum retries."


sub status2Text {
	$param= shift;
	if ($param) {
		return "ok";
	}
	else {
		return "failed";
	}
}

sub showLinkByIP {
  my $search= shift;
  my @line= ();

  return 0 unless $search=~/^$ipPattern$/;
  my $left_ip= $1;
  my $right_ip;
  my $rawip= &aton($left_ip);

  %host_typ= ();
  %host_site= ();

  my $sth= $db->prepare("select id,ip,begin_ip,end_ip,typ,as_parent,".
    "radioparam,comment ".
    "from hamnet_subnet ".
    "where begin_ip<=$rawip and end_ip>$rawip and typ like 'Backbone-%'");
  $sth->execute;
  if (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $ip= $line[$idx++];
    my $begin_ip= $line[$idx++];
    my $end_ip= $line[$idx++];
    my $typ= $line[$idx++];
    my $as_parent= $line[$idx++];
    my $radioparam= $line[$idx++]; # "network-type"
    my $comment= &maxlen($line[$idx++],$commentMax);
    return if $subnetInLink{$ip};
    $subnetInLink{$ip}= 1;

    my $sth= $db->prepare(qq(select 
      ip,hamnet_host.typ,hamnet_host.site
      from hamnet_host
      where $begin_ip<=rawip and $end_ip>rawip and typ like 'Routing%'
      order by rawip desc));
    $sth->execute;
    my $min_ip;
    while (@line= $sth->fetchrow_array) {
      my $idx= 0;
      my $host_ip= $line[$idx++];
      $host_typ{$host_ip}= $line[$idx++];
      $host_site{$host_ip}= $line[$idx++];
      $min_ip= $host_ip;
    }
    return if int(keys %host_site)!=2;

    unless ($host_site{$left_ip}) {
      $left_ip= $min_ip;
    }

    my $right= "";

    foreach $ip (sort keys %host_site) {
      next if $ip eq $left_ip;
      $right_ip= $ip;
    }
    
    #print qq($host_site{$left_ip} left $left_ip    $host_site{$right_ip} right $right_ip );

    $left_call= $host_site{$left_ip};
    $right_call= $host_site{$right_ip};

    return 1;
  }
  return 0;
}

sub showLinkRSSIIP {
  my $search= shift;
  my @line= ();

  return 0 unless $search=~/^$ipPattern$/;
  my $left_ip= $1;
  my $right_ip;
  my $rawip= &aton($left_ip);

  %host_typ= ();
  %host_site= ();

  my $sth= $db->prepare("select id,ip,begin_ip,end_ip,typ,as_parent,".
    "radioparam,comment ".
    "from hamnet_subnet ".
    "where begin_ip<=$rawip and end_ip>$rawip and typ like 'Backbone-%'");
  $sth->execute;
  if (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $ip= $line[$idx++];
    my $begin_ip= $line[$idx++];
    my $end_ip= $line[$idx++];
    my $typ= $line[$idx++];
    my $as_parent= $line[$idx++];
    my $radioparam= $line[$idx++]; # "network-type"
    my $comment= &maxlen($line[$idx++],$commentMax);
    #return if $subnetInLink{$ip};
    $subnetInLink{$ip}= 1;

    my $sth= $db->prepare(qq(select 
      ip,hamnet_host.typ,hamnet_host.site
      from hamnet_host
      where $begin_ip<=rawip and $end_ip>rawip  
      and monitor = 1
      order by rawip desc));
    $sth->execute;
    my $min_ip;
    my $host_cnt;
    while (@line= $sth->fetchrow_array) {
      my $idx= 0;
      my $host_ip= $line[$idx++];
      $host_typ{$host_ip}= $line[$idx++];
      $host_site{$host_ip}= $line[$idx++];
      $min_ip= $host_ip;
      $host_cnt++;
    }
    if (int(keys %host_site)!=2) {
      $failed= 1;	  
      return "Monitoring is not active on both sites!"
    }
    if ($host_cnt gt 2) {
      $failed= 1;	  
      return "Monitoring is active on more than one host at each site!"
    }

    unless ($host_site{$left_ip}) {
      $left_ip= $min_ip;
    }

    my $right= "";

    foreach $ip (sort keys %host_site) {
      next if $ip eq $left_ip;
      $right_ip= $ip;
    }
    

    #print qq(monitor $host_site{$left_ip} left $left_ip    $host_site{$right_ip} right $right_ip host_cnt $host_cnt\n);
    $left_monitor= $left_ip;
    $right_monitor= $right_ip;

    $left_call= $host_site{$left_ip};
    $right_call= $host_site{$right_ip};

    return "ok";
  }
  $failed= 1;	  
  return 0;
}

sub checkRoutingFlag {
  my $ip= shift;
  my $sql="select ip ".
    "from hamnet_host ".
    "where ip='$ip' and routing=1";
  my $sth= $db->prepare($sql);
  $sth->execute;
  if (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $result= $line[$idx++];
    return 1;
  }
  return 0;
}  

