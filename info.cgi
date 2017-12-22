#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Show short info in inline popup
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
#
# Script is only used as AJAX data source, thus no html header/footer needed.
#
my $q= lc $query->param("q");

if ($q eq "" && $ARGV[0]) {
  $q= lc $ARGV[0];
}
$q=~s/[^a-z0-9\.\/\-_:]//g;        # avoid sql bombs.n

my $found= 0;
my $isHost= 0;
my $isSubnet= 0;

unless ($found) {
  my $sth= $db->prepare(qq(
    select hamnet_host.name,hamnet_site.name,hamnet_host.site,
    ip,rawip,typ,aliases,
    hamnet_host.radioparam,hamnet_host.comment,hamnet_host.mac
    from hamnet_host 
    left join hamnet_site on hamnet_host.site=hamnet_site.callsign
    where ip=).$db->quote($q));

  if ($sth->execute && (@line= $sth->fetchrow_array)) {
    my $idx= 0;
    my $name= $line[$idx++];
    my $sitename= $line[$idx++];
    my $sitecall= $line[$idx++];
    my $ip= $line[$idx++];
    my $rawip= $line[$idx++];
    my $typ= $line[$idx++];
    my $aliases= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= &maxlen($line[$idx++],40);
    my $mac= $line[$idx++];
    $radioparam=~s/,/<br>/ if length($radioparam)>40;

    my %st= &hostsStatus("hamnet_host.ip='$ip'");

    print qq(<h4>Host $ip</h4><b>$st{$ip} $name ($typ)</b>
             <br>$sitecall ($sitename));
    &brprint($radioparam);
    &brprint(&macColon($mac));
    &brprint($comment);
    if ($aliases) {
      print("<br>Aliases: <b>$aliases</b>");
    }
    print("<br><br>\n");

    ($q)= $db->selectrow_array(qq(select ip from hamnet_subnet
      where $rawip<end_ip and $rawip>=begin_ip order by ip desc));
    $isHost= 1;
  }
}

unless ($found) {
  my $sth= $db->prepare(qq(
    select ip,typ,as_parent,begin_ip,end_ip,radioparam,comment
    from hamnet_subnet where ip=).$db->quote($q));

  if ($sth->execute && (@line= $sth->fetchrow_array)) {
    my $idx= 0;
    my $ip= $line[$idx++];
    my $typ= $line[$idx++];
    my $as_parent= $line[$idx++];
    my $begin_ip= $line[$idx++];
    my $end_ip= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= &maxlen($line[$idx++],40);
    $radioparam=~s/,/<br>/ if length($radioparam)>40;

    print qq(<h4>Subnet $ip</h4><b>$typ</b>);
    &brprint($radioparam);
    &brprint($comment);
    print("<br><br>");
    
    unless ($isHost) {
      print qq(<h4>Sites:</h4>);
      my %sites= ();
      my $sth= $db->prepare(qq(select hamnet_site.callsign,hamnet_site.name
         from hamnet_host 
         left join hamnet_site on hamnet_host.site=hamnet_site.callsign
         where rawip between $begin_ip and $end_ip));
      $sth->execute;
      while (@line= $sth->fetchrow_array) {
        $sites{$line[0]}= $line[1] if $line[0];
      }
      if (%sites) {
        my %st= &hostsStatus("hamnet_host.site in ('".
                             join("','",keys %sites)."')", 1);
        print("<table cellspacing=0 cellpadding=0 border=0>");
        foreach $site (sort keys %sites) {
          print("<tr><td>$st{$site} &nbsp;</td><td>$site &nbsp;</td>".
                "<td>$sites{$site}</td></tr>\n");
        }
        print("</table>");
      }
      else {
        print("none.<br>");
      }
      print("<br>\n");
    }

    $q= "as$as_parent";
    $isSubnet= 1;
  }
}

unless ($found) {
  my $sth= $db->prepare(qq(
    select callsign,fullname,email,comment
    from hamnet_maintainer where callsign=).$db->quote($q));

  if ($sth->execute && (@line= $sth->fetchrow_array)) {
    my $idx= 0;
    my $callsign= $line[$idx++];
    my $fullname= $line[$idx++];
    my $email= $line[$idx++];
    my $comment= $line[$idx++];
    my $activity= 0;

    if ($username) {
      ($activity)= $db->selectrow_array(qq(select unix_timestamp(last_act) 
               from hamnet_session where callsign='$callsign'
               order by last_act desc limit 0,1));
    }
    else {
      $fullname=~s/ .*$//;
      $email= "";
    }

    print qq(<h4>Maintainer $callsign</h4><b>$fullname</b>);
    &brprint($email);
    if ($comment) {
      &brprint("<p>".&maxlen($comment,60));
    }
    if ($username) {
      if ($activity) {
        &brprint("<p>Last activity: ".&timespan(time-$activity));
      }
      else {
        &brprint("<p>Never logged in.</p>");
      }
    }
    $found= 1;
  }

  my $sth= $db->prepare(qq(
    select callsign,name,radioparam,comment,no_check
    from hamnet_site where callsign=).$db->quote($q));

  if ($sth->execute && (@line= $sth->fetchrow_array)) {
    my $idx= 0;
    my $callsign= $line[$idx++];
    my $name= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= &maxlen($line[$idx++],40);
    my $no_check= $line[$idx++];

    my $c= $callsign;
    $c= "" if $c=~/nocall/;
    print qq(<br><br>) if $found;
    print qq(<h4>Site $c</h4><b>$name</b>\n);

    &brprint("<b style='color:#a00000'>".
             "No hamnet.</b>") if $no_check>1 && $no_check<4;
    &brprint($radioparam);
    &brprint($comment);

    my %st= &hostsStatus("site='$callsign'");
    my $hostFound= 0;
    print qq(<br><br><h4>Hosts:</h4>);
    my %sites= ();
    my $sth= $db->prepare(qq(select name,ip
       from hamnet_host where site='$callsign' order by rawip));
    $sth->execute;
    print("<table cellspacing=0 cellpadding=0 border=0>");
    while (@line= $sth->fetchrow_array) {
      print("<tr><td>$st{$line[1]} &nbsp;</td>".
            "<td>$line[0] &nbsp;</td><td>$line[1]</td></tr>\n");
      $hostFound= 1;
    }
    print("</table>");
    unless ($hostFound) {
      print("none.<br>\n");
    }
    $found= 1;
  }
}

unless ($found) {
  if ($q=~/^as(\d+)/i) {
    my $as= $1;
    my $sth= $db->prepare(qq(
      select name,as_num,comment
      from hamnet_as where as_num=).$db->quote($as));

    if ($sth->execute && (@line= $sth->fetchrow_array)) {
      my $idx= 0;
      my $name= $line[$idx++];
      my $as_num= $line[$idx++];
      my $comment= &maxlen($line[$idx++],40);

      print qq(<h4>AS$as_num $name</h4>$comment);
      
      unless ($isHost || $isSubnet) {
        print qq(<br><br><h4>Sites:</h4>);
        my %sites= ();
        my $sth= $db->prepare(qq(select hamnet_site.callsign,hamnet_site.name
           from hamnet_subnet 
           left join hamnet_host on rawip between begin_ip and end_ip
           left join hamnet_site on hamnet_host.site=hamnet_site.callsign
           where as_parent=$as_num and hamnet_host.typ='Service'));
        $sth->execute;
        while (@line= $sth->fetchrow_array) {
          $sites{$line[0]}= $line[1] if $line[0];
        }
        if (%sites) {
          my %st= &hostsStatus("hamnet_host.site in ('".
                               join("','",keys %sites)."')", 1);
          print("<table cellspacing=0 cellpadding=0 border=0>");
          foreach $site (sort keys %sites) {
            print("<tr><td>$st{$site} &nbsp;</td><td>$site &nbsp;</td>".
                  "<td>$sites{$site}</td></tr>\n");
          }
          print("</table>");
        }
        else {
          print("none.<br>\n");
        }
      }
      $found= 1;
    }
  }
}

unless ($found) {
  if ($q=~/^([a-z0-9\-]+):([a-z0-9\-]+)$/i) {
    my $left= $1;
    my $right= $2;
    my $dir= 0;
    my @callsign;
    my @name;
    my @latitude;
    my @longitude;

    my $sth= $db->prepare(qq(select callsign,name,latitude,longitude
      from hamnet_site where callsign in ('$left','$right')
      order by longitude));
    $sth->execute or &fatal("cannot select");

    while (@line= $sth->fetchrow_array) {
      my $idx= 0;
      $callsign[$dir]= $line[$idx++];
      $name[$dir]= $line[$idx++];
      $latitude[$dir]= $line[$idx++];
      $longitude[$dir]= $line[$idx++];
      $dir++;
    }
    my $dist= &distance($latitude[0],$longitude[0],$latitude[1],$longitude[1]);
    if ($dist>0 && $dist<1000) {
      $dist= sprintf("%0.1fkm", $dist);
    }
    else {
      $dist= "";
    }
    my $bear0= &bearing($latitude[0],$longitude[0],$latitude[1],$longitude[1]);
    my $bear1= &bearing($latitude[1],$longitude[1],$latitude[0],$longitude[0]);

    my $sth= $db->prepare(qq(select 
      hamnet_subnet.radioparam,h0.ip,h1.ip,h0.radioparam,h1.radioparam,
      h0.typ,h1.typ, hamnet_subnet.begin_ip, hamnet_subnet.end_ip
      from hamnet_subnet
      left join hamnet_host as h0 on h0.rawip between begin_ip and end_ip
      left join hamnet_host as h1 on h1.rawip between begin_ip and end_ip
      where h0.site='$callsign[0]' and h1.site='$callsign[1]' 
      and hamnet_subnet.typ='Backbone-Network'));

    if ($sth->execute && (@line= $sth->fetchrow_array)) {
      my $idx= 0;
      my $radioparam= $line[$idx++];
      my $ip0= $line[$idx++];
      my $ip1= $line[$idx++];
      my $radioparam0= $line[$idx++];
      my $radioparam1= $line[$idx++];
      my $typ0= $line[$idx++];
      my $typ1= $line[$idx++];
      my $begin_ip= $line[$idx++];
      my $end_ip= $line[$idx++];
      $radioparam0=~s/,/<br>/;
      $radioparam1=~s/,/<br>/;
      $radioparam.= " - " if $radioparam && $dist;
      $radioparam.= $dist;

      if ($typ0 eq $typ1 && !($typ0=~/Radio/i)) {
        $radioparam.= " - $typ0";
      }

      #get rssi
      my $monitor_left;
      $sql=qq(select 
        ip
        from hamnet_host
        where 
        monitor=1 and rawip > $begin_ip and 
        rawip < $end_ip and site='$callsign[0]'
      );
      my $sth= $db->prepare($sql);
      $sth->execute;
      while (@line= $sth->fetchrow_array) {
        my $idx= 0;
        $monitor_left= $line[$idx++];
      }

      my $monitor_right;
      $sql=qq(select 
        ip
        from hamnet_host
        where 
        monitor=1 and rawip > $begin_ip and 
        rawip < $end_ip and site='$callsign[1]'
      );
      my $sth= $db->prepare($sql);
      $sth->execute;
      while (@line= $sth->fetchrow_array) {
        my $idx= 0;
        $monitor_right= $line[$idx++];
      }
      my $rssi; 
      my $rssi1; 
      my $rssi2; 
      $rssi1=linkStatus($monitor_left,'rssi');
      $rssi2=linkStatus($monitor_right,'rssi');
      $rssi1= $rssi1." dBm" if length($rssi1) >2;
      $rssi2= $rssi2." dBm" if length($rssi2) >2;
      if (length($rssi1)>1 || length($rssi2)>1) {
        $rssi= $rssi1." / ".$rssi2;
      }


      my %st= &hostsStatus("hamnet_host.ip in ('$ip0','$ip1')");

      print qq(
        <table cellspacing=0 cellpadding=0 border=0>
        <tr>
          <td align="right" valign="top">
          <h4>$st{$ip0} $callsign[0] &nbsp; $bear0</h4><b>$name[0]</b>
          <p>$radioparam0
          </td>
          <td align="center" valign="middle">
            &nbsp;<img src="arrow.png" width=30 height=20>&nbsp;
          </td>
          <td align="left" valign="top">
          <h4>$bear1 &nbsp; $callsign[1] $st{$ip1}</h4><b>$name[1]</b>
          <p>$radioparam1
          </td>
        </tr>
        <tr>
          <td colspan=3 align="center"><p><b>$radioparam</b>
          <br>
          $rssi</td>
        </tr>
        </table>

      );
      $found= 1;
    }
    # edge links
    unless ($found) {
      my $sth= $db->prepare(qq(select 
        left_host,right_host,typ,radioparam,comment
        from hamnet_edge
        where left_site in ('$callsign[0]','$callsign[1]') and
        right_site in ('$callsign[0]','$callsign[1]')
      ));

      if ($sth->execute && (@line= $sth->fetchrow_array)) {
        my $idx= 0;
        my $ip0= $line[$idx++];
        my $ip1= $line[$idx++];
        my $typ= $line[$idx++];
        my $radioparam= $line[$idx++];
        my $comment= $line[$idx++];
        $radioparam.= " - " if $radioparam && $dist;
        $radioparam.= $dist;

        print qq(
          <table cellspacing=0 cellpadding=0 border=0>
          <tr>
            <td align="right" valign="top">
            <h4>$st{$ip0} $callsign[0] &nbsp; $bear0</h4><b>$name[0]</b>
            <p>$radioparam0
            </td>
            <td align="center" valign="middle">
              &nbsp;<img src="arrow.png" width=30 height=20>&nbsp;
            </td>
            <td align="left" valign="top">
            <h4>$bear1 &nbsp; $callsign[1] $st{$ip1}</h4><b>$name[1]</b>
            <p>$radioparam1
            </td>
          </tr>
          <tr>
            <td colspan=3 align="center">
              <p>Edge
              <p><b>$typ - $radioparam</b>
            </td>
          </tr>
          </table>
        );
        $found= 1;
      }
    }
  }
}


unless ($found) {
  my $ele= "Entry";
  if ($q=~/^as/i) {
    $ele= "AS";
  }
  if ($q=~/\.\d+\/\d/) {
    $ele= "Subnet";
  }
  if ($q=~/^[\d\.]+$/) {
    $ele= "Host";
  }
  if ($q=~/^([a-z0-9]+)-([a-z0-9]+)$/i) {
    $ele= "Link";
  }
  print qq(<h4>$ele not found</h4>\n);
}

