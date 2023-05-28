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
do "../lib.cgi" or die;

my $refer = $ENV{HTTP_REFERER};
my $list= $query->param("list")+0;
my $load_saved= $query->param("load")+0;
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
my $tree= $query->param("tree")+0;
my $export= $query->param("e")+0;

my $error= 0;

#print("Content-Type: text/html\nExpires: 0\n\n");

#print("test result___\n");
# path ; label; lat1; lon1; tower1; lat2; lon2; tower2; towerRX; ref; tree; top; left; bottom; right;  
#print("/osm_disk;testbereich;47.80;13.10;9;47.80;12.99;8;0;0.25;48.22;12.8;47.36;14.0\n");
#print("/osm_disk;testbereich;47.80;13.10;9;47.80;12.99;8;0;0.25;0;0;0;0\n");
#use paths from config.cgi
$path_prog= $visibility_path_program;
$path_srtm= $visibility_path_srtm;
$path_errlog= $visibility_path_errorlog;
$path_out= $visibility_path_out;
$path_list= "visibility.csv";

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
  $new_label= listNewLabel($label);

  #if label & parameters are same in file use existing
  #if label & no parameters use existing



  my $color_a= "255 0 0 120"; #red
  my $color_b= "0 0 255 120"; #blue
  my $color_c= "0 255 255 110"; #greenblue
  #my $dx = 1.3;
  my $dx = 1.3;
  #my $dy = 0.9;
  my $dy = 0.8;
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

  my $cmd= "nice -n 9 $path_prog -p $path_srtm"; #reduce priority 
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

  if ($tree > 0) {
    $cmd.= " -t 30 2 ";
  }

  #check if saved visibility is equal with current parameters, including name
  $output_parameter= "$lat_a;$lon_a;$antenna_a;$lat_b;$lon_b;$antenna_b;$antenna_c;$refraction;$tree;$border_up;$border_left;$border_down;$border_right\n";
  $existing_parameter= listParameters($label);
  my @split_parameter= split(/;/, $existing_parameter);
  $parameter_plain= join(';',@split_parameter[2..14]);
  $output_parameter =~ s/^\s+|\s+$//g;
  $parameter_plain =~ s/^\s+|\s+$//g;
  if($output_parameter eq $parameter_plain) { 
    $load_saved= 1;
  }

  unless($load_saved) {
    my $path_out_rnd= generateRndDir();
    $output_parameter= "rftools/visibility/$path_out_rnd;$new_label;".$output_parameter."\n";
    $cmd.= " -o $path_out$path_out_rnd";
    unless ($error) {
      $cmd.= " 2>&1";
      $result= qx/$cmd/;
    }

    #catch errors
    my $len=length($result);
    if ($len >= 1 || $error) {
      print("Content-Type: text/html\nExpires: 0\n\n");
      open(my $fh, '>>', $path_errlog) or die "Could not open file";
      print $fh "failed $cmd\n";
      close $fh;
      print qq(Error creating visibility! $result :\( \n); 
    }
    else {
      if ($export) {
        exportZip($output_parameter);   
      } else {     
        print("Content-Type: text/html\nExpires: 0\n\n");
        print qq(OK! $result new\n);
        print($output_parameter);
        listAdd($output_parameter);
      }
    }
    #print qq(\n $cmd);
  }
  else
  {
    $output_parameter= listParameters($label);
    if (length($output_parameter) < 10) {
      print("Content-Type: text/html\nExpires: 0\n\n");
      print qq(Error creating visibility! :\( \n); 
    }
    else {
      if ($export) {
        exportZip($output_parameter);   
      } else {     
        print("Content-Type: text/html\nExpires: 0\n\n");
        print qq(OK! saved $result \n);
        print($output_parameter);
      }
    }
  }
}
else {
  print("Content-Type: text/html\nExpires: 0\n\n");
  listLabels();
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


sub generateRndDir {
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
  $text =~ s/^\s+|\s+$//g;
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
  @lines= reverse(@lines);
  return @lines;
}
sub listParameters {
  my $name= shift;
  my @lines= listRead();
  foreach $line (@lines) {
    my @fields = split(/;/, $line);
    if ($fields[1] eq $name) {
      return $line;
    }
  }
  return 0;
}
sub listLabels {
  my $text= shift;
  my @lines= listRead();

  foreach $line (@lines) {
    my @fields = split(/;/, $line);
    print qq(\n$fields[1]);
  }
}
sub listNewLabel {
  #compage strings, if last word is number, dont compare number
  #if strings matches increment number & return string with new number
  my $name= shift;
  my @names= split(/ /, $name);
  my @lines= listRead();
  my @numbers;
  my $new_name;
  my $size_n= scalar @names;

  if (looks_like_number($names[$size_n-1])) { 
    $size_n-= 1;
  }
  $name_plain= join(' ',@names[0..$size_n-1]);
  $name_plain =~ s/^\s+|\s+$//g;
#  print qq(plain in:"$name_plain" size_n:$size_n\n );
  foreach $line (@lines) {
    my @fields = split(/;/, $line);
    my @labels = split(/ /, $fields[1]);
    my $number;
    $size_l= scalar @labels;
    if (looks_like_number($labels[$size_l-1])) { 
      $size_l-= 1;
      $number= $labels[$size_l]+0;
    }
    $label_plain= join(' ',@labels[0..$size_l-1]);
    $label_plain =~ s/^\s+|\s+$//g;
#    print qq(plain_l:"$label_plain" size_n:$size_l\n );

    if($name_plain eq $label_plain) { #find highest number
#      print qq( equal \n);
      push @numbers, $number+1; 
    }
  }
  my $max_number = (max @numbers);
  if ($max_number >=1) {
    $new_name= qq($name_plain $max_number);
  }
  else{
    $new_name=$name_plain;
  }
  if(looks_like_number($name)) {
      $new_name= qq($max_number);
  }
  $new_name =~ s/^\s+|\s+$//g;
  if ($new_name eq "") {
    $new_name="1";
  }
  #print qq(\n$new_name); 
  return $new_name;
}
sub listAdd {
  my $text= shift;
  my $handle = $path_list;
  open(my $fh, '>>', $handle) or die "Could not open file '$handle' $!";
  print $fh $text;
  close $fh;
  return $text;
}
sub exportZip {
  my $param= shift;
  
  #extract path
  #zip 
  #push zip 
  @param2 = split /;/, $param;
  @folder = split /\//, $param2[0];
  $out= 'visibility/'.$folder[-1];
  $cmd="cd $out && zip -r - * ";
  print("Content-Type:application/octet-stream; name = \"export.zipF\"\r\n");
  print("Content-Disposition: attachment; filename = \"export.zip\"\r\n\n");
  $result_zip= qx/$cmd/;
  print qq($result_zip);
}
