#!/usr/bin/perl -w
# ---------------------------------------------------------------
# Hamnet IP database - antenna-diagram
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


use CGI;
$query=  new CGI;

do "config.cgi";

do "lib.cgi";

my $antenna = $query->param("name");
my $func = $query->param("func");

my $old= $query->param("old")+0;

my $line = 'leer';

if($old==1){
  $sth = $db->prepare("select file from hamnet_antennafiles_hist where name='$antenna'");
}
else{
  $sth = $db->prepare("select file from hamnet_antennafiles where name='$antenna'");
}
$sth->execute();

$line =$sth->fetchrow_array();


if($func eq "download")
{
  print("Content-Type:application/x-download\n");
  print("Content-Disposition: attachment; filename=$antenna.ant\n\n");
  print($line);
} 
else
{
  
  my ($js_azimuth_ant, $js_elevation_ant);
  $js_azimuth_ant .= $line ;
  $js_azimuth_ant =~ s/\n/,/g;
  
print qq(Content-Type: text/html\nExpires: 0\n\n<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        margin: 10px;
        padding: 0px;
        font-family: arial,helvetica,sans-serif;
        font-size:15px;
      }
      h3 {
        /*color: #407040;*/
        font-size:20px;
      }
      
      #elevation_gain {
        position:absolute;
        left:300px;
      }
    </style>
  </head>
  <body>
   <h3>Antenna: $antenna</h3>
    <canvas id="azimuth_gain" width="270" height="270"></canvas>
    <canvas id="elevation_gain" width="270" height="270"></canvas>
    <br>
    Download: <a href="?old=$old&name=$antenna&func=download">$antenna.ant</a>
    <script src="chart.js"></script>
    <script>
      var antenna = [$js_azimuth_ant];
      var canvas_azimuth = document.getElementById('azimuth_gain');
      var canvas_elevation = document.getElementById('elevation_gain');
      var ant_azimuth = canvas_azimuth.getContext('2d'); 
      var ant_elevation = canvas_elevation.getContext('2d'); 

      var center_x = 135;
      var center_y = 145;
      var radius = 100;
      var factor= 1;
      ant_azimuth.lineWidth = 2;
      ant_azimuth.strokeStyle='#a0a0a0';
      //outer circle
      ant_azimuth.arc(center_x, center_y, radius, 0, 2 * Math.PI, false);
      //lines though circle
      ant_azimuth.lineWidth = 0.7
      ant_azimuth.strokeStyle='#c0c0c0';
      
      var minimum = Math.min.apply(Math, antenna);
      minimum = Math.abs(minimum);
      var scale = 1/minimum;
      //dB scale
      for(var i=1;i<(minimum/10>>0);i++)
      {
        var scale_radius = (1 - scale * i *10)*radius;
        ant_azimuth.arc(center_x, center_y, scale_radius, 0, 2 * Math.PI, false);
      }  
      //for degree scale
      for(var i=0;i<36;i++)
      {
        ant_azimuth.moveTo(center_x,center_y);
        ant_azimuth.lineTo((radius*Math.cos((i*10-90)*Math.PI/180)) + center_x,(radius*Math.sin((i*10-90)*Math.PI/180)) +center_y,1,1);
      }
      
      ant_azimuth.stroke();
      ant_azimuth.beginPath();
      
      ant_azimuth.font = 'bold 16px Sans-Serif';
      ant_azimuth.fillText('Azimuth Gain', 75, 15);
      ant_azimuth.fillStyle = '#000';
      ant_azimuth.font = '14px Sans-Serif';
      ant_azimuth.textBaseline = 'Top';
      ant_azimuth.fillText('0°', 130, 40);
      ant_azimuth.fillText('90°', 240, 150);
      ant_azimuth.fillText('180°', 120, 260);
      ant_azimuth.fillText('270°', 0, 150);
      
      ant_azimuth.fillStyle = '#f5f5f5';
      ant_azimuth.font = '11px Sans-Serif';
      ant_azimuth.fillText('by Hamnetdb', 190, 260);

      ant_azimuth.lineWidth = 1;
      ant_azimuth.strokeStyle='#ff0000';

      //startpoint of diagram   
      ant_azimuth.moveTo(center_x,center_y-(1- scale *Math.abs(antenna[0]))*radius);
      for( var i=0; i <360; i++)
      {
        factor=1- scale * Math.abs(antenna[i]); //some simple math

        ant_azimuth.lineTo((radius*Math.cos((i-90)*Math.PI/180))*factor + center_x,(radius*Math.sin((i-90)*Math.PI/180))*factor +center_y,1,1);
      
      }
      //endpoint of diagram
      ant_azimuth.lineTo(center_x,center_y-(1- scale *Math.abs(antenna[0]))*radius);
      ant_azimuth.stroke();

 //////////////////////////////////////////////////////////////////////////////////////////////////////   
    
      ant_elevation.lineWidth = 2;
      ant_elevation.strokeStyle='#a0a0a0';
      //outer circle
      ant_elevation.arc(center_x, center_y, radius, 0, 2 * Math.PI, false);
      //lines though circle
      ant_elevation.lineWidth = 0.7
      ant_elevation.strokeStyle='#c0c0c0';
      
      //dB scale
      for(var i=1;i<(minimum/10>>0);i++)
      {
        var scale_radius = (1 - scale * i *10)*radius;
        ant_elevation.arc(center_x, center_y, scale_radius, 0, 2 * Math.PI, false);
      }  
      //for degree scale
      for(var i=0;i<36;i++)
      {
        ant_elevation.moveTo(center_x,center_y);
        ant_elevation.lineTo((radius*Math.cos((i*10-90)*Math.PI/180)) + center_x,(radius*Math.sin((i*10-90)*Math.PI/180)) +center_y,1,1);
      }
      
      ant_elevation.stroke();
      ant_elevation.beginPath();
      
      ant_elevation.font = 'bold 16px Sans-Serif';
      ant_elevation.fillText('Elevation Gain', 75, 15);
      ant_elevation.fillStyle = '#000';
      ant_elevation.font = '14px Sans-Serif';
      ant_elevation.textBaseline = 'Top';
      ant_elevation.fillText('90°', 127, 40);
      ant_elevation.fillText('0°', 240, 150);
      ant_elevation.fillText('-90°', 122, 260);
      ant_elevation.fillText('180°', 0, 150);

      ant_elevation.fillStyle = '#f5f5f5';
      ant_elevation.font = '11px Sans-Serif';
      ant_elevation.fillText('by Hamnetdb', 190, 260);

      ant_elevation.lineWidth = 1;
      ant_elevation.strokeStyle='#ff0000';

      //startpoint of diagram   
      ant_elevation.moveTo(center_x,center_y+(1- scale *Math.abs(antenna[360]))*radius);
      for( var i=0; i<360; i++)
      {
        factor=1- scale * Math.abs(antenna[i+360]); 
        ant_elevation.lineTo((radius*Math.cos((i-90)*Math.PI/180))*factor + center_x,((-1)*radius*Math.sin((i-90)*Math.PI/180))*factor +center_y,1,1);
       
      }
      //endpoint of diagram
      ant_elevation.lineTo(center_x,center_y+(1- scale *Math.abs(antenna[360]))*radius);
      ant_elevation.stroke();
    
    </script>
  </body>
</html> 
);

}
