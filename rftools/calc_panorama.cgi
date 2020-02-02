#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Calculate topo-profile
#
# Lucas Speckbacher, OE2LSP
# Christian Rabler, OE5DXL (rf-visibility)
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
use lib qw(.);
use Scalar::Util qw(looks_like_number);
use List::Util qw( min max );
use Digest::MD5 qw(md5 md5_hex md5_base64);
do "../lib.cgi" or die;

my $refer = $ENV{HTTP_REFERER};
my $lat_a= $query->param("lat_a")+0; #breitengrad (bauch)
my $lon_a= $query->param("lon_a")+0; #laengengrad
my $antenna_a= $query->param("ant_a")+0;
my $lat_b= $query->param("lat_b")+0;
my $lon_b= $query->param("lon_b")+0;
my $refraction= $query->param("ref")+0;
my $poi= $query->param("poi");
my $size_x= $query->param("x")+0; #image-size
my $size_y= $query->param("y")+0;
my $zoom= $query->param("z")+0;
my $font_size= $query->param("font")+0;
my $elevation= $query->param("el")+0;
my $angle= $query->param("angle")+0;
my $waves= $query->param("waves")+0;
my $snow1= $query->param("snow1")+0;
my $snow2= $query->param("snow2")+0;
my $sun_az= $query->param("sun_az")+0;
my $sun_el= $query->param("sun_el")+0;
my $desert= $query->param("desert")+0;

#print("Content-Type: text/html\nExpires: 0\n\n");

#use paths from config.cgi
$path_prog= $panorama_path_program;
$path_srtm= $panorama_path_srtm;
$path_errlog= $panorama_path_errorlog;
$path_web= $panorama_path_web;

  #min 
  $refraction= 0 if $refraction<0;
  $antenna_a= 0  if $antenna_a<0;
  $size_x= 100 if $size_x<100;
  $size_y= 100 if $size_y<100;
  $font_size= 0 if $font_size<0;
  $elevation= -90 if $font_size<-90;
  $angle= 1 if $angle<1;
  $zoom= 1 if $zoom < 0.1;
  $sun_az= 0 if $sun_az < 0;
  $sun_el= -2 if $sun_el < -2;

  #max
  $refraction= 1 if $refraction>1;
  $antenna_a= 3000  if $antenna_b>3000;
  $size_x= 6000 if $size_x>6000;
  $size_y= 2160 if $size_y>2160;
  $font_size= 3 if $font_size>3;
  $elevation= 90 if $font_size>90;
  $angle= 360 if $angle>360;
  $zoom= 10 if $zoom>10;
  $sun_az= 360 if $sun_az > 360;
  $sun_el= 90 if $sun_el > 90;

  if ($font_size > 0) 
  {
    $font_cmd= "-F $font_size";
  } 
  else 
  {
    $font_cmd= "";
  }	  

  #generate poi parameter
  $poi_param= "";
  if ($poi=~/hamnet/) 
  {
    $poi_param.= "-J h -I $path_web/rftools/mk_w.png $path_web/rftools/mk_w.png -P 255 0 0 240 $path_web/rftools/hamnet.txt "; 
  }
  if ($poi=~/sota/)
  {  
    $poi_param.= "-J sota -I $path_web/rftools/mks_w.png $path_web/rftools/mks_w.png -P 0 255 0 250 $path_web/rftools/sota.txt ";
  }
  if ($poi=~/wc/) 
  {
    $poi_param.= "-J wc -I $path_web/rftools/mk_cam.png $path_web/rftools/mk_cam.png -P 255 255 255 200 $path_web/rftools/fotowebcam.txt ";
  }
  if ($poi=~/fone/) 
  {
    $poi_param.= "-J f -I $path_web/rftools/mk_w.png $path_web/rftools/mk_w.png -P 0 255 0 100 $path_web/rftools/fone2019.txt ";
  }
  if ($poi=~/mt/) 
  {
    $poi_param.= "-J MT -I $path_web/rftools/mkss_w.png $path_web/rftools/mkss_w.png -P 100 100 100 200 $path_web/rftools/alps.txt ";
    $poi_param.= "-J MT -I $path_web/rftools/mkss_w.png $path_web/rftools/mkss_w.png -P 100 100 100 200 $path_web/rftools/MT.txt ";
  }
  if ($poi=~/small/)
  {  
    $poi_param.= "-J s -I $path_web/rftools/mkxs_w.png $path_web/rftools/mkxs_w.png -P 60 60 60 100 $path_web/rftools/AT.txt ";
  }
  $sun_param= "";
  if ($sun_az > 0 && $sun_el > 0)
  {
    $sun_param= "-S $sun_az $sun_el";
  }
  else #todo 90degree to camera
  {
    $sun_param= "-S 180 15";
  }
  $snow_param= "";
  if ($snow1 > 0 && $snow2 > 0)
  {
    $snow_param= "-G $snow1 $snow2";
  }
  $desert_param= "";
  if ($desert > 0)
  {
    $desert_param= "-t 1 0 -u ";
  }
  else
  {
    $desert_param= "-W 0.7 2 0 ";
  }

  my $cmd= "nice -n 9 $path_prog -p $path_srtm -A $antenna_a ";
  $cmd.= "-a $lat_a $lon_a -b $lat_b $lon_b -z $zoom ";
  $cmd.= "-e $elevation $font_cmd -g 2.3 -o 5 -C 3 ";
  $cmd.= "-x $size_x -y $size_y -w $angle $poi_param ";
  $cmd.= "-r $refraction $sun_param $desert_param $snow_param ";
  
  #high contrast -l 1.0 0.0 


  $pan_hash= md5_hex($cmd);

  #if file $pan_hash exists dont calc
  $output_file= "$path_web/rftools/panorama/$pan_hash";
  if (-e "$output_file.csv") 
  {
#    print("use existing\n");
  }	  
  else
  {
    $cmd.= "-i $output_file.jpg -c $output_file.csv ";
#    print("$cmd \n\n $pan_hash");
    $result= qx/$cmd/;
 #   print("\nr: $result\n");
    #check if saved visibility is equal with current parameters, including name
  }


  if ($0=~/calc_panorama_image/) 
  {
    $cmd_image="cat $output_file.jpg";
    #if (0)
    if (not $refer =~ m/hamnetdb\.net|localhost/ )
    {
      $size_watermark= $size_y/6;
      $cmd_wartermark= " | convert png:- -gravity Center -pointsize $size_watermark -stroke none -fill 'rgba(180,180,180,0.4)' -annotate 0 'hamnetdb.net' jpg:- 2>>$path_errlog";
      $cmd_image.= $cmd_wartermark;
    }
    #print("Content-Type: text/html\nExpires: 0\n\n");
    #print($cmd_image);

    print("Content-Type: image/jpg\n\n");
    $result_image= qx/$cmd_image/;
    print qq($result_image);
  }
  elsif ($0=~/calc_panorama_metadata/) 
  {
    $cmd_meta="cat $output_file.csv";
    $result_meta= qx/$cmd_meta/;
    print("Content-Type: text/html\nExpires: 0\n\n");
    print qq($result_meta);
  }
  else 
  {
    print("Content-type: text/html\n\n");
    print("preparing\n\n$cmd\n\n");
  }

