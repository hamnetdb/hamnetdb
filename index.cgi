#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Main page
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
do "lib.cgi" or die;

# Maximum width in table
$nameMax= 40;
$maintainMax= 20;
$commentMax= 80;
$sortDefault= "c";

$m= $query->param("m");
$m= "as" unless $m;
$m=~s/[^a-z]//i;
$hostWhere= "1";
$siteWhere= "1";
$subnetWhere= "1";
$asWhere= "1";
$as= $query->param("as")+0;
&prepareWhereAS($as);

$search=~s/:.*//; # replace Edge by left site
($foundType, $search)= &prepareWhere($search);
if ($foundType) {
  $m= $foundType;
  if ($foundType eq "as") {
    if ($asWhere=~/as_num='(\d+)'/) {
      $as= $1;
    }
    else {
      $as= 0;
    }
  }
}

&htmlHead((ucfirst $m)." $search - ");
print qq(
  $htmlRel
  <div id="infoPopup" class="vgrad" style='padding:5px;'></div>
  <script language="JavaScript">
  function changed() {} // dummy for comboBox which is intended for input-win
  </script>
  <script for="document" event="onmousemove()" 
                         language="JScript" type="text/jscript"> 
  { hamnetdb.info.move(window.event); }
  </script>
  <table class="opttab text"><tr>
);

for $ml ("AS:as", "Sites:site", "Hosts:host", "Subnets:subnet",  
         "Utilities:util", "Last changes:history", "Help:help", 
         "Login:login") {
  if ($ml=~/(.*):(.*)/) {
    my $mp= $1;
    my $mc= $2;
    my $c= "";
    $c= " class='optact'" if $mc=~/$m/i;
    if ($mp=~/Login/ && $username) {
      $mp.= ": $username";
    }
    my $ass= "";
    if ($mc ne "as") {
      $ass= "?m=$mc";
      $ass.= "&as=$as" if $as>0;
    }
    print qq(<td$c><a href="$baseUri/$ass">$mp</a></td>\n);
  }
}
print qq(
  </tr>
  </table>
  <form name="main">
  <div class="cmdbox vgrad">
  <input type="hidden" name="m" value="$m">
  <a href='?m='><img width='32' height='32' align="right" style="margin-top:-5px;" 
     src="hamnetdb-64.png"></a>
);

if ($m=~/login/i) {
  print qq(<h3>Hamnet-DB write access login</h3>);
}
elsif ($m=~/util/i) {
  my $sub= &subMenu("func:Utility functions",
           "export+:Data export",
           "check:Consistency check",
           "maintainer:Maintainers"
  );
  if ($sub eq "history") {
    $sortDefault= "zr";
  }
  if ($sub eq "maintainer") {
    print("&nbsp;&nbsp;");
    &newBut($sub);
  }
}
elsif ($m=~/history/i) {
  &subMenu("func:List",
           "last200+:Last 200 changes",
           "last2000+:Last 2000 changes",
           "relnotes:Software release notes"
  );
  $sortDefault= "zr";
}
else {
  &searchBox; 
  unless ($m=~/as/i) {
    print("&nbsp;&nbsp;&nbsp;AS:");
    &asCombo(1, 1, 0, $as)
  }
  &dispBut;
  &newBut($m);
}

print qq(
  <noscript><div style="color:red;font-weight:bold;margin-top:20px">
  You will need to enable JavaScript to use all functions of this site.
  </div></noscript>
  <div style='text-align:right;margin-top:20px;font-size:70%;'>
  Hamnet-DB $hamnetdb_version 
  Content is covered by 
  <a title="Creative Commons  Attribution-NonCommercial-ShareAlike 3.0"
     href="http://creativecommons.org/licenses/by-nc-sa/3.0/" target="_blank">
  CC BY-NC-SA
  </a> license
  </div>
  </div>
);
&sortInit;

# ---------------------------------------------------------------------------
# End of head section - from here on the content section begins
# ---------------------------------------------------------------------------


if ($m eq "as") {
  if (! &asShow($search)) {
    my $cc= "";
    if ($asWhere=~/country='([a-z][a-z])'/) {
      $cc= $1;
    }
    if ($cc || (!$search && !$query->param("bynum"))) {
      print qq(<div class="infobox vgrad" 
         style="float:right;padding-bottom:0px;">
         <h2>The Hamnet-Database</h2>);
      &mapMenu;
      print qq(<br><br><br>
        <a href='?bynum=1'>Classic list of AS by number</a>
        <br><br>
        </div>);

      &overviewList($cc);
      if ($cc) {
        &asList("", "AS of ".$tldName{$cc}." ($cc)");
      }
    }
    else {
      &asList($search);
    }
  }
}
if ($m eq "site") {
  unless (&siteShow($search)) {
    &siteList($search);
  }
}
if ($m eq "subnet") {
  unless (&subnetShow($search)) {
    &subnetList($search);
    if ($foundType) {
      &hostList("", "Hosts in Subnet $search");
      &asList("", "In AS");
    }
  }
}
if ($m eq "host") {
  unless (&hostShow($search)) {
    &hostList($search);
    if ($foundType) {
      &subnetList("", "Surrounding subnets");
      &asList("", "Surrounding AS");
    }
  }
}
if ($m eq "history") {
  my $func= $query->param("func");
  if ($func eq "relnotes") {
    print qq(<div class="help">);
    if (open(REL,"<CHANGES.html")) {
      print(<REL>);
      close(REL);
    }
    print qq(</div>);
  }
  else {
    &loadCheckList(1);
    &showHistoryList;
  }
}
if ($m eq "util") {
  my $adr= $ENV{"SERVER_NAME"}.$baseUri;
  my $func= $query->param("func");
  if ($func eq "check") {
    &loadCheckList;
    &showCheckList;
  }
  elsif ($func eq "maintainer") {
    &maintainerList($search);
  }
  else {
    print qq(
      </form>
      <div class="utility vgrad">
      <h3>Database dump and software download</h3>
      Download: &nbsp; 
      <a href="dump.cgi">MySQL dump of Hamnet-DB tables (including history)</a>
      <br><br>
      Hint: Use the following command to maintain a mirror
      (assumes existing user and database <i>hamnet</i>):
      <pre class="command">
      wget -qO- http://$adr/dump.cgi | \\
        mysql -u hamnet --password=&lt;yourpw&gt; hamnet</pre>
      For the first setup you need the 
      <a href="dump.cgi?tables=1">full structure of all tables</a>
    );

    my @dist= reverse sort <distrib/hamnetdb-*.tgz>;
    if (-s $dist[0]) {
      print qq( and the <a href="$dist[0]">software code</a>
              (see README.txt for install info));
    }
    print qq(.</div>);

    print qq(
      <div class="utility vgrad">
      <h3>CSV-export of Hamnet-DB tables</h3>
      Download: &nbsp; 
      <a href="csv.cgi?tab=as">as.csv</a> &nbsp;
      <a href="csv.cgi?tab=site">site.csv</a> &nbsp;
      <a href="csv.cgi?tab=host">host.csv</a> &nbsp;
      <a href="csv.cgi?tab=subnet">subnet.csv</a> &nbsp;
      <a href="csv.cgi?tab=edge">edge.csv</a> &nbsp;
      </div>
    );

    print qq(
      <div class="utility vgrad">
      <h3>Generate DNS zone files</h3>
      <form method="get" action="dnszone.cgi">
    );

    &checkBox("Generate sub-domains for each AS ".
              "(CGI-parameter: <b>by_as</b>)", "by_as");

    print qq(&nbsp;&nbsp;);
    &textBox("Limit to AS (<b>only_as</b>)", 
             "only_as", 5, 1, "");
    print qq(<br><p>);
    &textBox("SOA-NS (<b>ns</b>)", "ns", 18, 1, "hamnetdb.ampr.org");
    print qq(&nbsp;&nbsp;);
    &textBox("SOA-Mail (<b>mail</b>)", "mail",24,1, "hostmaster.hamnetdb.net");
    print qq(<br><p>);
    &textBox("SOA-Serial (<b>serial</b>)", "serial",12,1, "");
    print qq((Inserted literally, 'unix' &gt; seconds since epoch, 
              default yymmddHHMM)
             <br><p>);
    &textBox("Domain-suffix for all entries (<b>suffix</b>)", 
             "suffix", 15, 1, "de.ampr.org");
    print qq(&nbsp;&nbsp;);
    &textBox("Country (<b>country</b>)", 
             "country", 2, 1, "de");

    print qq(
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
      <input type="submit" value="Generate DNS zones"><br>
      </form>
      <br>
      Automated update (Debian file system layout):
      <pre class="command">
      cd /var/cache/bind &amp;&amp; \\
        wget -qO- 'http://$adr/dnszone.cgi).
        qq(?by_as=0&suffix=de.ampr.org' | \\
        tar zxvf - &amp;&amp; /etc/init.d/bind9 reload</pre>
      First setup: Add &nbsp; <b>include "named.conf.hamnetdb";</b> &nbsp;
      to /etc/bind/named.conf.local
      </div>
    );

    print qq(
      <div class="utility vgrad">
      <h3>Generate /etc/hosts for local name resolution or usage with 
          dnsmasq</h3>
      Download: &nbsp; 
      <a href="hosts.cgi">/etc/hosts</a>
      <br><br>
      This file can be combined with normal DNS name resolution. 
      It offers a simple possibility to get here documented 
      addresses resolved to names.
      <p>
      Hint: You can use this file as source for the <b>dnsmasq</b> name 
      server program. In this combination it is possible to mix up the 
      zone contents of official <b>ampr.org</b> with the entries of 
      this database. 
      This is also true for the reverse lookup. 
      When offline, known names are still resolved as &lt;name&gt;.ampr.org.
      <p>
      Set this in /etc/dnsmasq.conf:
      <pre class="command">
      addn-hosts=/tmp/hosts.hamnetdb
      server=8.8.8.8                        # or your parent name server </pre>
      Shell commands for auto update:
      <pre class="command">
      wget -qO /tmp/hosts.hamnetdb http://hamnetdb.net/hosts.cgi && \\
        /etc/init.d/dnsmasq restart</pre>
      </div>
    );
  }
}
if ($m=~/help/i) {
  print qq(<div class="help">);
  if (open(HELP,"<help-de.html")) {
    print(<HELP>);
    close(HELP);
  }
  print qq(</div>);
}

if ($m=~/login/i) {
  print qq(</form><div class="utility vgrad" 
                       style="padding-top:10px;padding-bottom:10px;">);
  my $errMsg= $query->param("errMsg");
  if ($errMsg) {
    $errMsg=~s/[^a-z0-9\-\. ]//gi;
    print("<b style='color:red'>$errMsg</b><br><br>");
  }
  my $okMsg= $query->param("okMsg");
  if ($okMsg) {
    $okMsg=~s/[^a-z0-9\-\. ]//gi;
    print("<b style='color:green'>$okMsg</b><br><br>");
  }
  if ($username) {
    print qq(
      Login: $username ($myFullname, $myEmail) | 
      <a href="login.cgi?logout=1">Logout</a><br><br>
      <form method="POST" action="login.cgi">
      Change Password - 
      Current: <input type="password" size=8 name="pw">
      New: <input type="password" size=8 name="newpw">
      Confirm: <input type="password" size=8 name="newagain">
      <input type="submit" value="Change"></form>
    );
  }
  elsif ($query->param("func") eq "forgot") {
    print qq(
      <form method="POST" action="login.cgi">
      Your callsign: <input type="text" size=10 name="callsign">
      Your stored email address: <input type="text" size=15 name="email">
      <input type="submit" value="Generate new password">
      <input type="hidden" name="forgotpw" value="1"></form>
    );
  }
  else {
    print qq(
      <form method="POST" action="login.cgi">
      Callsign: <input type="text" size=10 name="login" autofocus="autofocus">
      Password: <input type="password" size=10 name="pw">
      <input type="submit" value="Login">
      &nbsp;&nbsp;
    );
      &checkBox("Remember login cookie","persist");
    print qq(
      &nbsp;&nbsp; &nbsp;&nbsp;
      <a href="?m=Login&func=forgot">Forgot password?</a></form>
    );
  }
  print qq(</div>);
}
else {
  print qq(</form>);
}
my $ypos= $query->param("ypos")+0;
if ($ypos>0) {
  print qq(<script>
    setTimeout(function() {
      window.scrollTo(0,$ypos);
    }, 200);
    </script>
  );
}

print qq(<br><br><br><br>);  # some place for info popup
&htmlFoot;
exit;

# ---------------------------------------------------------------------------
# End of main program.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Details of one particular site
sub siteShow {
  my $search= shift;
  my @line= ();
  my $t= "site";
  return 0 unless $search;

  my $sth= $db->prepare(qq(
    select id,name,callsign,longitude,latitude,elevation,no_check,
    radioparam,comment,maintainer,editor,date(edited),version
    from hamnet_$t where callsign=).$db->quote($search));
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $name= $line[$idx++];
    my $callsign= $line[$idx++];
    my $longitude= $line[$idx++];
    my $latitude= $line[$idx++];
    my $elevation= $line[$idx++];
    my $no_check= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= $line[$idx++];
    my $maintainer= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];
    my $version= $line[$idx++];
    $comment= &escComment($comment);
  
    my $coords= "$latitude,$longitude";
    my $shownc= sprintf("%0.6f,%0.6f",$latitude,$longitude);
    my $min= &dec2min($latitude)." N ".&dec2min($longitude)." E";
    my $sec= &dec2minsec($latitude)." N ".&dec2minsec($longitude)." E";
    my $locator= calcLocator($longitude,$latitude);
    my $coordh= "$shownc &nbsp;-&nbsp; $min &nbsp;-&nbsp; $sec  &nbsp;-&nbsp; $locator\n"; 
    my $ele= "${elevation} m above ground";

    my $in= "";
    $in= "<b style='color:#a00000'>".
         "On this site no hamnet is active.</b><p>" if $no_check> 1 && $no_check< 4;
    $in= "<b style='color:#407040'>".
         "ISM-Site</b></p>" if $no_check==4; 

    print qq(<div class="infobox vgrad">);
    &mapMenu(0, $callsign);
    $callsign= "" if $callsign=~/nocall/;

    print qq(<h2>).&editIcon($t, $id, 1);
    print qq(
      Site $callsign ($name)</h2>$in
      Coordinates: $coordh
      <br>Elevation: $ele
      <p>Maintainer: <b>$maintainer</b><br>);

    if ($radioparam) {
      print qq(<p>User access: <b>$radioparam</b></p>);
    }
    if ($comment) {
      print qq(<p>$comment</p>);
    }
    
    ###Show Antenna Configuration from hamnet_coverage###
    
    my $sth2 = $db->prepare("select tag,antennatype,azimuth,altitude,frequency from hamnet_coverage where callsign='$callsign' and version='$version'");
    $sth2->execute;
    
    #preventing the table if there is no coverage
    my $first_cov = 1; 
    
    while(($tag,$antennatype,$azimuth,$altitude,$frequency)=$sth2->fetchrow_array()) # (@line= $sth2->fetchrow_array) 
    {
      if($first_cov)
      {
        $first_cov= 0;
        print qq(<p>Antenna-configuration:<table>);
      }
      print qq(<tr><td><b>$tag </b></td> 
        <td>Typ: </td> <td align="right"> <b>$antennatype</b></td>
        <td>Azimuth: </td> <td align="right"><b> $azimuth°  </b></td>
        <td>Elevation: </td> <td align="right"> <b> $altitude° </td>
        <td></b> Frequency:</td> <td align="right"> <b>$frequency</b> </td> <td align="right">MHz</td></tr>
      );
    }
    if($first_cov == 0)
    {
      print qq(</table></p>);
    }
    
    print qq(<div style='text-align:right;font-size:90%'><i>
             Last edited $edited by <b class='ovinfo'>$editor</b></i></div>);
    print qq(<br>);

    &showLinkBySite($search);
    print qq(</div>);
    &hostList("", "Contains the following hosts".
              &addIcon("host","&site=$callsign"), $subnetWhere);
    &subnetList("", "Surrounding subnets".&addIcon("subnet"));
    &asList("", "Surrounding AS");
    &neighbourList($id);
    return 1;
  }
  return 0;
}

# ---------------------------------------------------------------------------
# Details of one particular subnet
sub subnetShow {
  my $search= shift;
  my @line= ();
  my $t= "subnet";
  return 0 unless $search;

  my $sth= $db->prepare("select ".
    "id,ip,begin_ip,end_ip,typ,as_num,as_parent,radioparam,".
    "comment,editor,date(edited) ".
    "from hamnet_$t where ip=".$db->quote($search));
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $ip= $line[$idx++];
    my $begin_ip= $line[$idx++];
    my $end_ip= $line[$idx++];
    my $typ= $line[$idx++];
    my $as_num= $line[$idx++];
    my $as_parent= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];
    $subnetWasShown{$ip}= 1;
  
    $comment= &escComment($comment);
    my $end_ipa= &ntoa($end_ip-1);

    my $base_ip;
    my $bits;
    if ($ip=~/(.*)\/(.*)/) {
      $base_ip= $1;
      $bits= $2;
    }
    my $netmask= 0;
    for ($i= 0; $i < 32; $i++) {
      if ($i >= (32-$bits)) {
        $netmask|= (1 << $i);
      }
    }
    my $adrnum= (1 << 32-$bits);
    my $mask= &ntoa($netmask);
    $radioparam= "Radio parameters: <b>$radioparam</b><br>" if $radioparam;

    print qq(<div class="infobox vgrad">);
    print qq(<h2>).&editIcon($t, $id, 1);
    print qq(
      Subnet $ip ($typ)</h2>
      <h3>Broadcast: $end_ipa &nbsp;&nbsp;&nbsp; 
          Netmask: $mask &nbsp;&nbsp;&nbsp; 
          $adrnum IPs</h3>
      $radioparam
    );
    if ($comment) {
      print qq(<br>$comment<br>);
    }
    print qq(<div style='text-align:right;font-size:90%'><i>
             Last edited $edited by <b class='ovinfo'>$editor</b></i></div>);

    if ($typ=~/Backbone/) {
      print qq(<br>);
      &showLinkByIP(&ntoa($begin_ip+1));
    }
    print qq(  
      </div>
    );

    &subnetList("", "Related to the subnets".
              &addIcon("subnet", "&base_ip=$base_ip"));

    &hostList("", "Contains the following hosts".
              &addIcon("host", "&ip=$base_ip"), $subnetWhere);

    &siteList("", "These hosts reside on following sites");
    
    &asList("", "Surrounding AS");

    return 1;
  }
  return 0;
}

# ---------------------------------------------------------------------------
sub hostShow {
  my $search= shift;
  my @line= ();
  my $t= "host";
  return 0 unless $search;

  my $sth= $db->prepare("select ".
    "id,name,ip,rawip,mac,aliases,typ,radioparam,site,".
    "comment,editor,date(edited) ".
    "from hamnet_$t where ip=".$db->quote($search));
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $name= $line[$idx++];
    my $ip= $line[$idx++];
    my $rawip= $line[$idx++];
    my $mac= $line[$idx++];
    my $aliases= $line[$idx++];
    my $typ= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $site= $line[$idx++];
    my $comment= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];
  
    $comment= &escComment($comment);

    $aliases= "DNS Aliases: <b>$aliases</b><br>" if $aliases;
    $mac= "MAC on radio interface: <b>$mac</b><br>" if $mac;
    $radioparam= "Radio parameters: <b>$radioparam</b><br>" if $radioparam;

    print qq(<div class="infobox vgrad">);
    print qq(<h2>).&editIcon($t, $id, 1);
    print qq(
      Host $name - $ip ($typ)</h2>
      $radioparam
      $aliases
      $mac
    );
    if ($comment) {
      print qq(<br>$comment<br>);
    }

    if ($typ=~/Routing/) {
      print qq(<br>);
      &showLinkByIP($search);
    }
    print qq(<div style='text-align:right;font-size:90%'><i>
             Last edited $edited by <b class='ovinfo'>$editor</b></i></div>);
    print qq(  
      </div>
    );

    &siteList("", "Site of this host");
    &subnetList("", "Surrounding subnets".&addIcon("subnet", "&base_ip=$ip"));
    &asList("", "Surrounding AS");

    return 1;
  }
  return 0;
}

# ---------------------------------------------------------------------------
sub showLinkBySite {
  my $site= shift;

  my @line= ();
  my @ips= ();
  my %macs= ();
  my %ipForMac= ();

  my $sth= $db->prepare(qq(select ip,mac from hamnet_host
    where site='$site' and typ like 'Routing%'));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    push(@ips, $line[0]);
    $macs{$line[1]}.= "," if $macs{$line[1]};
    $macs{$line[1]}.= $line[0];
  }
  foreach $mac (keys %macs) {
    my @shared= split(/,/, $macs{$mac});
    if (int(@shared)>1) {
      foreach $ip (@shared) {
        $host_mac_is_shared{$ip}= 1;
      }
    }
  }
  foreach $ip (@ips) {
    &showLinkByIP($ip);
  }
  # -------------------------------------------------------------------------
  # Prepare edges explicitely stored in the database
  my $sth= $db->prepare(qq(select id,
    left_site,right_site,left_host,right_host,typ,radioparam,comment
    from hamnet_edge
    where left_site='$site' or right_site='$site'
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $left_site= $line[$idx++];
    my $right_site= $line[$idx++];
    my $left_host= $line[$idx++];
    my $right_host= $line[$idx++];
    my $typ= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= $line[$idx++];


    if ($right_site eq $site) {
      my $tmp= $right_site;
      $right_site= $left_site;
      $left_site= $tmp;
      $tmp= $right_host;
      $right_host= $left_host;
      $left_host= $tmp;
    }

    my $left=  &showLinkpartner($left_site,$left_host);
    my $right= &showLinkpartner($right_site,$right_host,$left_site);

    my $c= "";
    if ($radioparam) {
      $c.= "<br>$radioparam";
    }
    if ($comment) {
      $c.= "<br>$comment";
    }

    my $ed= "";
    $ed= &editIcon("edge", $id, 1);
    print qq(
      <div style="border-top: 1px #d0d0d0 solid;padding-top:10px;">
      <table class="linktab">
      <tr>
      <td width="37%">$left</td>
      <td width="26%" align="center">
        Edge - $typ<br>
        $ed <a class='ovinfo' href="?q=$left_site:$right_site"
               >$left_site:$right_site</a><br>
        <img src="arrow.png">
        $c<br>
      </td>
      <td width="37%">$right</td>
      </tr>
      </table>
      </div>
    );
  }
}

# ---------------------------------------------------------------------------
sub showLinkByIP {
  my $search= shift;
  my @line= ();
  return 0 unless $search=~/^$ipPattern$/;
  my $left_ip= $1;
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
    my $radioparam= $line[$idx++];
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

    my $left= &showLinkpartner($host_site{$left_ip},$left_ip);
    my $right= "";

    foreach $ip (sort keys %host_site) {
      next if $ip eq $left_ip;
      $right.= &showLinkpartner($host_site{$ip},$ip,$host_site{$left_ip});
      $right_ip= $ip;
    }
    
    #get hosts and rssi values
    my $monitor_left;
    $sql=qq(select 
      ip
      from hamnet_host
      where 
      monitor=1 and rawip > $begin_ip and 
      rawip < $end_ip and site='$host_site{$left_ip}'
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
      rawip < $end_ip and site='$host_site{$right_ip}'
    );
    my $sth= $db->prepare($sql);
    $sth->execute;
    while (@line= $sth->fetchrow_array) {
      my $idx= 0;
      $monitor_right= $line[$idx++];
    }
   
    my $c= "";
    if ($radioparam) {
      $c.= "<br>$radioparam";
    }
    if ($comment) {
      $c.= "<br>$comment";
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
    my $ed= "";
    $ed= &editIcon("subnet", $id, 1);
    print qq(
      <div style="border-top: 1px #d0d0d0 solid;padding-top:10px;">
      <table class="linktab">
      <tr>
      <td width="37%">$left</td>
      <td width="26%" align="center">
        $typ<br>
        $ed <a class='ovinfo' href="?q=$ip">$ip</a><br>
        <img src="arrow.png">
        $c<br>
        <span alt="RSSI see help">$rssi</span>
      </td>
      <td width="37%">$right</td>
      </tr>
      </table>
      </div>
    );
    return 1;
  }
  return 0;
}

# ---------------------------------------------------------------------------
# Format one half of a link to screen
sub showLinkpartner {
  my $own_site= shift;
  my $own_ip= shift;
  my $peer_site= shift;

  # HACK: remember for later...
  $is_linkpartner{$own_site}= 1;

  my $sth= $db->prepare(qq(
    select id,name,latitude,longitude,elevation from hamnet_site
    where callsign='$own_site'
  ));
  if ($sth->execute && (@line= $sth->fetchrow_array)) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $name= $line[$idx++];
    my $lat= $line[$idx++];
    my $long= $line[$idx++];
    my $ele= $line[$idx++];

    my $linkInfo= "";
    if ($peer_site) {
      my $sth= $db->prepare(qq(
        select latitude,longitude,elevation from hamnet_site
        where callsign='$peer_site'
      ));
      if ($sth->execute && (@line= $sth->fetchrow_array)) {
        my $idx= 0;
        my $peer_lat= $line[$idx++];
        my $peer_long= $line[$idx++];
        my $peer_ele= $line[$idx++];

        my $dist= &distance($peer_lat,$peer_long,$lat,$long);
        if ($dist>0) {
          $dist= sprintf(" %0.1fkm", $dist);
          $dist.= " - ".&bearing($peer_lat,$peer_long,$lat,$long);
          $linkInfo.=
              qq(<br>$dist - <a target='_blank' href=').
              qq(map.cgi?mb_lat=$lat&mb_lon=$long&mb_tow=$ele&mb_lab=$own_site&).
              qq(ma_lat=$peer_lat&ma_lon=$peer_long&ma_tow=$peer_ele&ma_lab=$peer_site' ).
              #qq(http://ham.remote-area.net/linktool/index?F=58).
              #qq(&RZ0=$peer_site&RZ1=$own_site&P0B=$peer_lat&P0L=$peer_long).
              #qq(&P1B=$lat&P1L=$long&H0=$peer_ele&H1=$ele).
              #qq(&RZ0a=$peer_site&RZ1a=$own_site&Senden=HAMNETDB' ).
              qq(title='Show link in Map'>).
              qq(Show in Linktool</a>);
        }
        else {
          $linkInfo.= "<br>0m";
        }
      }
    }

    my $hostInfo= "";
    if ($own_ip) {
      my $sth= $db->prepare(qq(
        select id,mac,name,typ,radioparam,comment from hamnet_host
        where ip='$own_ip'
      ));
      if ($sth->execute && (@line= $sth->fetchrow_array)) {
        my $idx= 0;
        my $id= $line[$idx++];
        my $mac= $line[$idx++];
        my $name= $line[$idx++];
        my $typ= $line[$idx++];
        my $radioparam= $line[$idx++];
        my $comment= $line[$idx++];

        $hostInfo= qq($name<br>).&editIcon("host", $id, 1).
            qq( <a class="ovinfo" href="?q=$own_ip">$own_ip</a>);

        if ($radioparam) {
          $hostInfo.= "<br>" if $hostInfo;
          $hostInfo.=  &maxlen($radioparam,$commentMax);
        }
        if ($mac) {
          $hostInfo.= "<br>" if $hostInfo;
          $hostInfo.= $mac;

          $hostInfo.= " &nbsp;&nbsp; <b>(shared)</b>" 
              if $host_mac_is_shared{$own_ip};
        }
        unless ($typ=~/Radio/i) {
          $hostInfo.= "<br>" if $hostInfo;
          $hostInfo.= "<b>$typ</b>";
        }
        if ($comment) {
          $hostInfo.= "<br>" if $hostInfo;
          $hostInfo.= &maxlen($comment,$commentMax);
        }
        $hostInfo= "<br>$hostInfo" if $hostInfo;
      }
    }
    return qq(
      <div class="linkpartner vgradr">).&editIcon("site", $id, 1).qq(
      <a class='ovinfo' href="?q=$own_site"><b>$own_site</b></a> 
      ($name)
      $hostInfo
      $linkInfo
      </div>
    );
  }
  return 
    qq(<br><b>Error: link partner '$own_site:$own_ip' not found.</b><br><br>);
}

# ---------------------------------------------------------------------------
sub asShow {
  my $search= shift;
  my @line= ();
  my $t= "as";
  return 0 unless $search;

  $search=~s/as *//i;

  my $sth= $db->prepare(qq(
    select id,name,as_num,as_root,comment,maintainer,country
    editor, date(edited)
    from hamnet_$t where as_num=).$db->quote($search)
  );
 
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $name= $line[$idx++];
    my $as_num= $line[$idx++];
    my $as_root= $line[$idx++];
    my $comment= $line[$idx++];
    my $maintainer= $line[$idx++];
    my $country= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];
  
    $comment= &escComment($comment);

    print qq(<div class="infobox vgrad">);
    &mapMenu($as_num, "");

    print qq(<h2>).&editIcon($t, $id, 1);
    print qq(
      AS$as_num - $name</h2>
      Maintainer: <b>$maintainer</b>
      &nbsp;&nbsp;<a href="?q=$country">$country - $tldName{$country}</a>
      <br><br>
      $comment);
    print qq(<div style='text-align:right;font-size:90%'><i>
             Last edited $edited by <b class='ovinfo'>$editor</b></i></div>);
    print qq(
      </div>
    );

    if ($db->selectrow_array("select id 
      from hamnet_$t where as_root=$as_num")) {
      $asWhere= "as_root=$as_num";
      &asList("", "Related to Sub-AS");
    }
    if ($as_root) {
      $asWhere= "as_num=$as_root";
      &asList("", "Related to Root-AS");
    }

    &siteList("", "Sites".&addIcon("site"));
    &subnetList("", "Subnets".&addIcon("subnet", "&as=$as_num"));
    &hostList("", "Hosts".&addIcon("host"));
    return 1;
  }
  return 0;
}

# ---------------------------------------------------------------------------
sub siteList {
  my $search= shift;
  my @list= ();
  my @line= ();
  my $t= "site";
  my $hw= $siteWhere;
  $hw=~s/callsign/site/g;
  my %siteStatus= &hostsStatus($hw, 1);
  
  my $sth= $db->prepare(qq(
    select id,name,callsign,longitude,latitude,elevation,no_check,
    radioparam,comment,maintainer,editor,unix_timestamp(edited) 
    from hamnet_${t} where $siteWhere
  ));
  $sth->execute;
  
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $name= $line[$idx++];
    my $callsign= $line[$idx++];
    my $longitude= $line[$idx++];
    my $latitude= $line[$idx++];
    my $elevation= $line[$idx++];
    my $no_check= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= $line[$idx++];
    my $maintainer= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];
    $maintainer=~s/[\s,]+/,/g;
#/
    my $in= "";
    $in= " inactive" if $no_check>1 && $no_check<4;
    
    my $ret= qq(<tr id='tr_${t}_$id' class='listentry$in'>).
             &editIcon($t, $id);

    if ($callsign=~/nocall/) {
      $sort= "zzz$name" if $scrit eq "c";
      $ret.= qq(<td valign=top><a class='ovinfo' ovinfo='$callsign' 
        href='?q=$callsign' style='color:#909090'>No Call</a></td>);
    }
    else {
      $sort= $callsign if $scrit eq "c";
      $ret.= "<td valign=top>".
         "<a class='ovinfo' href='?q=$callsign'>$callsign</a></td>\n"; 
    }
    
    $ret.= qq(<td width='14'>$siteStatus{$callsign}</td>);
    $sort= $siteStatus{$callsign} if $scrit eq "x";

    $ret.= "<td valign=top>".&maxlen($name,$nameMax)."</td>\n"; 
    $sort= $name if ($scrit eq "n");

    $ret.= "<td valign=top>".&maxlen($maintainer,$maintainMax)."</td>\n"; 
    $sort= $maintainer if ($scrit eq "m");

    $ret.= "<td valign=top>".&maxlen($radioparam,$maintainMax)."</td>\n"; 
    $sort= $radioparam if ($scrit eq "r");

    $ret.= "<td valign=top>".&maxlen($comment, $commentMax)."</td>\n"; 
    $sort= $comment if ($scrit eq "k");

    $ret.= "<td>".&timespan(time-$edited).
           " <span class='ovinfo'>$editor</span></td>";
    $sort= $edited if $scrit eq "z";

    push(@list, $sort.":}".$ret."</tr>\n");
  }

  &listHeader;
  &sortq("e", "") if &editIcon($t);
  &sortq("c", "Callsign");
  &sortq("x", "M");
  &sortq("n", "Location Name");
  &sortq("m", "Maintainer");
  &sortq("r", "User access");
  &sortq("k", "Comment");
  &sortq("zr", "Edited");
  &listHeaderEnd;
  &listOut($search, @list);
}

# ---------------------------------------------------------------------------
sub subnetList {
  my $search= shift;
  my @list= ();
  my @line= ();
  my $t= "subnet";

  ## fetch subnet information (thanks to HB9XAR)
  ## - for network type "Backbone-Network" include alls sites
  ##   within this subnet (actually fetch hosts.site)
  ## - for all other network types do nothing (leave host_site field empty)
  my $sql_statement= qq(
    SELECT
        min(h_s.id), h_s.ip, min(h_s.begin_ip), min(h_s.typ), min(h_s.as_num),
        min(h_s.as_parent), min(h_s.radioparam),
        min(h_s.comment), min(h_s.editor), UNIX_TIMESTAMP(min(h_s.edited)),
        GROUP_CONCAT(distinct(h_h.site) SEPARATOR ',')  AS host_site
    FROM hamnet_subnet h_s
    LEFT JOIN hamnet_host h_h 
      ON  (
        h_h.rawip BETWEEN h_s.begin_ip AND h_s.end_ip-1 AND
        h_s.typ NOT IN ("AS-Backbone","AS-User/Services","AS-Packet-Radio")
      )
    WHERE $subnetWhere
    GROUP BY h_s.ip
  );
  # when the full list shall be fetched, do not join to hosts
  # for the sake of performance
  if ($subnetWhere eq "1") {
    $sql_statement= qq(SELECT
      id, ip, begin_ip, typ, as_num, as_parent, radioparam,
      comment,editor,unix_timestamp(edited),""
      FROM hamnet_subnet h_s
    );
  }
  my $sth= $db->prepare($sql_statement);
  $sth->execute;

  my $auto_site=0;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $ip= $line[$idx++];
    my $begin_ip= $line[$idx++];
    my $typ= $line[$idx++];
    my $as_num= $line[$idx++];
    my $as_parent= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];
    my $host_site= $line[$idx++];
    next if $subnetWasShown{$ip};

    $radioparam=~s/\s*mhz/MHz/gi;
    $radioparam=~s/\s*,\s*/,/g;
#/
    $radioparam.= " - " if $radioparam && $comment;
    $radioparam.= $comment if $comment;


    my $ret= qq(<tr id='tr_${t}_$id' class='listentry'>).&editIcon($t, $id);
    
    my $bits;
    if ($ip=~/\/(\d+)/) {
      $bits= $1;
    }

    # Mark AS networks
    my $bb= "";
    my $be= "";
    my $in= "&nbsp;&nbsp;";
    if ($typ=~/AS-/) {
      $bb= "<b>";
      $be= "</b>";
      $in= "";
    }
    if ($typ=~/(User|Service)-Net/) {
      $in= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
    }
    $ret.= "<td valign=top>$in".
           "<a class='ovinfo' href='?q=$ip'>$bb$ip$be</a></td>\n"; 
    $sort= sprintf("%09d%02d", $begin_ip, $bits) if ($scrit eq "c");
    
    $ret.= "<td valign=top>$in$bb$typ$be</td>\n"; 
    $sort= $typ if ($scrit eq "t");

    if ($as_num>0) { $as_num= "AS$as_num"; } else { $as_num= "-" };
    $ret.= "<td valign=top>$as_num</td>\n"; 
    $sort= $as_num if ($scrit eq "a");

    if ($as_parent>0) { 
      $as_parent= 
        "<a class='ovinfo' href='?q=$as_parent'>AS$as_parent</a>\n"; 
    } 
    else { 
      $as_parent= "-" 
    };
    $ret.= "<td valign=top>$as_parent</td>\n"; 
    $sort= $as_parent if ($scrit eq "p");

    my $hs= "";
    $host_site=~s/,$//;
    if ($host_site) {
      # Limit site info to 4 sites
      my @sites= split(/,/, $host_site);
      @sites= () if int(@sites)>4;
      if (@sites) {
        foreach $site (@sites) {
          $hs.= "," if $hs;
          $hs.= "<a href='?q=$site' class='ovinfo'>$site</a>";
        }
        $hs= "<i>$hs</i>";
        $hs.= " - " if $radioparam;
      }
    }
    $ret.= "<td valign=top>$hs".&maxlen($radioparam,$commentMax)."</td>\n"; 
    $sort= $radioparam if ($scrit eq "k");

    $ret.= "<td>".&timespan(time-$edited).
           " <span class='ovinfo'>$editor</span></td>";
    $sort= $edited if $scrit eq "z";

    push(@list, $sort.":}".$ret."</tr>\n");
  }

  &listHeader;
  &sortq("e", "") if &editIcon($t);
  &sortq("c", "Subnet-IP");
  &sortq("t", "Type");
  &sortq("a", "Own AS");
  &sortq("p", "Parent");
  &sortq("k", "Radio parameters / Comment");
  &sortq("zr", "Edited");
  &listHeaderEnd;
  &listOut($search, @list);
}

# ---------------------------------------------------------------------------
sub hostList {
  my $search= shift;
  my $caption= shift;
  my $dhcpFromSubnetWhere= shift;
  my @ipHasHost= ();

  my @list= ();
  my @line= ();
  my $t= "host";

  my %hostsStatus= &hostsStatus($hostWhere);

  my $sth= $db->prepare(qq(
    select id,name,ip,rawip,typ,site,radioparam,
    comment,editor,unix_timestamp(edited)
    from hamnet_$t where $hostWhere
  ));
  $sth->execute;
  my %allSites= ();
  my $lastSite= "";

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $name= $line[$idx++];
    my $ip= $line[$idx++];
    my $rawip= $line[$idx++];
    my $typ= $line[$idx++];
    my $site= $line[$idx++];
    my $radioparam= $line[$idx++];
    my $comment= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];

    $radioparam.= " - " if $radioparam && $comment;
    $radioparam.= $comment if $comment;

    my $ret= qq(<tr id='tr_${t}_$id' class='listentry'>).&editIcon($t, $id);
    $ipHasHost{$ip}= 1;
    $ret.= "<td valign=top>".
           "<a class='ovinfo' href='?q=$ip'>$ip</a></td>\n"; 
    $sort= sprintf("%8d", $rawip) if ($scrit eq "c");
    
    $ret.= qq(<td width='14'>$hostsStatus{$ip}</td>);
    $sort= $hostsStatus{$ip} if $scrit eq "x";

    $ret.= "<td valign=top>$name</td>\n"; 
    $sort= $name if ($scrit eq "n");

    $ret.= "<td valign=top>$typ</td>\n"; 
    $sort= $typ if ($scrit eq "t");

    $ret.= "<td valign=top>".
           "<a class='ovinfo' href='?q=$site'>$site</a></td>\n"; 
    $sort= $site if ($scrit eq "s");
    if ($site) {
      $allSites{$site}= 1;
      $lastSite= $site;
    }

    $ret.= "<td valign=top>".&maxlen($radioparam, $commentMax)."</td>\n"; 
    $sort= $comment if ($scrit eq "k");

    $ret.= "<td>".&timespan(time-$edited).
           " <span class='ovinfo'>$editor</span></td>";
    $sort= $edited if $scrit eq "z";

    push(@list, $sort.":}".$ret."</tr>\n");
  }

  # Generate dhcp-assigned hosts as dummy entries
  if ($dhcpFromSubnetWhere && int(keys %allSites)==1) {
    my $sth= $db->prepare(qq(
      select ip,dhcp_range 
      from hamnet_subnet where $dhcpFromSubnetWhere and dhcp_range<>''
    ));
    $sth->execute;

    while (@line= $sth->fetchrow_array) {
      my $netip= $line[0];
      my $range= $line[1];
      $netip=~s/\d+\/\d+//;
      if ($range=~/^(\d+)-(\d+)$/) {
        my $begin= $1;
        my $end= $2;
        my $comment= "assigned dynamically";

        for ($i= $begin; $i<=$end; $i++) {
          my $ip= $netip.$i;
          my $netipSlash = $netip;
          $netipSlash=~s/\./-/g;
          
          unless ($ipHasHost{$ip}) {
            my $name= "dhcp-$netipSlash$i.$lastSite";

            my $ret= qq(<tr class='listentry'>);
            $ret.= qq(<td></td>) if &editIcon($t);
            $ret.= qq(<td>$ip</td>);
            $sort= sprintf("%8d", &aton($ip)) if ($scrit eq "c");
            
            $ret.= "<td></td><td valign=top>$name</td>\n"; 
            $sort= $name if ($scrit eq "n");

            $ret.= "<td valign=top>DHCP-Range</td>\n"; 
            $sort= $typ if ($scrit eq "t");

            $ret.= "<td valign=top>$lastSite</td>";
            $sort= $lastSite if ($scrit eq "s");

            $ret.= "<td valign=top>$comment</td>\n"; 
            $sort= $comment if ($scrit eq "k");

            $ret.= "<td>0s system</td>";
            $sort= $edited if $scrit eq "z";

            push(@list, $sort.":}".$ret."</tr>\n");
          }
        }
      }
    }
  }

  &listHeader($caption);
  &sortq("e", "") if &editIcon($t);
  &sortq("c", "Host-IP");
  &sortq("x", "M");
  &sortq("n", "Hostname");
  &sortq("t", "Type");
  &sortq("s", "Site");
  &sortq("k", "Radio parameters / Comment");
  &sortq("zr", "Edited");
  &listHeaderEnd;
  &listOut($search, @list);
}

# ---------------------------------------------------------------------------
sub maintainerList {
  my $search= shift;
  my @list= ();
  my @line= ();
  my $t= "maintainer";
  my %activity= ();
  my $filterPerm= lc $query->param("filterPerm");
  $filterPerm=~s/[^a-z]//g;

  my $sth= $db->prepare(qq(
    select callsign,unix_timestamp(last_act) 
    from hamnet_session order by last_act
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    $activity{$line[0]}= $line[1];
  }

  my $where= "1";
  my $sth= $db->prepare(qq(
    select id,callsign,fullname,email,unix_timestamp(last_login),
    comment,permissions,editor,unix_timestamp(edited)
    from hamnet_maintainer where $where
  ));
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $callsign= $line[$idx++];
    my $fullname= $line[$idx++];
    my $email= $line[$idx++];
    my $last_login= $line[$idx++];
    my $comment= $line[$idx++];
    my $permissions= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];

    next unless !$filterPerm || $permissions=~/$filterPerm/i;

    $fullname=~s/ .*// unless $username;
  
    my $ret= qq(<tr id='tr_${t}_$id' class='listentry'>).&editIcon($t, $id);

    $ret.= "<td valign=top>$callsign</td>\n"; 
    #  "<a href='?q=$callsign'>$callsign</a></td>\n"; 
    $sort= $callsign if ($scrit eq "c");
    
    $ret.= "<td valign=top>$fullname</td>\n"; 
    $sort= $fullname if ($scrit eq "n");

    if ($username)  {
      $ret.= "<td valign=top><a href='mailto:$email'>$email</a></td>\n"; 
      $sort= $email if ($scrit eq "e");
    }

    if ($username) {
      if ($last_login>0) {
        $ret.= "<td valign=top>".&timespan(time-$last_login)."</td>\n"; 
      }
      else {
        $ret.= "<td valign=top>-</td>\n"; 
      }
      $sort= sprintf("%012d", $last_login) if ($scrit eq "l");

      if ($activity{$callsign}>0) {
        $ret.= "<td valign=top>".
               &timespan(time-$activity{$callsign})."</td>\n"; 
      }
      else {
        $ret.= "<td valign=top>-</td>\n"; 
      }
      $sort= sprintf("%012d", $activity{$callsign}) if ($scrit eq "a");

      my $p= "";
      $p.= "a" if $permissions=~/as/;
      $p.= "s" if $permissions=~/site/;
      $p.= "h" if $permissions=~/host/;
      $p.= "n" if $permissions=~/subnet/;
      $p.= "m" if $permissions=~/maintainer/;
      $p.= "y" if $permissions=~/sysadmin/ && $mySysPerm;
      $sort= $p if $scrit eq "p";
      $ret.= "<td valign=top>$p</td>\n"; 
    }

    $ret.= "<td valign=top>".&maxlen($comment,$commentMax)."</td>\n"; 
    $sort= $comment if ($scrit eq "k");

    $ret.= "<td>".&timespan(time-$edited).
           " <span class='ovinfo'>$editor</span></td>";
    $sort= $edited if $scrit eq "z";

    push(@list, $sort.":}".$ret."</tr>\n");
  }

  my $p= "";
  $p= " (permission filter: ".(ucfirst $filterPerm).")" if $filterPerm;
  &listHeader("Maintainers with write-access in this database$p");
  &sortq("e", "") if &editIcon($t);
  &sortq("c", "Callsign");
  &sortq("n", "Full Name");
  if ($username) {
    &sortq("e", "eMail");
    &sortq("lr", "Login");
    &sortq("ar", "Act");
    &sortq("p", "Perm");
  }
  &sortq("k", "Comment");
  &sortq("zr", "Edited");
  &listHeaderEnd;
  &listOut($search, @list);
}

# ---------------------------------------------------------------------------
sub overviewList {
  my $cc= shift;
  my @list= ();
  my @line= ();
 
  print qq(
    <style>
    .countries td {
      /*font-size: 16px;*/
    }
    .countries {
      max-width: 400px; !important;
    }
    </style>
    <script>
    </script>
    <table class='list countries'><tr class='listheader'>
    <td><b>Country</b></td>
    <td align=center><b>TLD</b></td>
    <td align=right><b>AS Count</b></td>
    <td align=right><b>Last edit</b></td>
    </tr>
  );

  my $sth= $db->prepare(qq(
    select country,count(id),max(unix_timestamp(edited))
    from hamnet_as 
    group by country
  ));
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $country= $line[$idx++];
    my $as_count= $line[$idx++];
    my $newest= $line[$idx++];
    my $name= $tldName{$country};
    my $pf= "rechts";
    if ($cc eq $country) {
      $pf= "runter";
    }

    my $ret= qq(<tr id='tr_${t}_$country' class='listentry'>);
    $ret.= "<td><a href='?q=$country'>
          <img src='$pf.png' align='absmiddle'> $name</td>\n"; 
    $ret.= "<td align=center>$country</td>\n"; 
    $ret.= "<td align=right>$as_count</td>\n"; 
    $ret.= "<td align=right>".&timespan(time-$newest)."</td>";

    print($ret."</tr>\n");
  }
  print("</table>");

}
# ---------------------------------------------------------------------------
sub asList {
  my $search= shift;
  my @list= ();
  my @line= ();
  my $t= "as";
  my $bynum= $query->param("bynum")+0;

  my $sth= $db->prepare(qq(
    select id,name,as_num,as_root,comment,maintainer,editor,
    unix_timestamp(edited) 
    from hamnet_as where $asWhere
  ));
  $sth->execute;

  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    my $name= $line[$idx++];
    my $as_num= $line[$idx++];
    my $as_root= $line[$idx++];
    my $comment= $line[$idx++];
    my $maintainer= $line[$idx++];
    my $editor= $line[$idx++];
    my $edited= $line[$idx++];
  
    my $ret= qq(<tr id='tr_${t}_$id' class='listentry'>).&editIcon($t, $id);

    my $as_txt= "AS$as_num";
    my $as_sort= sprintf("%010d ",$as_num);
    if ($as_root && !$bynum) {
      $as_txt= "&nbsp;&nbsp;AS$as_root &gt; AS$as_num";
      $as_sort= sprintf("%010d-$as_num",$as_root);
    }

    $ret.= "<td valign=top>".
      "<a class='ovinfo' ovinfo='AS$as_num' href='?q=$as_num'>".
      "$as_txt</a></td>\n"; 
    $sort= $as_sort if ($scrit eq "c");
    
    $ret.= "<td valign=top>$name</td>\n"; 
    $sort= $name if ($scrit eq "n");

    $maintainer=~s/,\s+/,/g;

    $ret.= "<td valign=top>".&maxlen($maintainer,$maintainMax)."</td>\n"; 
    $sort= $maintainer if ($scrit eq "m");

    $ret.= "<td valign=top>".&maxlen($comment,$commentMax)."</td>\n"; 
    $sort= $comment if ($scrit eq "k");

    $ret.= "<td>".&timespan(time-$edited). 
           " <span class='ovinfo'>$editor</span></td>";
    $sort= $edited if $scrit eq "z";

    push(@list, $sort.":}".$ret."</tr>\n");
  }

  &listHeader;
  &sortq("e", "") if &editIcon($t);
  &sortq("c", "AS");
  &sortq("n", "Name");
  &sortq("m", "Maintainer");
  &sortq("k", "Comment");
  &sortq("zr", "Edited");
  &listHeaderEnd;
  &listOut($search, @list);
}

# ---------------------------------------------------------------------------
sub loadCheckList {
  my $showHistory= shift;
  my $hist= "";
  $hist= "_hist" if $showHistory;

  my $sth= $db->prepare(qq(
    select id,name,as_num,comment,
    unix_timestamp(edited),editor,deleted
    from hamnet_as$hist order by edited
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    $checkAsName{$id}= $line[$idx++];
    $checkAsNum{$id}= $line[$idx++];
    $checkComment{"as"}{$id}= $line[$idx++];
    $checkEdited{"as"}{$id}= $line[$idx++];
    $checkEditor{"as"}{$id}= $line[$idx++];
    $checkDeleted{"as"}{$id}= $line[$idx++];
  }
  my $sth= $db->prepare(qq(
    select id,name,ip,rawip,typ,radioparam,aliases,comment,
    unix_timestamp(edited),editor,deleted
    from hamnet_host$hist order by edited
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    $checkHostName{$id}= $line[$idx++];
    $checkHostIp{$id}= $line[$idx++];
    $checkHostRawip{$id}= $line[$idx++];
    $checkHostTyp{$id}= $line[$idx++];
    $checkHostRadio{$id}= $line[$idx++];
    $checkHostAliases{$id}= $line[$idx++];
    $checkComment{"host"}{$id}= $line[$idx++];
    $checkEdited{"host"}{$id}= $line[$idx++];
    $checkEditor{"host"}{$id}= $line[$idx++];
    $checkDeleted{"host"}{$id}= $line[$idx++];
  }
  my $sth= $db->prepare(qq(
    select id,callsign,name,latitude,longitude,no_check,comment,
    unix_timestamp(edited),editor,deleted
    from hamnet_site$hist order by edited
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    $checkSiteCall{$id}= $line[$idx++];
    $checkSiteName{$id}= $line[$idx++];
    $checkSiteLatitude{$id}= $line[$idx++];
    $checkSiteLongitude{$id}= $line[$idx++];
    $checkSiteNocheck{$id}= $line[$idx++];
    $checkComment{"site"}{$id}= $line[$idx++];
    $checkEdited{"site"}{$id}= $line[$idx++];
    $checkEditor{"site"}{$id}= $line[$idx++];
    $checkDeleted{"site"}{$id}= $line[$idx++];
  }
  my $sth= $db->prepare(qq(
    select id,ip,begin_ip,end_ip,typ,comment,
    unix_timestamp(edited),editor,deleted
    from hamnet_subnet$hist order by edited
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    $checkSubnetIp{$id}= $line[$idx++];
    $checkSubnetBegin{$id}= $line[$idx++];
    $checkSubnetEnd{$id}= $line[$idx++];
    $checkSubnetTyp{$id}= $line[$idx++];
    $checkComment{"subnet"}{$id}= $line[$idx++];
    $checkEdited{"subnet"}{$id}= $line[$idx++];
    $checkEditor{"subnet"}{$id}= $line[$idx++];
    $checkDeleted{"subnet"}{$id}= $line[$idx++];
  }
  my $sth= $db->prepare(qq(
    select id,left_site,right_site,typ,radioparam,comment,
    unix_timestamp(edited),editor,deleted
    from hamnet_edge$hist order by edited
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    $checkEdgeLink{$id}= $line[$idx++].":".$line[$idx++];
    $checkEdgeTyp{$id}= $line[$idx++];
    $checkEdgeRadio{$id}= $line[$idx++];
    $checkComment{"edge"}{$id}= $line[$idx++];
    $checkEdited{"edge"}{$id}= $line[$idx++];
    $checkEditor{"edge"}{$id}= $line[$idx++];
    $checkDeleted{"edge"}{$id}= $line[$idx++];
  }
  my $sth= $db->prepare(qq(
    select id,callsign,fullname,email,comment,
    unix_timestamp(edited),editor,deleted
    from hamnet_maintainer$hist order by edited
  ));
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $id= $line[$idx++];
    $checkMaintainerCall{$id}= $line[$idx++];
    $checkMaintainerName{$id}= $line[$idx++];
    $checkMaintainerEmail{$id}= $line[$idx++];
    $checkComment{"maintainer"}{$id}= $line[$idx++];
    $checkEdited{"maintainer"}{$id}= $line[$idx++];
    $checkEditor{"maintainer"}{$id}= $line[$idx++];
    $checkDeleted{"maintainer"}{$id}= $line[$idx++];
  }
}

# ---------------------------------------------------------------------------
sub showCheckList {
  @list= ();
  sub add {
    my $t= shift;
    my $id= shift;
    my $name= shift;
    my $comment= shift;
    my $edited= $checkEdited{$t}{$id};
    my $editor= $checkEditor{$t}{$id};

    # Avoid redundand messages for the same object
    return if $findingSeen{"$t-$id"};
    $findingSeen{"$t-$id"}= 1;

    return if $checkComment{$t}{$id}=~/reserv(ed|iert)/i;

    my $ret= qq(<tr id='tr_${t}_$id' class='listentry'>);
    my $sort;

    my $e= &editIcon($t, $id);
    $ret.= $e?$e:"<td>&nbsp;</td>";

    $ret.= qq(<td valign=top>
              <a class='ovinfo' href="?q=$name">$name</a></td>); 
    $sort= $name if ($scrit eq "c");

    my $ele= ucfirst $t;
    $ret.= "<td valign=top>$ele</td>\n"; 
    $sort= $ele if ($scrit eq "t");

    $ret.= "<td valign=top>".&maxlen($comment, $commentMax)."</td>\n"; 
    $sort= $comment if ($scrit eq "k");

    $ret.= "<td>".&timespan(time-$edited).
           " <span class='ovinfo'>$editor</span></td>";
    $sort= $edited if $scrit eq "z";

    push(@list, $sort.":}".$ret."</tr>\n");
  }

  foreach $siteId (keys %checkSiteCall) {
    next if $checkSiteNocheck{$siteId};
    my $hostOk= 0;
    foreach $hostId (keys %checkHostName) {
      if ($checkHostName{$hostId}=~/^(router.|web.|)$checkSiteCall{$siteId}$/){
        if ($checkHostTyp{$hostId}=~/Routing/i) {
          &add("host",$hostId,$checkHostIp{$hostId},
          "'$checkHostName{$hostId}' has callsign as hostname but wrong type");
        }
        else {
          $hostOk= 1;
          my $siteNetFound= 0;
          foreach $subnetId (keys %checkSubnetIp) {
            if ($checkSubnetBegin{$subnetId}<=$checkHostRawip{$hostId} &&
                $checkSubnetEnd{$subnetId}>$checkHostRawip{$hostId}) {
              if ($checkSubnetTyp{$subnetId}=~/Site-Network/) {
                $siteNetFound= 1;
              }
              elsif (! $checkSubnetTyp{$subnetId}=~/AS-User/) {
                &add("subnet",$subnetId,$checkSubnetIp{$subnetId},
                  "Network should be a Site-Network");
              }
            }
          }
          unless ($siteNetFound) {
            &add("site",$siteId,$checkSiteCall{$siteId},
                 "Site has no Site-Network around ip ".
                 "$checkHostIp{$hostId} ($checkHostName{$hostId})");
          }
        }
      }
    }
    unless ($hostOk) {
      #&add("site",$siteId,$checkSiteCall{$siteId},
      #     "Site has no associated host entry for node ip");
    }
  }
  foreach $hostId (keys %checkHostName) {
    my $subnetFound= 0;
    my $asNetFound= 0;

    foreach $subnetId (keys %checkSubnetIp) {
      if ($checkSubnetBegin{$subnetId}<=$checkHostRawip{$hostId} &&
          $checkSubnetEnd{$subnetId}>$checkHostRawip{$hostId}) {

        if ($checkSubnetBegin{$subnetId}==$checkHostRawip{$hostId}) {
          if ($checkSubnetEnd{$subnetId}-$checkSubnetBegin{$subnetId}>2) {
            &add("host",$hostId,$checkHostIp{$hostId},
              "Host '$checkHostName{$hostId}' has network address ".
              "'$checkSubnetIp{$subnetId}'");
          }
        }
        if ($checkSubnetTyp{$subnetId}=~/AS-/) {
          $asNetFound= 1;
        }
        elsif ($checkHostTyp{$hostId}=~/Routing-/) {
          if ($checkSubnetTyp{$subnetId}=~/Backbone/) {
            $subnetFound= 1;
          }
          else {
            &add("host",$hostId,$checkHostIp{$hostId},
              "Routing host should not be in service network ".
              "$checkSubnetIp{$subnetId} ($checkSubnetTyp{$subnetId})");
          }
        }
        else {
          $subnetFound= 1;
        }
      }
    }
    unless ($subnetFound) {
      &add("host",$hostId,$checkHostIp{$hostId},
        "No appropriate subnet found for host '$checkHostName{$hostId}'");
    }
    unless ($asNetFound) {
      &add("host",$hostId,$checkHostIp{$hostId},
        "No appropriate AS network found for host '$checkHostName{$hostId}'");
    }
  }
  foreach $subnetId (keys %checkSubnetIp) {
    my $hostFound= 0;
    my $apFound= 0;
    my $staFound= 0;
    foreach $hostId (keys %checkHostName) {
      if ($checkSubnetBegin{$subnetId}<=$checkHostRawip{$hostId} &&
          $checkSubnetEnd{$subnetId}>$checkHostRawip{$hostId}) {
        $hostFound= 1;
        if ($checkHostRadio{$hostId}=~/^ap/i) {
          $apFound++;
        }
        if ($checkHostRadio{$hostId}=~/^sta/i) {
          $staFound++;
        }
      }
    }
    if ($hostFound) {
      if ($checkSubnetTyp{$subnetId}=~/^Trans-Radio/i) {
        if ($apFound>1) {
          &add("subnet",$subnetId,$checkSubnetIp{$subnetId},
            "$checkSubnetTyp{$subnetId} contains $apFound access points");
        }
        if ($apFound==0) {
          &add("subnet",$subnetId,$checkSubnetIp{$subnetId},
            "$checkSubnetTyp{$subnetId} contains no access points");
        }
        if ($staFound==0) {
          &add("subnet",$subnetId,$checkSubnetIp{$subnetId},
            "$checkSubnetTyp{$subnetId} contains no station mode routers");
        }
      }
    }
    else {
      unless ($checkSubnetTyp{$subnetId}=~/AS-/) {
        &add("subnet",$subnetId,$checkSubnetIp{$subnetId},
          "$checkSubnetTyp{$subnetId} is empty (no host address found)");
      }
    }
  }

  &listHeader("Findings of cross-reference check on the whole database");
  &sortq("e", "");
  &sortq("c", "Name / IP");
  &sortq("t", "Object");
  &sortq("k", "Comment");
  &sortq("zr", "Edited");
  &listHeaderEnd;
  &listOut($search, @list);
}

# ---------------------------------------------------------------------------
sub showHistoryList {
  sub addHistory {
    my $t= shift;
    my $id= shift;
    my $name= shift;
    my $comment= shift;
    my $edited= $checkEdited{$t}{$id};
    my $editor= $checkEditor{$t}{$id};
    my $deleted= $checkDeleted{$t}{$id};
    my $del= "";
    $del= " deleted" if $deleted;

    my $ret= qq(<tr id='tr_${t}_$id' class='listentry$del'>);
    my $sort;

    my $e= &editIcon($t, $id);
    $ret.= $e?$e:"<td>&nbsp;</td>";

    $ret.= "<td>".&timespan(time-$edited).
           " <span class='ovinfo'>$editor</span></td>";
    $sort= $edited if $scrit eq "z";

    $ret.= qq(<td valign=top>
              <a class="ovinfo" href="?q=$name">$name</a></td>); 
    $sort= $name if ($scrit eq "c");

    my $ele= ucfirst $t;
    $ret.= "<td valign=top>$ele</td>\n"; 
    $sort= $ele if ($scrit eq "t");

    $ret.= "<td valign=top>".&maxlen($comment, $commentMax)."</td>\n"; 
    $sort= $comment if ($scrit eq "k");

    push(@list, $sort.":}".$ret."</tr>\n");
  }

  foreach $siteId (keys %checkSiteCall) {
    my $c= $checkSiteName{$siteId};
    $c.= " - ".$checkComment{"site"}{$siteId} if $checkComment{"site"}{$siteId};
    &addHistory("site", $siteId, $checkSiteCall{$siteId}, $c);
  }
  foreach $hostId (keys %checkHostName) {
    my $c= $checkHostName{$hostId}." - ".$checkHostTyp{$hostId};
    $c.= " - ".$checkHostRadio{$hostId} if $checkHostRadio{$hostId};
    $c.= " - ".$checkComment{"host"}{$hostId} if $checkComment{"host"}{$hostId};
    &addHistory("host", $hostId, $checkHostIp{$hostId}, $c);
  }
  foreach $subnetId (keys %checkSubnetIp) {
    my $c= $checkSubnetTyp{$subnetId};
    $c.= " - ".$checkSubnetRadio{$subnetId} if $checkSubnetRadio{$subnetId};
    $c.= " - ".$checkComment{"subnet"}{$subnetId}
                                      if $checkComment{"subnet"}{$subnetId};
    &addHistory("subnet",$subnetId,$checkSubnetIp{$subnetId}, $c);
  }
  foreach $edgeId (keys %checkEdgeLink) {
    my $c= $checkEdgeTyp{$edgeId};
    $c.= " - ".$checkEdgeRadio{$edgeId} if $checkEdgeRadio{$edgeId};
    $c.= " - ".$checkComment{"edge"}{$edgeId}
                                      if $checkComment{"edge"}{$edgeId};
    &addHistory("edge",$edgeId,$checkEdgeLink{$edgeId}, $c);
  }
  foreach $asId (keys %checkAsNum) {
    my $c= $checkAsName{$asId};
    $c.= " - ".$checkComment{"as"}{$asId} if $checkComment{"as"}{$asId};
    &addHistory("as", $asId, "AS$checkAsNum{$asId}", $c);
  }
  foreach $maintainerId (keys %checkMaintainerName) {
    my $c= $checkMaintainerName{$maintainerId}." - ".
           $checkMaintainerEmail{$maintainerId}." ".
           $checkComment{"maintainer"}{$maintainerId};
    $c=~s/ .*// unless $username;              # privacy if not logged in
    &addHistory("maintainer", $maintainerId, 
                $checkMaintainerCall{$maintainerId}, $c);
  }

  $maxLines= 200;
  if ($query->param("func")=~/last(\d+)/) {
    $maxLines= $1;
  }
  if ($query->param("func")=~/all/) {
    $maxLines= 20000;
  }
  my $num= int(@list);
  if ($num>$maxLines) {
    $num= $maxLines;
  }

  &listHeader("The last $num changes of all objects in this database");
  &sortq("e", "");
  &sortq("zr", "Edited");
  &sortq("c", "Name / IP");
  &sortq("t", "Object");
  &sortq("k", "Comment");
  &listHeaderEnd;
  &listOut($search, @list);
}

# ---------------------------------------------------------------------------
sub neighbourList {
  my $id= shift;

  # Show profile inline in table
  print qq(<script>
    function openProfile(tr, left, right) {
      if (jQuery("#d"+tr).length>0) {
        jQuery("#d"+tr).remove();
      }
      else {
        var width= jQuery("#"+tr).width()-12;
        jQuery("#"+tr).after("<tr bgcolor='white'>"+
            "<td colspan=8 id='d"+tr+"'>"+
            "<img src='loading.gif'></td></tr>");
        jQuery("#d"+tr).load("profile.cgi?left="+left+
            "&right="+right+"&width="+width);
      }
    }
  </script>);

  my $sth= $db->prepare(qq(
    select callsign,hamnet_site.id,hamnet_site.name,
    latitude,longitude,elevation,no_check,max(hamnet_host.rawip)
    from hamnet_site
    left join hamnet_host on hamnet_host.site=callsign
    group by hamnet_site.callsign
  ));
  $sth->execute;

  my @line;
  while (@line= $sth->fetchrow_array) {
    my $idx= 0;
    my $callsign= $line[$idx++];
    my $id= $line[$idx++];

    $siteId{$callsign}=  $id;
    $siteCall{$id}= $callsign;
    $siteName{$callsign}= $line[$idx++];
    $siteLat{$callsign}=  $line[$idx++];
    $siteLong{$callsign}= $line[$idx++];
    $siteElev{$callsign}= $line[$idx++];
    $siteno_check{$callsign}= $line[$idx++];
    $site_host{$callsign}= $line[$idx++];
  }

  unless ($siteCall{$id}) {
    print("<h3>Site not found</h3>");
    return;
  }
  my $site= $siteCall{$id};

  $scrit= "d";
  $srev= "";

  my @list;
  foreach $callsign (keys %siteName) {
    my $idx= 0;
    my $id= $siteId{$callsign};
    my $name= $siteName{$callsign};
    my $latitude= $siteLat{$callsign};
    my $longitude= $siteLong{$callsign};
    my $elevation= $siteElev{$callsign};
    my $dist= &distance($siteLat{$site},$siteLong{$site},
                        $latitude, $longitude);

    my $in= "";
    $in= " inactive" if $siteno_check{$callsign}>1 &&$siteno_check{$callsign}<4 ;

    next if $callsign eq $site;
    next if $dist>400;

    my $bear= &bearing($siteLat{$site},$siteLong{$site},
                       $latitude, $longitude);

    my $ret= qq(<tr id='tr_site_$id' class='listentry$in'>).
             &editIcon("site", $id);

    if ($callsign=~/nocall/) {
      $sort= "zzz$name" if $scrit eq "c";
      $ret.= qq(<td valign=top><a class='ovinfo' ovinfo='$callsign' 
        href='?q=$callsign' style='color:#909090'>No Call</a></td>);
    }
    else {
      $sort= $callsign if $scrit eq "c";
      $ret.= "<td valign=top>".
         "<a class='ovinfo' href='?q=$callsign'>$callsign</a></td>\n"; 
    }
    
    $ret.= "<td valign=top>".&maxlen($name,$nameMax)."</td>\n"; 
    $sort= $name if ($scrit eq "n");

    $ret.= "<td align=right>".sprintf("%0.1f km", $dist)."&nbsp;</td>";
    $sort= sprintf("%9.3f", $dist) if $scrit eq "d";

    $ret.= "<td align=right>$bear&nbsp;</td>";

    $ret.= "<td align=right>$elevation m&nbsp;</td>";

    if (&editIcon("edge")) {
      if ($site_host{$callsign} && !$is_linkpartner{$callsign}) {
        $ret.= "<td align=right>".
          &addIcon("edge","&left_site=$site&right_site=$callsign")."</td>";
      }
      else {
        $ret.= "<td align=right>&nbsp;</td>";
      }
    }

    my $prof= "openProfile('tr_site_$id','$site','$callsign')";
    $ret.= qq(<td><a title="Show terrain profile to check line of sight" ).
      qq(href="javascript:$prof">Profile</a> | <a href=').
      qq(map.cgi?ma_lat=$siteLat{$site}&ma_lon=$siteLong{$site}).
      qq(&ma_tow=$siteElev{$site}&ma_lab=$site&).
      qq(mb_lat=$siteLat{$callsign}&mb_lon=$siteLong{$callsign}).
      qq(&mb_tow=$siteElev{$callsign}&mb_lab=$callsign').
      qq(target='_blank'>Show in linktool</a></td>);
      #qq(<a href='http://ham.remote-area.net/linktool/index?F=58).
      #qq(&RZ0=$site&RZ1=$callsign).
      #qq(&P0B=$siteLat{$site}&P0L=$siteLong{$site}).
      #qq(&P1B=$siteLat{$callsign}&P1L=$siteLong{$callsign}).
      #qq(&H0=$siteElev{$site}&H1=$siteElev{$callsign}).
      #qq(&RZ0a=$site&RZ1a=$callsign).
      #qq(&Senden=HAMNETDB' target='_blank'>Show in linktool</a></td>);

    push(@list, $sort.":}".$ret."</tr>\n");
  }

  &listHeader("Other sites near $site");
  &sortq("e", "") if &editIcon("site");
  &sortq("c", "Site");
  &sortq("n", "Name");
  &sortq("d", "Distance", "align=right");
  &sortq("b", "Direction", "align=right");
  &sortq("e", "Above ground", "align=right");
  #&sortq("a", "Above sea level", "align=right");
  &sortq("g", "Edge", "align=right") if &editIcon("subnet");
  &sortq("l", "");
  &listHeaderEnd;
  $maxLines= 100;
  if ($query->param("func")=~/all/) {
    $maxLines= 1000;
  }  
  &listOut("", @list);
}

# ---------------------------------------------------------------------------
sub mapMenu {
  my $as= shift;
  my $site= shift;
  $as+= 0;
  $site.= "";
  print qq(<div style="float:right">);
  $showFuncDef{"tab"}= -1;
  my $clientIP= $query->remote_host();
  my $mapHamnet="0";
  $mapHamnet=checkMapSource();
  print qq(<script>
    function showtab(val) {
      if (val == "full") {
        hamnetdb.openMap(1, $as, "$site", $mapHamnet);
      }
      else if (val == "map") {
        hamnetdb.openMap(0, $as, "$site", $mapHamnet);
      }
      else {
        document.main.tab.value= val;
        document.main.submit();
      }
    }
  </script>);
  my $tab= &subMenu("tab:Show", "map:Map","full:Fullscreen Map");
  print qq(</div>);
}
