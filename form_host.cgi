#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Host input form
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
do "form.cgi" or die;

$suffix= "host";
$table= "hamnet_$suffix";
$table_history= "${table}_hist";
$requiredPermission= $suffix;

($name,$ip,$rawip,$mac,$aliases,$typ,$radioparam,$site,$no_ping,$monitor,
  $routing,$comment,$rw_maint)= &loadFormData
  ("name,ip,rawip,mac,aliases,typ,radioparam,site,no_ping,monitor,routing,comment,rw_maint");

$no_ping+= 0;
$monitor+= 0;
$routing+= 0;

# If possible, fetch maintainer-list from site since a host has no maintainers
# Do it only if site is also locked, otherwise it would not have any effect
my $maintainer= "";
if ($site) {
  ($maintainer)= $db->selectrow_array(qq(select maintainer from hamnet_site
    where rw_maint>0 and callsign=).$db->quote($site));

  #$name= ".$site" unless $id;
  unless($id) {
      $name= ".$site" unless $ip;
  }
  #if($id1) {
  #  $name= ".$site"
  #}
  &checkMaintainerRW($rw_maint, $maintainer);
  
}
unless ($maintainer) {
  $rw_maint= 0;
}

if ($mustLoadFromDB) {
  if ($radioparam=~s/^ap *(bridge|)//i) {
    $radio_mode= "AP Bridge";
  }
  if ($radioparam=~s/^sta(tion|)//i) {
    $radio_mode= "Station";
  }
  if ($radioparam=~s/^ *wds//i) {
    $radio_mode.= " WDS";
  }
  if ($radioparam=~s/ *\(*nstreme\)*//i) {
    $radio_mode.= " (NStreme)";
  }
  if ($radioparam=~s/ *\(*airmax\)*//i) {
    $radio_mode.= " (AirMax)";
  }
  $radioparam=~s/^[\s,]*//;
  $radio_remarks= $radioparam;
}
else {
  $radio_mode= $query->param("radio_mode");
  $radio_remarks= $query->param("radio_remarks");
}

$caption= "Change $suffix '$name'";
$caption= "New $suffix $maintainer" unless $id;
&beforeForm($caption);

print qq(
  <div class="formnline">
    <div class="formn1">
     <label align="left" nowrap>IP:</label><br>
     <input type="text" name="ip" value="$ip" size=12$chtrack>
    </div>
    
    <div class="formn2">
      <label align="left" nowrap>Host name (end with .callsign):</label><br>
      <input type="text" name="name" value="$name" size=25$chtrack>
    </div>
    <div class="formn3">
      <label align="left" nowrap>MAC of radio interface:</label><br>
      <input type="text" name="mac" value="$mac" size=15$chtrack>
    </div>
  </div>
  <div class="formnline"> 
    <div class="formn1">
      <label align="left" nowrap>Host type:</label><br>
);

$typ= "Service" unless $typ;

&comboBox("", "typ", $typ, 
          "Routing-Radio", "Routing-ISM", "Routing-Ethernet", "Routing-Tunnel",
          "Service");

print qq(
    </div>
  
    <div class="formn2 select_max_width" >
      <label align="left" nowrap colspan=2 class="select_max_width" >Belonging to site:</label><br>
);

my $sth= $db->prepare("select ".
         "callsign,name from hamnet_site order by callsign");
$sth->execute;
while (@line= $sth->fetchrow_array) {
  next if $line[0]=~/nocall/;
  push(@sites, "$line[0]::$line[0] - $line[1]");
}
&comboBoxSearch("", "site", $site, "::-None-", @sites);

print qq(
    </div>

    <div class="formn3">
);

&checkBox("No ping check", "no_ping", 1, $no_ping);

&checkBox("Monitor", "monitor", 1, $monitor);
&checkBox("Routing", "routing", 1, $routing);
print qq(
    </div>
  </div>
  <div class="formnline">
    <div class="formnfull" align="left" nowrap style="width:98%;">
      <label>DNS aliases (CNAME, optional, end with .callsign):</label><br>
      <input type="text" name="aliases" value="$aliases" style="width:100%"$chtrack>
    </div>
  </div>
  <div class="formnline" style="padding-top:15px;padding-bottom:15px">
    
    Radio config parameters 
    (only site-specific parameters, for common see subnet):<br>
    <div class="formn1" 
      align="left">
);
  <div class="formn2 select_site_width" >
&comboBox("Mode:", "radio_mode", $radio_mode, "", 
  "AP Bridge (NStreme)",
  "AP Bridge (AirMax)",
  "AP Bridge",
  "Station WDS (NStreme)",
  "Station (AirMax)",
  "Station");
print qq(
        </div>
      <div class="formn2"> Remarks: <input type="text" name="radio_remarks" value="$radio_remarks" 
        style="width:300px"$chtrack>
      </div>
    </div>
    <h4>Services:</h4>
);

# -----------------------------------------------------------------------------
# Service Start

#ToDo:
#  JS-update host+alias
#  ?keep untouched in serice-list
#  service-version = host-version
#    check + save  service
#  ?site call change => service call change
#
#  service list   @ host
#                 @ site
#                 @ last changes
#                 @ export

my $sth= $db->prepare("select ".
         "name from hamnet_servicetag order by hierarchy");
$sth->execute;
while (@line= $sth->fetchrow_array) {
  next if $line[0]=~/nocall/;
  push(@servicetags, "$line[0]");
}
my @dns;
push(@dns,'-None-',$name);
foreach $n (split(/,/, $aliases)) {
  push(@dns,$n);
}

print qq(<div id="serviceHidden" class="invisible">);
#addService('cnt',id,'name','host-name','port','parameters','Description','services');
addService('',0,'','','','','','');
print qq(</div>
  <div id="servicelist">);

my $serviceCnt= 0;
if ($mustLoadFromDB) {
  my $sqlFrom= "from hamnet_service where";
  if ($table_history && $newversion && $id) {
    $sqlFrom= "from hamnet_service_hist ".
              "where version='$newversion' and";
  }
  my $sth= $db->prepare(
      "select id, name, dns, port, parameters, description, tags $sqlFrom host_id=$id");
  $sth->execute;
  #my $serviceCnt=0;
  while (@line= $sth->fetchrow_array) {
    $serviceCnt+= 1;
    addService($serviceCnt,$line[0],$line[1],$line[2],$line[3],$line[4],$line[5],$line[6]);
  }
}
else {
  # http Post values
  my $maxCnt= 0;
  my $Cnt= 0;
  if ($query->param("servicecnt")+0 > 100) {
    $maxCnt= 100;
  }
  else {
    $maxCnt= $query->param("servicecnt")+0;
  }
  
  while ($Cnt < $maxCnt) {
    $serviceCnt+=1;
    $Cnt+=1;
    my $serviceId= $query->param("ID$Cnt");
    my $serviceName= $query->param("servicename$Cnt");
    my $serviceDns= $query->param("servicedns$Cnt");
    my $servicePort= $query->param("serviceport$Cnt");
    my $serviceParam= $query->param("serviceparam$Cnt");
    my $serviceDesc= $query->param("servicedesc$Cnt");
    my @serviceTag= $query->param("servicetags$Cnt");
    my $taglist;
    foreach (@serviceTag) {
      $taglist.= "$_,";
    }
    if ($serviceDns) {
      addService($serviceCnt, $serviceId, $serviceName, $serviceDns, $servicePort, $serviceParam, $serviceDesc, $taglist);
    }
    #print qq(tag: $taglist  dns: $serviceDns $Cnt<br>\n );
    
  }
}
print qq(</div>);

print qq(
  <script language="JavaScript">
    function serviceAdd() {
      cnt= parseInt(document.getElementById("servicecnt").value);
      cnt+= 1;
      plainservice= document.getElementById('serviceHidden').innerHTML;
      services= document.getElementById('servicelist');
      services.innerHTML= services.innerHTML+plainservice;
      size= services.getElementsByClassName('formnline').length;
      newservice= services.getElementsByClassName('formnline')[size-1];
      newservice.id= newservice.id+cnt;
      inputsize= newservice.getElementsByTagName('input').length;
      for (i= 0; i< inputsize; i++) {
        oldname=newservice.getElementsByTagName('input')[i].getAttribute('name');
        newservice.getElementsByTagName('input')[i].setAttribute('name',oldname+cnt);
      }
      inputsize= newservice.getElementsByTagName('select').length;
      for (i= 0; i< inputsize; i++) {
        oldname=newservice.getElementsByTagName('select')[i].getAttribute('name');
        newservice.getElementsByTagName('select')[i].setAttribute('name',oldname+cnt);
        if (oldname == "servicetags") {
          newservice.getElementsByTagName('select')[i].id= "comboBoxMultiSearch"+cnt;
        }
      }
      document.getElementById("servicecnt").value= cnt;
      // Initialize select2
      \$("#comboBoxMultiSearch"+cnt).select2({
        placeholder: "Add Tag"  });
    }
    function serviceDel(e) {
      changed();
      e.parentElement.parentElement.remove();
    }
  </script>
  <input type="hidden" id="servicecnt" name="servicecnt" value="$serviceCnt">

    <div class="formnline">
      <div class="formn1">
        <a onclick="serviceAdd();"><b>+</b> add Service</a>
      </div>
    </div>
);
# -----------------------------------------------------------------------------
# Service end

print qq(<div class="formnline">);
if (&inList($username, $maintainer) || ($maintainer && $mySysPerm)) {
  &checkBox("Restrict write access to list of site maintainers",
            "rw_maint", 1, $rw_maint);
}

print qq(
  Comment area:<br>
  <textarea name="comment" class="txt" $chtrack
            style="width:100%; height:160px;">$comment</textarea>
  </div>
);
&afterFormn;
exit;


# --------------------------------------------------------------------------
# check and store values
sub checkValues {
  #$inputStatus= "Debug ".$a;
  $name= lc $name;
  unless ($name) {
    $inputStatus= "Name is missing";
  }
  if ($name=~/[^0-9a-z\-\.]/) {
    $inputStatus= "Name contains invalid characters";
  }
  unless (&ipCheck($ip)) {
    $inputStatus= "IP is not a valid IP address";
  }
  $rw_maint+= 0;

  $radioparam= $radio_mode;
  $radioparam.= "," if $radio_remarks && $radioparam;
  $radioparam.= $radio_remarks;
  $radioparam= &alignRadioparam($radioparam);
  &checkMaintainerRW($rw_maint, $maintainer);
  if (! $site) {
    $inputStatus= "Host must be assigned to a site";
  }
  
  unless ($inputStatus) {
    #no callsign check for virtual site
    unless ($db->selectrow_array("select callsign, no_check from hamnet_site  ".
              "where callsign='$site' and no_check=5")){
      unless ($name=~/[a-z][0-9]+[a-z]+-*\d*$/) {
        $inputStatus= 
          "Host name must end with a callsign to be globally unique";
      } 
    }
  }

  if ($mac) {
    $mac= lc $mac;
    $mac=~s/[^0-9a-f]//g;
    if (length($mac)!=12) {
      $inputStatus= "Invalid mac address - empty or 12 hex digits";
    }
  }
  unless ($inputStatus) {
    if ($name=~/^\./) {
      $inputStatus= "first charater of Host name can't be '.' ";
    }
  }
    
  unless ($inputStatus) {
    if ($db->selectrow_array("select ip from $table ".
          "where ip='$ip' and id<>'$id'")) {
      $inputStatus= "The host '$ip' exists already";
    }
    if ($db->selectrow_array("select name from $table ".
          "where name='$name' and id<>'$id'")) {
      $inputStatus= "The host '$name' exists already";
    }
  }
  unless ($inputStatus) {
    $aliases= lc $aliases;
    if ($aliases) {
      my $al;
      foreach $alias (split(/[\s,;]+/, $aliases)) {
        if ($db->selectrow_array("select name from $table ".
            "where name='$alias' and id<>'$id'")) {
          $inputStatus= "The alias '$alias' exists already as host";
          last;
        }
        unless ($db->selectrow_array("select callsign, no_check from hamnet_site  ".
              "where callsign='$site' and no_check=5")){
          unless ($alias=~/[a-z][0-9]+[a-z]+$/) {
            $inputStatus= 
              "Alias '$alias' must end with a callsign to be globally unique";
            last;
          }  
        }
        if ($alias=~/[^0-9a-z\-\.]/) {
          $inputStatus= "Alias contains invalid characters";
          last;
        }
        $al.= "," if $al;
        $al.= $alias;
      }
      unless ($inputStatus) {
        $aliases= $al;
      }
    }
  }
  unless($inputStatus) {
    if ($typ eq "Routing-Radio"){
      if ($db->selectrow_array("select callsign, no_check from hamnet_site  ".
              "where callsign='$site' and (no_check=4 or no_check=5)")) {
            $inputStatus= "This type of site can't have host of type \"Routing-Radio\"";
      }
    }
    elsif ($typ eq "Routing-ISM"){
      if ($db->selectrow_array("select callsign, no_check from hamnet_site  ".
              "where callsign='$site' and no_check=5")) {
            $inputStatus= "This type of site can't have host of type \"Routing-ISM\"";
      }
    }
  }
  unless ($inputStatus) {
    $inputStatus="aaa";
    $inputStatus= checkService();
  }
  $rawip= &aton($ip);
  return  "comment=".$db->quote($comment).", ".
          "ip=".$db->quote($ip).", ".
          "typ=".$db->quote($typ).", ".
          "mac=".$db->quote($mac).", ".
          "aliases=".$db->quote($aliases).", ".
          "radioparam=".$db->quote($radioparam).", ".
          "site=".$db->quote($site).", ".
          "no_ping=".$db->quote($no_ping).", ".
          "monitor=".$db->quote($monitor).", ".
          "routing=".$db->quote($routing).", ".
          "rw_maint=".$db->quote($rw_maint).", ".
          "rawip=".$db->quote($rawip).", ".
          "name=".$db->quote($name);
  
}

sub checkService {
  #TODO update service DNS?
  my $serviceStatus;
  my $maxCnt= 0;
  my $Cnt= 0;
  my @dns;
  push(@dns,'-None-',$name);
  foreach $n (split(/,/, $aliases)) {
    push(@dns,$n);
  }
  if ($query->param("servicecnt")+0 > 100) {
    $maxCnt= 100;
  }
  else {
    $maxCnt= $query->param("servicecnt")+0;
  }
  
  while ($Cnt < $maxCnt) {
    $Cnt+=1;
    my $serviceId= $query->param("ID$Cnt");
    my $serviceName= $query->param("servicename$Cnt");
    my $serviceDns= $query->param("servicedns$Cnt");
    my $servicePort= $query->param("serviceport$Cnt")+0;
    my $serviceParam= $query->param("serviceparam$Cnt");
    my $serviceDesc= $query->param("servicedesc$Cnt");
    my @serviceTag= $query->param("servicetags$Cnt");
    
    if ($serviceDns) {
      unless ($serviceName) {
        $serviceStatus= "Service name is missing";
      }
      unless ($serviceDesc) {
        $serviceStatus= "Service description is missing";
      }
      if ($servicePort < 1 || $servicePort > 65535 ) {
        $serviceStatus= "Service port is not valid";
      }    
      unless (grep { $_ eq $serviceDns } @dns) {
        $serviceStatus= "Service DNS not in list";
      }    
      foreach (@serviceTag) {
        my $tag= $_; 
        #  $serviceStatus.= "-$tag:$_-";
        #unless (grep { $_ eq $tag } @servicetags) {
        if ( grep( /^$tag$/, @servicetags ) ) {
          $serviceStatus= "Service Tag not valid";
        } 
      }
      if (@serviceTag < 1) {
        $serviceStatus= "At least one Tag has to be chosen for each service";
      }
      unless ($serviceStatus) {
        if (grep( /^Web$/, @serviceTag && length($serviceParam))) {
          unless ($serviceParam =~ m/^\//){
            $serviceStatus="Service of type Web: Parameter must start with '/'";
          }
        }
        elsif (grep( /^PR$/, @serviceTag)) {
          unless ($serviceParam=~/^[a-z0-9]{3,6}-*\d*$/ && $serviceParam=~/[0-9][a-z]-*\d*/) {
            $serviceStatus="Service of type PR: Parameter must contain CALLSIGN-SSID";
          }
        }
      }
    }
  }
  return $serviceStatus;
}

sub storeService {
  #get current version
  my $version;
  my $Cnt= 0;
  my $sth= $db->prepare("select ".
         "version from hamnet_host where id=$id");
  $sth->execute;
  while (@line= $sth->fetchrow_array) {
    $version= $line[0];
  }
  my $maxCnt= 0;
  if ($query->param("servicecnt")+0 > 100) {
    $maxCnt= 100;
  }
  else {
    $maxCnt= $query->param("servicecnt")+0;
  }
  while ($Cnt < $maxCnt) {
    $Cnt+=1;
    my $serviceId= $query->param("ID$Cnt");
    my $serviceName= $query->param("servicename$Cnt");
    my $serviceDns= $query->param("servicedns$Cnt");
    my $servicePort= $query->param("serviceport$Cnt")+0;
    my $serviceParam= $query->param("serviceparam$Cnt");
    my $serviceDesc= $query->param("servicedesc$Cnt");
    my @serviceTag= $query->param("servicetags$Cnt");
    my $taglist;
    foreach (@serviceTag) {
      $taglist.= "$_,";
    }

    if ($serviceDns && !$inputStatus) {

      my $sqlinsert=  "(name, dns, port, parameters, ".
        "description, tags,".
        " host_id, editor, edited, version, deleted)".
        "VALUES ('$serviceName', '$serviceDns', $servicePort,".
        " '$serviceParam', '$serviceDesc', '$taglist',".
        " $id, '$username', NOW(), $version, 0);";
      if ($serviceId) {
        my $sql= "UPDATE hamnet_service SET".
          " name='$serviceName', dns='$serviceDns', port='$servicePort',".
          " parameters='$serviceParam', tags='$taglist',".
          " edited=NOW(), editor='$username', version=$version ".
          "WHERE host_id=$id and id=$serviceId;";
        unless ($db->do($sql)) {
          $inputStatus= "ERROR: DB-Update failed 'Update'";
        } 
        #$inputStatus= $sql;
      }
      else {
        my $sql= "INSERT INTO hamnet_service $sqlinsert";
        unless ($db->do($sql)) {
          $inputStatus= "ERROR: DB-Update failed I1";
        } 
        #$inputStatus= $sql;

      }
      #to archive
      my $sql= "INSERT INTO hamnet_service_hist $sqlinsert";
      unless ($db->do($sql)) {
        $inputStatus= "ERROR: DB-Update failed I2";
      } 
      #$inputStatus= $sql;
    }
  }
  unless ($inputStatus) {
    $sql= "DELETE FROM hamnet_service where host_id=$id ".
     "AND version!=$version";
    unless ($db->do($sql)) {
      $inputStatus= "ERROR: DB-Update failed";
    } 
  }
}

sub deleteService {
  #get current version
  #delete services
}

sub addService {
  my $serviceCnt= shift;
  my $serviceId= shift;
  my $serviceName= shift;
  my $serviceDns= shift;
  my $servicePort= shift;
  my $serviceParam= shift;
  my $serviceDesc= shift;
  my $serviceTags= shift;
  $serviceId+= 0;

  print qq(

    <div class="formnline" id="serviceEntry$serviceCnt">
      <div class="formn1">
        &nbsp;&nbsp;&nbsp;&nbsp; Name:<br>
        <input type="hidden" name="ID$serviceCnt" value="$serviceId">
        <a onclick="serviceDel(this)"><img src="delete.png"></a>&nbsp;
        <input type="text" name="servicename$serviceCnt" value="$serviceName" style="width:130px;" $chtrack>
      </div>
      <div class="formn1">
        Host name:<br>
  );
  &comboBox("", "servicedns$serviceCnt", $serviceDns, @dns);
  print qq(
      </div>
      <div class="formn1">
        Port: <br>
        <input type="text" name="serviceport$serviceCnt" value="$servicePort" style="width:35px;" $chtrack>
      </div>
      <div class="formn1">
        Parameter: <br>
        <input type="text" name="serviceparam$serviceCnt" value="$serviceParam" style="width:150px;" $chtrack>
      </div>
      <div class="formn1">
        Description:<br>
        <input type="text" name="servicedesc$serviceCnt" value="$serviceDesc" style="width:150px;" $chtrack>  
      </div>
      <div class="formn1">
        Tag(s):<br>
  );
  &comboBoxMultiSearch("servicetags$serviceCnt", $serviceTags, "200px","60px", @servicetags);
  print qq(
      </div>
    </div>
    
  );
  return 1;
}
