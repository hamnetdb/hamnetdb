#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - OSM map display
#
# Lucas Speckbacher, OE2LSP
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#

do "lib.cgi" or die;

sub cleanLibs {
  my ($pathl) = @_;
  if (open(JS,"< " . $pathl)) {
    $js= join("", <JS>);
    close(JS);
    $js=~s/^\s+//mg;        # remove leading whitespaces
    $js=~s/^\/\/.*$//mg;    # remove single line content
    $js=~s/\/\*.*?\*\///gs; # remove comment
    print($js);
  }
  else {
    die;
  } 

}

print("Content-Type: text/html\nExpires: 0\n\n");


my $source= lc $query->param("source");
if ($source eq "" && $ARGV[0]) {
  $source= lc $ARGV[0];
}
$source+= 0;
if ($source == 0) {
  $source = 1;
}

my $hover= lc $query->param("hover");
if($hover eq "true") {
  $hoverchecked = "checked";
} 

$sourceselect[$source] = 'selected="selected"'; 
# Embed javascript part into page




print qq(
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
  <head>
     <link rel="shortcut icon" href="img/favicon.ico" type="image/x-icon" />
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <meta http-equiv="cache-control" content="max-age=0" />
     <meta http-equiv="cache-control" content="no-cache" />
     <meta http-equiv="expires" content="0" />  
     <meta http-equiv="Pragma" content="no-cache">

     <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
     <meta http-equiv="content-language" content="en" />
	  <title>HamnetDB Map</title>
	  <link rel="stylesheet" type="text/css" href="osm/leaflet.css" />
	  <link rel="stylesheet" type="text/css" href="osm/style-lf.css" />
    <script src="osm/leaflet.js"></script>
    
    <!--<script src="osm/GeoJSON.Style.js"></script>
    <script src="osm/GeoJSON.Ajax.js"></script>
    <script src="osm/Control.Layers.argsGeoJSON.js"></script>-->
      
);

#print('<script type="text/javascript">');
#cleanLibs('osm/leaflet.js');
#cleanLibs('osm/L.GeoJSON.js');
#cleanLibs('osm/L.ajax.js');
#cleanLibs('osm/L.promise.js');
#cleanLibs('osm/hamnetdb-lf.js');
#cleanLibs('osm/L.Control.MousePosition.js');
#cleanLibs('osm/L.Control.MiniMap.js');
#cleanLibs('osm/L.Control.Sidebar.js');
#cleanLibs('osm/L.Permalink.js');
#cleanLibs('osm/L.Permalink.Layer.js');
#cleanLibs('osm/L.Permalink.Overlay.js');
#cleanLibs('osm/L.Control.LSP.js');
#print('</script>');

if ($source eq 1) {
  print('<script src="osm/es6-promise.auto.js"></script><script>ES6Promise.polyfill();</script>');
  print('<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyA58LI1avl5xzd8mj9LLidnBVhRHGoaAsA" async defer></script> <script src="osm/Leaflet.GoogleMutant.js"></script>');
#  print('<script src="http://maps.google.com/maps/api/js?v=3&sensor=false"></script> <script src="osm/L.Google.js"></script>');
}
print qq(
     <script type="text/javascript" src="osm/leaflet.ajax.js"></script>
    <!--<script src="osm/spin.js"></script>
    <script src="osm/leaflet.spin.js"></script>-->

      
    <script src="osm/L.Control.MousePosition.js"></script>
    <script src="osm/L.Control.MiniMap.js"></script>
	  <script src="osm/L.Control.Sidebar.js"></script>
    <script src="osm/Permalink.js"></script>
    <script src="osm/Permalink.Marker.js"></script>
    <script src="osm/Permalink.Layer.js"></script>
    <script src="osm/Permalink.Overlay.js"></script>
	  <script src="osm/L.Control.LSP.js"></script>
    <script src="osm/hamnetdb-lf.js"></script>
	 
	</head>
	<body onload="init()">
      <div id="info" style="display:none;">
      <div id="sidebar-info" >
	    <div id="legende">
          <h4>Legend</h4>
          <table>        
            <tr><td><img src="site.png"/></td><td>This is a site. No realtime checks were performed last 2 hours.</td></tr>
            <tr><td><img src="site-user.png"/></td><td>This site has user-access radio parameters configured.</td></tr>
            <tr><td><img src="site-green.png"/></td><td>At least one host of this site has answered to ping last 2 hours.</td></tr>
            <tr><td><img src="site-red.png"/></td><td>No ping answer last 2 hours at 
                <a class="ovinfo" href="index.cgi?q=db0fhn">db0fhn</a>,
                <a class="ovinfo" href="index.cgi?q=db0zm">db0zm</a>,
                <a class="ovinfo" href="index.cgi?q=ir3dv">ir3dv</a>.</td></tr>
            <tr><td><img src="site-grey.png"/></td><td>Site is documented to have no hamnet on site. </td></tr>
          </table>
          <br><br>
          <h4> Coverage </h4>
	        <table>
	        	<tr> <td>The receive signal power is based on a 16dBi, 60km maximum radius</td></tr>
            <tr> <td> Green: Received power level better than -70 dBm.</td></tr> 
	        	<tr> <td> Cyan: Received power level better than -75 dBm.</td></tr> 
	        	<tr> <td> Dark Blue: Received power level better than -81 dBm.</td></tr>   
	        	<tr> <td> Purple: Received power level better than -89 dBm.</td></tr>
	        </table>
        </div>
        <div id="info_by">HamnetDB by DL8MBT <br />Map by OE2LSP</div>
      </div>
      <div id="sidebar-setting">
	    <h4>Map-Settings</h4>
        <div id="source">
          <form name="mapsourceform">
            <label for="mapsource">Map-Source</label> 
            <select id="mapsource" name="mapsource" class="mapform" onchange="mapSource();">
              <option $sourceselect[1] class="mapform" value="1">OSM+Googlemaps</option>
              <option $sourceselect[2] class="mapform" value="2">OSM</option>
              <option $sourceselect[3] class="mapform" value="3">OSM Hamnet</option>
            </select>
          </form>
          </div>
        <div id="popupsetting">
          <form><input type="checkbox" id="hoverpopup" onchange="popupSetting();" $hoverchecked value="hoverpopup"/>Popup on Mouse over</form>
        </div>
        <div id="only_as"><form><label for="as">Fit map position to AS:</label>   
);
            &asCombo(0, 1, 0, $only_as, "onchange='panelChange();'");

print qq(          
        </form></div>
        <div id="extern-permalink"></div>
      </div>
      </div>
      <div id="map">

      </div>
      <div class="hidden">
        <img src="site-user-red.png" />
        <img src="site-user-grey.png" />
        <img src="site-user-green.png" />
        <img src="site-user.png" />
        <img src="site-red.png" />
        <img src="site-grey.png" />
        <img src="site-green.png" />
        <img src="site.png" />
      </div>
	  <noscript><h1>Für diese Webseite benötigst du Javascript!</h1></noscript>
	</body>
</html>         
);
