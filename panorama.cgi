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
push @INC,'.';

print("Content-Type: text/html\nExpires: 0\n\n");

$host_calc_profile= "rftools/";
#unless ($profile_path_program) {
#  $host_calc_profile="https://hamnetdb.net/rftools/";
#}

print qq(<!DOCTYPE html>
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
    <script src="osm/hamnetdb-lf.js"></script>

    <script type="text/javascript">
      var host_calc_profile="$host_calc_profile";
      window.onresize = panoramaResize(); //function(event) {};
      var panoramaBigX = 650;
      var panoramaBigY = 350;
      var own_lat;
      var own_lon;
      var channel;
      var windowID = Math.random();
    </script>

    <title>HamnetDB Panorama</title>
	 <link rel="stylesheet" type="text/css" href="osm/style-lf.css" />
  </head>
  <body style="overflow-x: auto; min-width: 580px;" onresize="panoramaResize();" onload="panoramaBigInit();">
    <div id="panoarama-big-content">
    <div id='panorama-loading' style=""><img src='hdb.gif'
          alt='loading...'/>calculating...</div>
    <div id='panorama-img-parent'><img id='panorama-img' src='' onmouseover='javascript:panoramaProcessMetadata(event);' onmousemove='javascript:panoramaProcessMetadata(event);'  ondblclick='javascript:panoramaProcessMetadata(event);' onclick='javascript:panoramaProcessMetadata(event);'/></div>
      <span id="panorama-top" class='pan-important'>&nbsp;resize window or enter custom image size and press "recalculate", settings in map-window!</span><br>
      
      <div id='panorama-big-in'><form id='panorama'>&nbsp;&nbsp;
        <span id='panorama-updated'><label>custom size</label><input type="checkbox" name="pan-custom" id="pan-custom" onchange="javascript:panoramaBigChg();">&nbsp;&nbsp;<label for="pan-x-custom">width</label><input type="text" name="pan-x-custom" id="pan-x-custom" value="600" disabled>
        <label for="pan-y-custom">height</label><input type="text" name="pan-y-custom" id="pan-y-custom" value="400" disabled><input type='button' value='recalculate' onclick='javascript:panoramaBig();' ></span>
      </form>&nbsp;<span id='panorama-meta-big'></span><span id='panorama-error'></span> 
    </div>
    </div>
  </body>
</html>);


