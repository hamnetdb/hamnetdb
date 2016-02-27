#!/usr/bin/perl
# ---------------------------------------------------------------
# Hamnet IP database - Form utilities
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
# Hubertus Munz
# Lucas Speckbacher, OE2LSP
#
# Licensed under the Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# ---------------------------------------------------------------
#
do "lib.cgi" or die;
# 
# Default-settings
$changedField= "edited";
$tableCols= 4;
$keepDeleted= 0;
$copyButton= 1;
$deleteButton= 1;
$idField= "id";

# Some cgi-parameters, not depending on particluar form
$func=       $query->param("func");
$confirm=    $query->param("confirm")+0;
$id=         $query->param("id")+0 unless $id;
$ischanged=  $query->param("ischanged")+0;
$changedate= $query->param("changedate");
$warning=    $query->param("warning")+0;
$version=    $query->param("version")+0;
$newversion= $query->param("newversion")+0;
$formToken=  $query->param("sessiontoken");
$func=~s/[^a-z]//g;
$formToken=~s/[^0-9a-z_]//gi;

# If necessary, close current window and refresh opener
&checkWinClose($func);

if ($func eq "copy") {
  $id= undef;
  $newversion= 0;
}
$mustLoadFromDB= 0;
if (!($func=~/asnewest|redisp|store|delete/) && $id) {
  $mustLoadFromDB= 1;
}
$func= "delete" if $func eq "delcmd"; # Löschen ohne vorheriges Submit

# Einige Vordefinitionen, um den Code lesbarer zu machen und
# die Werte an einer Stelle stehen zu haben
$chtrack=    qq( onChange="changed()");

$lastChanged= "";
$isOldVersion= 0;

1;

############################################################################
# Nach den vorbereitenden Definitionen wird diese Prozedur vom Nutzer
# aufgerufen, die erst die Tatsächliche Verarbeitung durchführt
sub beforeForm {
  my $caption= shift;
  $caption.= " (Copy)" unless $func ne "copy" || $caption=~/\(Copy\)/;

  unless ($myPermissions=~/$requiredPermission,/) {
    &fatal(qq(Permission denied));
  }

  if ($func=~/store/) {
    &storeEntry;
    # Funktion kommt nie zurück, wenn alles gutgegangen ist.
    # Im Fehlerfall nochmal Edit-Formular aufrufen
  }

  if ($func eq "delete") {
    if ($suffix eq "antenna") {
      #get id from antenna
      $id= &nametoid;
    }
    &deleteEntry;
    # Funktion kommt nie zurück, wenn alles gutgegangen ist.
    # Im Fehlerfall nochmal Edit-Formular aufrufen
  }

   
  my $sqlFrom= "from $table where";
  if ($table_history && $newversion && $id) {
    $sqlFrom= "from $table_history ".
              "where version='$newversion' and";
  }

  if ($mustLoadFromDB) {
    my $sth= $db->prepare("select version,editor,".
             "unix_timestamp($changedField) $sqlFrom $idField='$id'");

    $sth->execute;
    if (@line= $sth->fetchrow_array) {
      my $idx= 0;
      $version= $line[$idx++];
      $editor=  $line[$idx++];
      $edited=  $line[$idx++];
    }
    else {
      $inputStatus= "ERROR: Object not found in database";
    }
    if ($table_history) {
      $undoTxt= "";
      my $lastversion= $version;
      my $ls= (-1);
      my $sth= $db->prepare("select version from $table_history ".
                            "where $idField='$id' ".
                            "order by version desc");
      if ($sth->execute) {
        while (@line= $sth->fetchrow_array) {
          if ($line[0]>($version-6) && $line[0]<($version+6)) {
            if ($line[0]==$version) {
              $undoTxt= "<b>$version</b> $undoTxt";
            }
            else {
              $undoTxt= qq(<a href="javascript:changeVersion($id,$line[0])"
                            class="small"><u>$line[0]</u></a> $undoTxt);
            }
          }
          $ls= $line[0] unless $ls>=0;
        }
      }
      $lastversion= $ls if $ls>=0;
      if ($undoTxt) {
        $undoTxt= 
          qq(<span class="small">Version: $undoTxt &nbsp;-&nbsp;</span> );
      }
      if ($lastversion!=$version) {
        $caption.= qq( <font color="#c00000">- Attic version</font>);
        $isOldVersion= 1;
      }
      else {
        $newversion= "";
      }
    }
  }
  unless ($changedate) {
    $editor= "import" unless $editor;
    if ($edited) {
      my $sptxt= "Edit: ";
      $sptxt= "" if $table_history;
      $changedate= strftime("$sptxt%d.%m.%Y %H:%M ($editor)",
                            localtime($edited));
    }
  }
  $changedate= "New Entry" unless $changedate;
  $lastChanged= $undoTxt.
        qq(<span id="changedtext" class="small">$changedate</span>);

  &htmlWinHead($caption);
  my $capcol= "";
  if ($inputStatus) {
    $capcol=  qq(bgcolor="#ff2020");
    $inputStatus=~s/&/&amp;/g;
    $inputStatus=~s/</&lt;/g;
    $inputStatus=~s/>/&gt;/g;
    $caption= "<font color='white'>$inputStatus</font>";
  }
  else {
    $caption.= ":";
  }
  


  print qq(
  <form name="main" method="POST" enctype="multipart/form-data">
  <input type="hidden" name="func" value="store">
  <input type="hidden" name="id" value="$id">
  <input type="hidden" name="confirm" value="0">
  <input type="hidden" name="warning" value="$warning">
  <input type="hidden" name="ischanged" value="$ischanged">
  <input type="hidden" name="changedate" value="$changedate">
  <input type="hidden" name="sessiontoken" value="$sessionToken">

  <script language="JavaScript">
	  function calcfromIP()
	  {
      changed();
	    ip = document.getElementById("base_ip").value;
	    if(checkIP(ip))
	    {
	      cidr = document.getElementsByName("bits")[0].value;
	      //calcHosts(cidr); //why that
	      if(checkInt(cidr) && cidr > 0 && cidr <= 32)//the easiest way to check if everything is ok
	      {
	        netmask = calcNetmask(cidr);
	        sp_ip = splitIP(ip);
	        sp_nm = splitIP(netmask);
	        var netaddress = new Array();
	        var broadcast = new Array();
	        for(i=0;i<4;i++)
	        {
	          if(sp_nm[i] == 255)//part stays unchanged
	          {
	            netaddress[i]=sp_ip[i];
	            broadcast[i]=sp_ip[i];
	          }
	          else if(sp_nm[i] == 0)
	          {
	            netaddress[i]=0;
	            broadcast[i]=255;
	          }
	          else //lets calc
	          {
	            num=256-sp_nm[i];
	            seg=Math.floor(sp_ip[i]/num);
	            netaddress[i]=num*seg;
	            broadcast[i]=num*(seg+1)-1;
	          }
	        }
          document.getElementById("netaddr_limits").innerHTML="Networkaddress: " + netaddress[0]+"."+netaddress[1]+"."+netaddress[2]+"."+netaddress[3] + "<br>Broadcast: "  + broadcast[0]+"."+broadcast[1]+"."+broadcast[2]+"."+broadcast[3];
	      }
	    }
	    else
	    {
	      document.getElementById("netaddr_limits").innerHTML="";
	    }
	  }
	  function checkIP(ip)
	  {
	    var pattern =/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/;
	    return pattern.test(ip);
	  }
	  function checkInt(val)
	  {
	    var pattern =/^[0-9]+/;
      return pattern.test(val);  
	  }
    function splitIP(ip)
	  {
	    var splitted =new Array();
	    
	    for(var i=0;i<3;i++)
	    {
	      dotpos=ip.indexOf(".");
	      splitted[i]=ip.substring(0,dotpos);
	      ip=ip.substring(dotpos+1);
	    }
	    splitted[3]=ip;
	    return splitted;
	  }
    function calcNetmask(cidr)
    {
      if(cidr > 24)
      {
        dyn=255-(Math.pow(2,32-cidr)-1);
        netmask="255.255.255."+ dyn;
      }
      else if(cidr >16)
      {
        dyn=255-(Math.pow(2,24-cidr)-1);
        netmask="255.255."+ dyn+".0";
      }
      else if(cidr > 8)
      {
        dyn=255-(Math.pow(2,16-cidr)-1);
        netmask="255."+ dyn+".0.0";
      }
      else
      {
        dyn=255-(Math.pow(2,8-cidr)-1);
        netmask= dyn+".0.0.0";
      }
      return netmask;
    }
    var locator_global="";
    function degmin2dec(degmin)
    {
      degmin = degmin.replace(/,/gi,".");
      degmin = degmin.replace(/ /g,"");
      res = degmin.match(/^([\\d\\.]+)°([\\d\\.]+)'([\\d\\.]*)/);     
      if (degmin.match(/^([\\d\\.]+)°([\\d\\.]+)'([\\d\\.]*)/)) {
        degmin= parseFloat(res[1]) + parseFloat(res[2]*(1/60.0)) + parseFloat(res[3]*(1/3600.0));
      }
      return degmin
    }
    function calcCoordinates()
	  {
	    changed();
	    var locator = document.getElementById('locator').value;
	    locator = locator.toUpperCase();
      if(locator == locator_global)//check if has changed
      {
        return;
      }
      else
      {
        locator_global=locator;
      }
	    if(/[A-R]{2}[0-9]{2}/i.test(locator))
      {
      //  var lat= (locator.charCodeAt(1)-65)*10 -90; //Char
     //   var lon= (locator.charCodeAt(0)-65) * 20 -180;//char
      //  lat+= (locator.charCodeAt(3) -48); //number
      //  lon+= (locator.charCodeAt(2)-48) * 2; //number
	    }
      if(/[A-R]{2}[0-9]{2}[A-X]{2}/i.test(locator))
      {
      //  lat+= (locator.charCodeAt(5)-65) /24; //char
     //   lon+= (locator.charCodeAt(4)-65)/12;//char
      }
      if(/[A-R]{2}[0-9]{2}[A-X]{2}[0-9]{2}/i.test(locator))
      {
      //  lat+= (locator.charCodeAt(7) -48) /(10*24); //number
      //  lon+= (locator.charCodeAt(6)-48)/(120); //number
      }
      if(/[A-R]{2}[0-9]{2}[A-X]{2}[0-9]{2}[A-X]{2}/i.test(locator))
      {
        var lat= (locator.charCodeAt(1)-65)*10 -90; //Char
        var lon= (locator.charCodeAt(0)-65) * 20 -180;//char
        lat+= (locator.charCodeAt(3) -48); //number
        lon+= (locator.charCodeAt(2)-48) * 2; //number
        
        lat+= (locator.charCodeAt(5)-65) /24; //char
        lon+= (locator.charCodeAt(4)-65)/12;//char

        lat+= (locator.charCodeAt(7) -48) /(10*24); //number
        lon+= (locator.charCodeAt(6)-48)/(120); //number
        
        lat+=  ((locator.charCodeAt(9)-65) + 0.5) / (10*24) / 24; //char
        lon+= ((locator.charCodeAt(8)-65) + 0.5) / 120 / 24;//char
      } 
      lat= parseInt(lat*100000)/100000;
      lon= parseInt(lon*100000)/100000;
      if ((/[.]/.test(lat)) && typeof (/\./.test(lon)))
      {
        document.getElementById("longitude").value=lon;
        document.getElementById("latitude").value=lat;
      }

	  }
	  function calcLocatorjs()
	  {
	    lon = document.getElementById("longitude").value;
	    lat = document.getElementById("latitude").value;
      lon = degmin2dec(lon);
      lat = degmin2dec(lat);
	    var locator = "";
			lon=parseFloat(lon);
			lat=parseFloat(lat);
			lat += 90;
			lon += 180;
			locator += String.fromCharCode(65 + Math.floor(lon / 20));
			locator += String.fromCharCode(65 + Math.floor(lat / 10));
			lon = lon % 20;
			if (lon < 0) lon += 20;
			lat = lat % 10;
			if (lat < 0) lat += 10;

			locator += String.fromCharCode(48 + Math.floor(lon / 2));
			locator += String.fromCharCode(48 + Math.floor(lat / 1));
			lon = lon % 2;
			if (lon < 0) lon += 2;
			lat = lat % 1;
			if (lat < 0) lat += 1;

			locator += String.fromCharCode(65 + Math.floor(lon * 12));
			locator += String.fromCharCode(65 + Math.floor(lat * 24));
			lon = lon % ( 1 / 12);
			if (lon < 0) lon +=  1 / 12;
			lat = lat % ( 1 / 24);
			if (lat < 0) lat += 1 / 24;

			locator += String.fromCharCode(48 + Math.floor(lon * 120));
			locator += String.fromCharCode(48 + Math.floor(lat * 240));
			lon = lon % (1 / 120);
			if (lon < 0) lon +=  1 / 120;
			lat = lat %( 1 / 240);
			if (lat < 0) lat += 1 / 240;

			locator += String.fromCharCode(65 + Math.floor(lon * 120 * 24));
			locator += String.fromCharCode(65 + Math.floor(lat * 240 * 24));
			lon = lon % ( 1 / 120 / 24);
			if (lon < 0) lon +=  1 / 120 / 24;
			lat = lat % (1 / 240 / 24);
			if (lat < 0) lat += 1 / 240 / 24;
      if(/[A-Z0-9]{10}/.test(locator))
      {
			  document.getElementById("locator").value=locator;
        locator_global = locator;
      }
	  }
    var storeDisabled= 0;
    function doStore() {
      if (('$newversion'!='0') && ('$newversion' != '$lastversion')) {
        alert("Cannot store attic version.\\n\\n"+
              "Please reload current version and repeat your change.");
        unchanged();
        return false;
      }
      if (isChanged) {
        document.main.func.value='store';
        document.main.ischanged.value=isChanged;
        unchanged();
        if (storeDisabled==0) {
          storeDisabled= 1;
          document.getElementById("subbut").disabled= 1;
          document.main.submit();
        }
      }
      else {
        checkAbort();
      }
    }
    function changeVersion(id,newversion) {
      if (isChanged) {
        if (!confirm('Data was changed.\\n\\nDrop your changes?')) {
          return;
        }
      }
      unchanged();
      self.location.href="?id="+id+"&newversion="+newversion;
    }
    function doDelete() {
      document.main.func.value='delete';
      document.main.confirm.value=$confirm;
      document.main.ischanged.value=isChanged;
      unchanged();
      document.main.submit();
    }
    function doCopy() {
      if (isChanged) {
        if (! confirm('This form contains unsaved data.\\n\\n'+
              'Take changes into the new copy?')) {
          return;
        }
      }
      document.main.func.value='copy';
      document.main.ischanged.value=1;
      unchanged();
      if (this.onCopy) {
        onCopy();
      }
      document.main.submit();
    }
    function doCopyAsNewest() {
      if (isChanged) {
        if (! confirm('This form contains unsaved data.\\n\\n'+
              'Take changes into the new copy?')) {
          return;
        }
      }
      document.main.func.value='asnewest';
      document.main.ischanged.value=1;
      unchanged();
      if (this.onCopy) {
        onCopy();
      }
      document.main.submit();
    }
  </script>
    <div id="infoPopup" class="vgrad"><!--<iframe  style="height:0; border:0; background-color:#fff; height:100%; " src="">You need Iframes to see this content!</iframe>-->
    <a style="text-decoration:none; font-size:35px; color:#666; position:absolute; right:5px; top:0px; font-weight:400;" href=javascript:hamnetdb.infopopHide();>x</a>
    </div>
  <!--<div id="ant_pop" width="575px" height="376px" style="position:absolute; top:200px; left:160px; visibility:hidden; z-index:999">
    <a style="text-decoration:none; font-size:35px; color:#666; position:absolute; right:5px; top:0px; font-weight:400;" href=javascript:hamnetdb.antennaHide();>Ã—</a>
    <iframe  style="height:0; border:0; background-color:#fff; height:100%; " src="">You need Iframes to see this content!</iframe>
  </div>-->
  <table cellspacing=0 cellpadding=4 border=0 width="100%"><tr>
  <td colspan=$tableCols $capcol><h3 class='nomargin'>$caption</h3></td></tr>
  );
}

sub afterForm {
  my $deleteBut= "";
  if ($id) {
    if ($copyButton) {
        $deleteBut.= qq(<button id="copybut" type="button" 
                        onclick="doCopy()">Copy</button>
                        &nbsp;&nbsp;&nbsp;);
      if ($isOldVersion) {
        $deleteBut.= qq(<button id="copyasnew" type="button" 
                        onclick="doCopyAsNewest()">Revert to this version
                        </button>
                        &nbsp;&nbsp;&nbsp;);
      }
      else {
        if ($deleteButton) {
          $deleteBut.= qq(<button id="delebut" type="button" 
                          onclick="doDelete()">Delete</button>
                          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                          &nbsp;&nbsp;&nbsp;&nbsp;);
        }
      }
    }
  }
  print qq(
  <tr><td colspan=$tableCols align="right">
    <table cellspacing=0 cellpadding=0 border=0 width="100%">
    <tr><td valign="center" align="left">
    $lastChanged</td><td align="right" valign="center">$br5
    $deleteBut
    <button id="subbut" type="button" 
            onclick="doStore()">Store</button>&nbsp;
    <button type="button" onclick="checkAbort()">Abort</button>
    </td></tr></table>
  </td></tr></table>

  <script language="JavaScript">
    if ($ischanged) {
      changed();
    }
    if ($isOldVersion) {
      document.getElementById("subbut").disabled= 1;
      if (document.getElementById("delebut")) {
        document.getElementById("delebut").disabled= 1;
      }
    }
  </script>
  </form>
  );
}

############################################################################
# Einen veränderten Eintrag abspeichern
sub storeEntry {
  my $setCommand= &checkValues;

  unless ($setCommand || $inputStatus) {
    $inputStatus= "ERROR: No values to store";
  }
  # Cross-Site-Request-Forgery-Attacke verhindern:
  unless ($sessionToken eq $formToken) {
    $inputStatus= "ERROR: Invalid session token, please retry";
  }
  unless ($inputStatus) {
    # Es ist alles ok, also in Datenbank schreiben
    my $where= "where $idField='$id'";
    my $sth=   $db->prepare("select $idField from $table $where");
    my $found= 0;
    my $setCommand= "editor='$username', ".
                    "version=version+1, $changedField=NOW(), ".$setCommand;

    if ($sth->execute()) {
      if (@line= $sth->fetchrow_array) {
        $found= 1;
        if ($beforeUpdateDo) {
          foreach $tmpsql (split(/;/, $beforeUpdateDo)) {
            unless ($inputStatus) {
              unless ($db->do($tmpsql)) {
                $inputStatus= "ERROR: beforeUpdate: $tmpsql";
              }
            }
          }
        }
        unless ($inputStatus) {
                  #todo
          ####check if site-type  has callsign
          #check if callsign has changed (id als reference), ev vorher kein callsign...
          #host-names search for old callsign replace with new
          
          #hamnet_coverage callsign, coveravge neu berechnen
          #hamnet_edge left_site, right_site
          #hamnet_host site, name(  xxx.callsign)
          if($table eq "hamnet_site"){
            my $sth1= $db->prepare("select callsign from hamnet_site ".
                              "where $idField='$id'");
            $sth1->execute();
            @line= $sth1->fetchrow_array;
            if ($line[0] ne $callsign) #if callsign changed
            {
              updateCallsign($line[0],$callsign);
              my $newcall=$callsign;
              my $oldcall=$line[0];



            }
          
          }
          unless ($db->do("update $table set $setCommand $where")) {
            $inputStatus= "ERROR: DB-Update failed";
          }
          unless ($inputStatus) {
            if ($table_history) {
              $db->do("insert $table_history select * ".
                             "from $table where $idField='$id'");
            }
          }
        }
      }
    }
    unless ($found) {
      if ($beforeInsertDo) {
        unless ($db->do($beforeInsertDo)) {
          $inputStatus= "ERROR: beforeInsert: $beforeInsertDo";
        }
      }
      unless ($inputStatus) {
        $setCommand.= ",$idField=$id" if $id;
        if ($id) {
          $inputStatus= "ERROR: Object not found in database";
          return;
        }
        elsif ($db->do("insert $table set $setCommand")) {
    
          if ($table_history) {
            $db->do("insert $table_history select * ".
                    "from $table order by $idField desc limit 0,1");
          }
          $found= 1;
        }
      }
    }
    unless ($inputStatus) {
      if ($found) {
        #Add antenna configuration to hamnet_coverage
        if($table eq "hamnet_site"){
          unless($inputStatus){
            addAccess();
          }
        }
      
        print("Status: 302\n");
        print("Location: ?func=close&id=$id\n\n");

        exit;
      }
      $inputStatus= "ERROR: Cannot write to database";
    }
  }
}

############################################################################
# Einen Eintrag löschen
sub deleteEntry {
  if ($confirm) {

    unless($db->do("update $table set ".
      "deleted=1,version=version+1,$changedField=NOW(),editor='$username' ".
      "where $idField='$id'")) 
    {
      $inputStatus= "ERROR: Cannot write delete flag";
    }
    else {
      if ($table_history) {
        $db->do("insert $table_history select * ".
                       "from $table where $idField='$id'");
      }
      unless ($keepDeleted) {
        unless ($db->do("delete from $table where $idField='$id'")) {
          $inputStatus= "ERROR: Cannot delete in database";
        }
        unless ($inputStatus) {
          if ($afterDeleteDo) {
            unless ($db->do($afterDeleteDo)) {
              $inputStatus= "ERROR: AfterDelete: $afterDeleteDo";
            }
          }
        }
      }
      if($table eq "hamnet_site"){
        unless($inputStatus){
          deleteAccess();
        }
      }
      unless ($inputStatus) {
        print("Status: 302\n");
        print("Location: ?func=close\n\n");
        exit;
      }
    }
  }
  else {
    $inputStatus= "Press delete button again to delete object";
    $confirm= 1;
  }
}

############################################################################
# Variablen aus dem Formular oder ggf. aus der Datenbank laden
sub loadFormData {
  my $attributes= shift;
  my @ret= ();

  if ($mustLoadFromDB) {
    my $sqlFrom= "from $table where";
    if ($table_history && $newversion && $id) {
      $sqlFrom= "from $table_history ".
                "where version='$newversion' and";
    }
    my $sth= $db->prepare(
        "select $attributes $sqlFrom $idField='$id'");

    if ($sth->execute) {
      unless (@ret= $sth->fetchrow_array) {
        $inputStatus= "ERROR: Element not found in database";
      }
    }
    else {
      $inputStatus= "DB-ERROR: $DBI::errstr";
    }
  }
  else {
    my @attnames= split(/ *, */, $attributes);
    foreach $name (@attnames) {
      push(@ret, $query->param($name).""); # undef-Werte vermeiden
    }
  }
  return @ret;
}


1;