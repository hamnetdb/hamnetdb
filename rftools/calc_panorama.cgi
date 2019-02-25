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

#print("Content-Type: text/html\nExpires: 0\n\n");
#print("test result___ $0\n");
# path ; label; lat1; lon1; tower1; lat2; lon2; tower2; towerRX; ref; top; left; bottom; right;  
#print("/osm_disk;testbereich;47.80;13.10;9;47.80;12.99;8;0;0.25;0;0;0;0\n");

#use paths from config.cgi
$path_prog= $panorama_path_program;
$path_srtm= $panorama_path_srtm;
$path_errlog= $panorama_path_errorlog;
$path_web= $panorama_path_web;

#check parameters
#if poi str in field add poi
#cmd str => md5
#check if md5 png csv exists
#
#if skript name = png calc png;  if csv calc csv and png
#
#complete cmd (output parameter)
#
#png
#open png print
#
#csv
#print ok \n csv
#
  #min 
  $refraction= 0 if $refraction<0;
  $antenna_a= 0  if $antenna_a<0;
  $size_x= 100 if $size_x<100;
  $size_y= 100 if $size_y<100;
  $font_size= 0 if $font_size<0;
  $elevation= -90 if $font_size<-90;
  $angle= 1 if $angle<1;
  $zoom= 1 if $zoom < 0.1;

  #max
  $refraction= 1 if $refraction>1;
  $antenna_a= 3000  if $antenna_b>3000;
  $size_x= 6000 if $size_x>6000;
  $size_y= 2160 if $size_y>2160;
  $font_size= 3 if $font_size>3;
  $elevation= 90 if $font_size>90;
  $angle= 360 if $angle>360;
  $zoom= 10 if $zoom>10;

#./panorama-x86-32 -A 20 -a JN67OH74WD -b JN68DE93KQ  -i /home/hamnetdb/htdocs/pan1.png -p /opt/coverage/ -w 60.0 -x 1920 -y 1080 -e -6 -H 0 0 200 -F 1 -g 2.3 -I marker1.png  -P hamnet.txt -I cam.png -P 255 255 255 255 fotowebcam.txt -o 3 -I markerg.png -P 254 80 254 fone.txt
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
  #bc
  #hamnet
  #foto-webcam
  #alps
  #europe
  if ($poi=~/hamnet/) 
  {
    $poi_param.="-J h -I $path_web/rftools/mk_w.png -P 255 0 0 240 $path_web/rftools/hamnet.txt "; 
  }
  if ($poi=~/sota/)
  {  
    $poi_param.="-J sota -I $path_web/rftools/mks_w.png -P 0 255 0 250 $path_web/rftools/sota.txt ";
  }
  if ($poi=~/wc/) 
  {
    $poi_param.="-J wc -I $path_web/rftools/mk_cam.png -P 255 255 255 200 $path_web/rftools/fotowebcam.txt ";
  }
  if ($poi=~/fone/) 
  {
    $poi_param.="-J f -I $path_web/rftools/mk_w.png -P 0 255 0 100 $path_web/rftools/fone.txt ";
  }
  if ($poi=~/mt/) 
  {
    $poi_param.="-J MT -I $path_web/rftools/mkss_w.png -P 100 100 100 200 $path_web/rftools/alps.txt ";
    $poi_param.="-J MT -I $path_web/rftools/mkss_w.png -P 100 100 100 200 $path_web/rftools/MT.txt ";
  }
  if ($poi=~/small/)
  {  
    $poi_param.="-J s -I $path_web/rftools/mkxs_w.png -P 60 60 60 100 $path_web/rftools/AT.txt ";
  }

  my $cmd= "nice -n 9 $path_prog -p $path_srtm -A $antenna_a ";
  $cmd.= "-a $lat_a $lon_a -b $lat_b $lon_b -z $zoom ";
  $cmd.= "-e $elevation $font_cmd -g 2.3 -o 5 -q -C 3 ";
  $cmd.= "-x $size_x -y $size_y -w $angle $poi_param ";
  $cmd.= "-r $refraction ";
  $pan_hash= md5_hex($cmd);

  #if file $pan_hash exists dont calc
  #  $pan_hash= "test";
  $output_file="$path_web/rftools/panorama/$pan_hash";
  if (-e "$output_file.csv") 
  {
 #   print("use existing\n");
  }	  
  else
  {

    $cmd.= "-i $output_file.png -c $output_file.csv ";
 #   print("$cmd \n\n $pan_hash");

    $result= qx/$cmd/;


 #   print("\nr: $result\n");
    #check if saved visibility is equal with current parameters, including name

  }


  if ($0=~/calc_panorama_image/) 
  {

    $cmd_image="cat $output_file.png";
    if (not $refer =~ m/hamnetdb\.net/ )
    #if (0)
    {
      $size_watermark= $size_y/6;
      $cmd_wartermark= " | convert png:- -gravity Center -pointsize $size_watermark -stroke none -fill 'rgba(180,180,180,0.3)' -annotate 0 'hamnetdb.net' png:- 2>>$path_errlog";
      $cmd_image.= $cmd_wartermark;
    }
					
    #print("Content-Type: text/html\nExpires: 0\n\n");
    #print($cmd_image);

    print("Content-Type: image/png\n\n");
    $result_image= qx/$cmd_image/;
    print qq($result_image);
  }
  elsif ($0=~/calc_panorama_metadata/) 
  {
    $cmd_meta="cat $output_file.csv";
    $result_meta= qx/$cmd_meta/;
    print("Content-Type: text/html\nExpires: 0\n\n");
    #print("metadata\n");
    print qq($result_meta);
  }
  else 
  {
    print("Content-type: text/html\n\n");
    print("preparing\n\n\n\n");
  }




#panorama
# -A <m>                            Camera over ground [m] (10)
# # -a <lat> <long> | [locator]       Camera position lat long (degrees) or qth locator
# # -b <lat> <long> | [locator]       Pan to point lat long (degrees) or qth locator
# # -c <filename>                     CSV file name
# # -d <deg> <km>                     Relative to position a (alternativ to -b)
# #                                     km distance sight limit
# # -e <degrees>                      Camera Elevation (degrees) (0.0)
# #                                     speed optimizer, surface contrast and dust calculation
# #                                     are able to handle only small elevations!
# # -F <font>                         Font Size (1) 1: 6x10, 2: 8x14, 3: 10x20
# # -f                                Flat screen else Curved projection area (needed at >=180deg sight)
# # -g <gamma>                        Image Gamma 0.1..10 (2.2)
# # -H <r> <g> <b>                    Heaven colour (50 70 300)
# # -h                                this
# # -I <filename>                     Symbol Image File Name, set before -P
# # -i <filename>                     Image File Name
# # -M <bytes>                        SRTM-Cache Limit (100000000)
# # -O                                POI File altitude is over ground not NN
# # -o <m>                            min. POI altitude over ground (1)
# #                                     if given in POI file and higher use this
# # -P [<r> <g> <b> [<transp>]] <filename>  optional icon colours (0..255) POI File Name
# #                                     repeat for more files
# # -p <pathname>                     folder with /srtm1 /srtm3 /srtm30
# # -r <refraction>                   0.0(vacuum)..1.0(earth is a disk) (0.13)
# # -s <size>                         POI symbol size (5)
# # -v                                Say something
# # -w <degrees>                      Camera horizontal sight angle (degrees) (45.0)
# # -x <size>                         Image size x (600)
# # -y <size>                         Image size y (400)
# # -z <factor>                       Vertical Zoom (for 360deg panorama) (1.0)
# path_list= "visibility.csv";


