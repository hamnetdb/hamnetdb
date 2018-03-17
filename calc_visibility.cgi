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
do "lib.cgi" or die;

my $refer = $ENV{HTTP_REFERER};
my $list= $query->param("list")+0;
my $lat_a= $query->param("lat_a")+0; #breitengrad (bauch)
my $lon_a= $query->param("lon_a")+0; #laengengrad
my $antenna_a= $query->param("ant_a")+0;
my $lat_b= $query->param("lat_b")+0;
my $lon_b= $query->param("lon_b")+0;
my $antenna_b= $query->param("ant_b")+0;
my $label= $query->param("label");
my $antenna_c= $query->param("ant_c")+0;
my $refraction= $query->param("ref")+0;
my $border_up= $query->param("up")+0;
my $border_left= $query->param("left")+0;
my $border_down= $query->param("down")+0;
my $border_right= $query->param("right")+0;


print("Content-Type: text/html\nExpires: 0\n\n");

#print("test result___\n");
# path ; label; lat1; lon1; tower1; lat2; lon2; tower2; towerRX; ref; top; left; bottom; right;  
#print("/osm_disk;testbereich;47.80;13.10;9;47.80;12.99;8;0;0.25;48.22;12.8;47.36;14.0\n");
#print("/osm_disk;testbereich;47.80;13.10;9;47.80;12.99;8;0;0.25;0;0;0;0\n");
#use paths from config.cgi
$path_prog= $visibility_path_program;
$path_srtm= $visibility_path_srtm;
$path_errlog= $visibility_path_errorlog;
$path_out= $visibility_path_out;


unless ($list) {

  #min 
  $refraction= 0 if $refraction<0;
  $frequency= 1  if $frequency<1;
  $antenna_a= 0  if $antenna_b<0;
  $antenna_b= 0  if $antenna_b<0;
  $antenna_c= 0  if $antenna_c<0;

  #max
  $refraction= 1 if $refraction>1;
  $antenna_a= 3000  if $antenna_b>3000;
  $antenna_b= 3000  if $antenna_b>3000;
  $antenna_c= 3000  if $antenna_c>3000;

  $label= checkLabel($label);


  my $path_out_rnd= generateRndDir();
  my $color_a= "255 0 0 120"; #red
  my $color_b= "0 0 255 120"; #blue
  my $color_c= "0 255 255 110"; #greenblue
  my $dx = 1.3;
  my $dy = 0.9;
  my $center_lat;
  my $center_lon;

  if ($lan_b == 0 && $lon_b == 0) {
    $center_lat= $lat_a; 
    $center_lon= $lon_a;
  }
  else {
    $center_lat= ($lat_a + $lat_b)/2;
    $center_lon= ($lon_a + $lon_b)/2;
  }

  my $cmd= "nice -n 19 $path_prog -p $path_srtm -o $path_out$path_out_rnd";
  $cmd.= " -x 32000 -y 32000 -z 1 14 -d 2 -g 7 -q 2 -R $refraction";

  if ($border_up != 0 && $border_left != 0 && $border_down !=0 && $border_right != 0) {

    #check border size, crop form far end if needed
    if (abs($border_up - $border_down) > 2*$dy) {
      if (abs($border_up - $center_lat) > abs($center_lat - $border_down)) {
        $border_up= $border_down + 2*$dy;
      }
      else {
        $border_down= $border_up - 2*$dy;
      }
    }
    if (abs($border_left - $border_right) > 2*$dx) {
      if (abs($border_right - $center_lon) > abs($center_lon - $border_left)) {
        $border_right = $border_left + 2*$dx;
      }
      else {
        $border_left = $border_right - 2*$dx;
      }
    }
  }
  else { #  create border?


    $border_up= $center_lat + $dy;
    $border_left= $center_lon - $dx;
    $border_down= $center_lat - $dy ;
    $border_right= $center_lon + $dx;
  }
    $cmd.= " -m $border_up $border_left -n $border_down $border_right"; 


  #define colors
  if ( $lat_a != 0 && $lon_a != 0  && $lat_b != 0 && $lon_b != 0) {
    $cmd.= " -a $lat_a $lon_a -A $antenna_a";
    $cmd.= " -b $lat_b $lon_b -B $antenna_b -C $antenna_c";
    $cmd.= " -U $color_a -V $color_b -W $color_c 0";
  }
  elsif ( $lat_a != 0 && $lon_a != 0 && lat_b == 0 && lon_b == 0 ) {
    $cmd.= " -a $lat_a $lon_a -A $antenna_a -B $antenna_c";
    $cmd.= " -W $color_a 0";
  } 
  elsif ( $lat_a == 0 && $lon_a == 0 && lat_b != 0 && lon_b != 0 ) {
    $cmd.= " -a $lat_b $lon_b -A $antenna_b -B $antenna_c";
    $cmd.= " -W $color_a 0";
  }
  else {
    $error = 1;
  }
#print qq($cmd);

  unless ($error) {
#    $cmd.= "2>&1";
    $result= qx/$cmd/;
  }

  #catch errors
  my $len=length($result);
  if ($len == 1) {
    open(my $fh, '>>', $path_errlog) or die "Could not open file";
    print $fh "$cmd\n";
    close $fh;
    print qq(Error creating visibility! :\( \n); 
  }
  else {
    print qq(OK! $result \n);
    #$label= listAdd($label);
    print("rfvisibility/$path_out_rnd;$label;$lat_a;$lon_a;$antenna_a;$lat_b;$lon_b;$antenna_b;$antenna_c;$refraction;$border_up;$border_left;$border_down;$border_right\n");
  }
  print qq($cmd);
}
 # -A <m>                            Antenna A over ground [m] (10)
 # -a <lat> <long> | [locator]       Position A lat long (degrees) or qth locator
 # -B <m>                            Antenna B over ground [m] (10)
 # -b <lat> <long> | [locator]       Position B lat long (degrees) or qth locator
 # -C <m>                            0 for ground echo or Repeater Antenna over ground [m] (0)
 # -c <contrast>                     0 for hard 30 for smooth area margin (3)
 # -d <depth>                        png palette bits/pixel 1,2,4,8 (1)
 # -g <gamma>                        image gamma 0.1..10.0 (2.2)
 # -h                                this
 # -i <filename>                     enable fullsize image with Image File Name
 # -M <bytes>                        srtmcache size (200000000)
 # -m <lat> <long> | [locator]       left up position of image
 # -n <lat> <long> | [locator]       alternate to -x -y: right down position of image
 #                                       set -x -y too as size limit
 # -o <path>                         enable tiles with Path Name
 # -p <path>                         srtm directory path
 # -Q                                srtm interpolation off (on)
 # -q <quality>                      0=fast 3=best (2)
 # -R <refraction>                   0.0(vacuum), 1.0(earth is a disk) (0.25)
 # -U <red> <green> <blue> <transp>  colour antenna 1
 # -V <red> <green> <blue> <transp>  colour antenna 2
 # -v                                verbous
 # -W <red> <green> <blue> <transp> <blacktransp>
 #                                   (0..255) colour antenna 1 or reflection
 # -x <size>                         Image size (600)
 # -y <size>                         Image size (400)
 # -z <from> <to>                    make tiles from..to zoomlevel 1..18
 # -Z <from> <to>                    as -z but write empty tiles too


# 0 0 255 110  blau
# 255 0 .0 110     rot
# -W  255 0 255 115 0     rosa
#-c 4 -z 1 14 -d 8



#date && ./radiorange-x86-64 -a JN67NT32EW -A 20 -b JN68PC74II -B 20 -m JN68LH -C 1 -x 32000 -y 32000 -o /media/spel/daten/tmp_osm/ -p osm/ -R 0.25 -U 255 0 0 120 -V 0 0 255 120 -W 00 255 255 120 0 -z 1 14 -d 2 -g 7 -q 2 && date

#$cmd= "$path_prog -b $lat_b $lon_b $name_b -a $lat_a $lon_a $name_a -p $path_srtm -i /dev/stdout $globe_val 0.25 -f $frequency -A $antenna_a -B $antenna_b -x $size_x -y $size_y $wood -F $font_size 2>>$path_errlog";


sub generateRndDir {
  #my $try= map{(a..z,0..9)[rand 36]} 0..10;
  my @set = ('0' ..'9', 'a' .. 'z');
  my $try = join '' => map $set[rand @set], 1 .. 10;
  my $path= $path_out.$try;
  if (-d $path) {
    return generateRndDir();
  }
  else {
    mkdir $path;
    return $try;
  }
}
sub checkLabel {  
  my $text= shift;
  $text =~ s/[^a-zA-Z0-9\-\_\ ]//g;
  if(length($text) > 30) {
    $text= substr($text, 0, 30 );
  }
  return $text;
}
sub listRead {
  #read file and make output list
  open my $handle, '<', $path_list;
  chomp(my @lines = <$handle>);
  close $handle;
  return @lines;
}
sub listAdd {
  my $text= shift;
  my $rnd_folder = shift;
  #check if label exists and add _#
  #add to file

  return $text;
}
