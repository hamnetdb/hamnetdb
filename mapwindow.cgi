#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Show map as popup window
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

# Map may be limited to parts of the network
$as= $query->param("as")+0;
$site= $query->param("site")."";
$site=~s/[^a-z0-9\-_]//gi; 
$country= lc $query->param("country")."";
$country=~s/[^a-z]//gi; 

# Create the list of ping agents
my $agents;
foreach $agent (sort @fpingAgents) {
  $agents.= ", " if $agents;
  $agents.= "<a class='ovinfo' href='index.cgi?q=$agent'>$agent</a>";
}
# Embed javascript part into page
my $js;
if (open(JS,"<mapwindow.js")) {
  $js= join("", <JS>);
  close(JS);
  $js=~s/\/\/.*$//mg;     # remove single line content
  $js=~s/^\s+//mg;        # remove leading whitespaces
  $js=~s/\/\*.*?\*\///gs; # remove comment
}

print qq(Content-Type: text/html\n\n
<!DOCTYPE html>
<html><head>      
  <title>Map - Hamnet IP-Database</title>
  <script language="JavaScript" src="jquery.js"></script>
  $htmlRel
  <script language='JavaScript'>
  $js
  </script>
  <style>
  #map_canvas {
    position: absolute;
    top: 0px;
    left: 0px;
    right: 0px;
    bottom: 0px;
  }
  #map_control {
    position: fixed;
    top: 50px;
  }
  </style>
</head><body>
  <script for="document" event="onmousemove()" 
                         language="JScript" type="text/jscript"> 
     { hamnetdb.info.move(window.event); }
  </script>
  <div id="infoPopup" class="vgrad"></div>
  <script src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>
  <div id='map_canvas'></div>
  <div id="map_control" class="vgrad" 
       onmouseover="mapwindow.panelOver()"
       onmouseout="mapwindow.panelOut()">
  <div style="margin-bottom: 5px;">
  <b>Hamnet-DB Control</b>
  </div>
  <form name="mapcont">
  &nbsp;Fit map position to AS:<br>
);
&asCombo(0, 1, 0, $only_as, "onchange='mapwindow.panelChange();'");
print qq(
  <div></div>
  <input type="checkbox" value="1" id="_onlyHamnet" name="onlyHamnet" 
  onclick='mapwindow.panelChange();'><label for="_onlyHamnet">
  Suppress sites without hamnet
  </label>
  <br>
  <input type="checkbox" value="1" id="_noTunnel" name="noTunnel" 
  onclick='mapwindow.panelChange();'><label for="_noTunnel">
  Suppress tunnel connections
  </label>
  <br>
  <input type="checkbox" value="1" id="_showLegend" name="showLegend" 
  onclick='mapwindow.legendChange();'><label for="_showLegend">
  Show symbol legend 
  </label>
  </form>
  </div>
  <script
    src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>
  <script>
    mapwindow.shallShow= true;
    mapwindow.scrollwheel= true;
    mapwindow.as= $as;
    mapwindow.site= "$site";
    mapwindow.country= "$country";
  </script>
  <div class="vgrad" id="map_legend">
    <h4>Legend</h4>
    <img align="absmiddle" src="site.png">
    This is a site. 
    No realtime checks were performed last 2 hours.
    <br>
    <img align="absmiddle" src="site-user.png">
    This site has user-access radio parameters configured.
    <br>
    <img align="absmiddle" src="site-green.png">
    At least one host of this site has answered to ping 
    last 2 hours.
    <br>
    <img align="absmiddle" src="site-red.png">
    No ping answer last 2 hours at $agents.
    <br>
    <img align="absmiddle" src="site-grey.png">
    Site is documented to have no hamnet on site.
  </div>
</body></html>
);
