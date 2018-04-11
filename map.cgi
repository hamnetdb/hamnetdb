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


$host_calc_profile= "";
unless ($profile_path_program) {
  $host_calc_profile="https://hamnetdb.net/";
}
$host_calc_visibility= "";
unless ($visibility_path_program) {
  $host_calc_visibility="https://hamnetdb.net/rftools/";
}

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
	  <script src="osm/L.Draw.js"></script>
    <script src="osm/Permalink.js"></script>
    <script src="osm/Permalink.Marker.js"></script>
    <script src="osm/Permalink.Layer.js"></script>
    <script src="osm/Permalink.Overlay.js"></script>
	  <script src="osm/L.Control.LSP.js"></script>
    
    <script src="osm/leaflet.contextmenu.js"></script>
    <!--<script src="osm/leaflet.contextmenu.min.js"></script>-->

    <script type="text/javascript">var host_calc_profile="$host_calc_profile";</script>
    <script type="text/javascript">var host_calc_visibility="$host_calc_visibility";</script> 

    <script src="osm/hamnetdb-lf.js"></script>


	 
	</head>
	<body onload="init()">
      <div class="hidden">
        Hamnet map, showing Hamnet infrastructure 
        also including  RF planing tools
        <br><br>
        <img src="site-user-red.png" />
        <img src="site-user-grey.png" />
        <img src="site-user-blue.png" />
        <img src="site-user-green.png" />
        <img src="site-user.png" />
        <img src="site-red.png" />
        <img src="site-grey.png" />
        <img src="site-blue.png" />
        <img src="site-green.png" />
        <img src="site.png" />
      </div>
      <div id="info" style="display:none;">
      <div id="sidebar-info">
	      <div id="legende">
          <h4>Legend</h4>
          <table>        
            <tr><td><img src="site.png"/></td><td>This is a site. No realtime checks were performed last 2 hours.</td></tr>
            <tr><td><img src="site-user.png"/></td><td>This site has user-access radio parameters configured.</td></tr>
            <tr><td><img src="site-green.png"/></td><td>At least one host of this site has answered to ping last 2 hours.</td></tr>
            <tr><td><img src="site-blue.png"/></td><td>Same as green, site also connected to the hamcloud.</td></tr>
            <tr><td><img src="site-red.png"/></td><td>No ping answer last 2 hours at hamcloud</td></tr>
            <tr><td><img src="site-grey.png"/></td><td>Site is documented to have no hamnet on site. </td></tr>
          </table>
          <h4> Monitoring </h4>
          <table>
            <tr><td bgcolor="#5dff00">&nbsp;</td><td>>=-65dBm<td></td></tr>
            <tr><td bgcolor="#a2ff00">&nbsp;</td><td>>=-70dBm<td></td></tr>
            <tr><td bgcolor="#f1ff00">&nbsp;</td><td>>=-75dBm<td></td></tr>
            <tr><td bgcolor="#ffde00">&nbsp;</td><td>>=-80dBm<td></td></tr>
            <tr><td bgcolor="#ffa700">&nbsp;</td><td>>=-85dBm<td></td></tr>
            <tr><td bgcolor="#ff000d">&nbsp;</td><td><=-86dBm<td></td></tr>        
          </table>
          <h4> Coverage </h4>
          The receive signal power is based on a 16dBi, 60km maximum radius
	        <table>
            <tr><td bgcolor="#59ed59">&nbsp;</td><td>Received power level better than -65 dBm.</td></tr> 
	        	<tr><td bgcolor="#59dbd9">&nbsp;</td><td>Received power level better than -70 dBm.</td></tr> 
	        	<tr><td bgcolor="#81a9ff">&nbsp;</td><td>Received power level better than -75 dBm.</td></tr>   
	        	<tr><td bgcolor="#a759ff">&nbsp;</td><td>Received power level better than -80 dBm.</td></tr>
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
      <div id="sidebar-rftools">
        <h3>RF-Tools</h3>
        An easy way to estimate <br> possilbe RF-links
        <br><br>
        <h4>Link-profile:</h4>
        <a onclick="rfPlacemarker();" style="text-decoration:none; border-radius:2px;">
          <span class="side-button side-draw-point" id="side-draw-add-point1"></span></a>
        <a onclick="deleteProfileAll();" style="text-decoration:none; border-radius:2px;">
          <span class="side-button side-draw-del" id="side-draw-del-point1"></span></a>
        &nbsp;place marker "From" and "To"<br>
        
        <input type='button' value='show profile' style='height:24px;' onclick='javascript:rfOpenprofile()'> 
        <br><br>
        <h4>(RF)-visibility:</h4>
        use exsisting visibility (faster)<br>
        );

        
print qq(
        <select id="rfPreset" onchange='rfGetPreset();' style="width:200px;">
          <option selected="selected" value="0">&nbsp;</option>
          <option value="1">not loaded</option>
        </select> 
        <hr>
        <div id="rfCalcNew">
          or calculate new visibility<br>
          <form>Label: <input type="text" id="rfLabel" style='width:120px' onchange='rfValUpd()'><br>
          <a onclick="rfPlacemarker();" style="text-decoration:none; border-radius:2px;">
            <span class="side-button side-draw-point" id="side-draw-add-point2"></span></a>
          <a onclick="deleteProfileAll();" style="text-decoration:none; border-radius:2px;">
            <span class="side-button side-draw-del" id="side-draw-del-point2"></span></a>  
          &nbsp;place at least one marker <br>

          <a onclick="rfRectangle();" style="text-decoration:none; border-radius:2px;">
            <span class="side-button side-draw-rect" id="side-draw-add-rect"></span></a>
          <a onclick="rfDelRectangle();" style="text-decoration:none; border-radius:2px;">
          <span class="side-button side-draw-del" id="side-draw-del-rect"></span></a>
          &nbsp;place rectangular constrain to speedup calculation (red frame)<br>
          <span id="rfTowerFromLine">Tower size "From" (m) <input type="text" id='rfTowerFrom' value='10' onchange='rfValUpd()' style='width:20px'><br></span>
          <span id="rfTowerToLine">Tower size "To" (m) <input type="text" id='rfTowerTo' value='10' onchange='rfValUpd()' style='width:20px'><br></span>
          Tower size visibility (m) <input type="text" id='rfTowerRx' value='1' onchange='rfValUpd()' style='width:20px'><br>
          
             use
             <select id="rfRefraction" onchange='rfValUpd();'>
              <option value="0" >optical visibility</option>
              <option value="0.25" selected="selected">RF-visibility</option>
            </select> (refraction)
          </form>
          <input type='button' value='calculate visibility' style='height:24px; width:' onclick='javascript:rfCalc()'>
          <br>
        </div>
        <div id="rf-loading"><img src="hdb.gif" width="150px" style="opacity: 0.6;"><br>
        loading...<br></div>
        <div id="rf-result"></div>
        <br>
        <div id="extern-permalink-rf"></div>
        <h4>hints:</h4>
        <ul><li>right click to site "snap to &lt;SITE&gt;" to use coordinates and tower size</li>
        <li>detailed documentation can be found <a href="index.cgi?m=help#rftools">here</a></li>
        </ul>

      </div>
      </div>
      
      <div id="map">

      </div>
	  <noscript><h1>Für diese Webseite benötigst du Javascript!</h1></noscript>
	</body>
</html>         
);
