#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Calculate topo-profile
#
# Lucas Speckbacher, OE2LSP
# Christian Rabler, OE5DXL (profile calulator)
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
use lib qw(.);
do "../lib.cgi" or die;

my $refer = $ENV{HTTP_REFERER};
my $size_y= $query->param("h")+0;
my $size_x= $query->param("w")+0;
my $frequency= $query->param("f")+0;
my $lat_a= $query->param("lat_a")+0; #breitengrad (bauch)
my $lon_a= $query->param("lon_a")+0; #laengengrad
my $antenna_a= $query->param("ant_a")+0; #laengengrad
my $lat_b= $query->param("lat_b")+0;
my $lon_b= $query->param("lon_b")+0;
my $antenna_b= $query->param("ant_b")+0;
my $notglobe= $query->param("ng")+0; #flat earther enabled (no globe)
my $name_a= $query->param("name_a");
my $name_b= $query->param("name_b");
my $wood= $query->param("wood")+0;
my $font_size= $query->param("font")+0;
my $mode= $query->param("mode")+0;

#print("Content-Type: text/html\nExpires: 0\n\n");

#use paths from config.cgi
$path_prog= $profile_path_program;
$path_srtm= $profile_path_srtm;
$path_errlog= $profile_path_errorlog;
$path_errimg= $profile_errorimg;




my $globe_val= "-R";
$globe_val="-r" if $notglobe == 1;

#min 
$size_x= 230  if $size_x<230;
$size_y= 100  if $size_y<100;
$frequency= 1  if $frequency<1;
$antenna_a= 0.1  if $antenna_b<0.1;
$antenna_b= 0.1  if $antenna_b<0.1;
$wood= 0  if $wood<0;
$font_size= 1  if $font_size<1;


#max
$size_x= 3840  if $size_x>3840;
$size_y= 2160  if $size_y>2160;
$frequency= 300000  if $frequency>300000;
$antenna_a= 3000  if $antenna_b>3000;
$antenna_b= 3000  if $antenna_b>3000;
$wood= 100  if $wood>100;
$font_size= 3  if $font_size>3;


$name_a= checkLabel($name_a);
$name_b= checkLabel($name_b);
	

if ($wood > 0) {
	$wood= "-w $wood";
}
else
{
	$wood= "";
}
if ($mode > 0) {
  $output_mode= "-c"; 
}
else
{
  $output_mode= "-i";
}


$cmd= "$path_prog -b $lat_b $lon_b $name_b -a $lat_a $lon_a $name_a -p $path_srtm $output_mode /dev/stdout $globe_val 0.25 -f $frequency -A $antenna_a -B $antenna_b -x $size_x -y $size_y $wood -F $font_size -C $profile_path_color 2>>$path_errlog";

#-C $profile_path_color

if ($mode > 0) {
  print("Content-Type: text/html\nExpires: 0\n\n");
  $result_profile= qx/$cmd/;
}
else
{
  if (not $refer =~ m/hamnetdb\.net/ )
  {
    $cmd_wartermark= " | convert png:- -gravity Center -pointsize 30 -stroke none -fill 'rgba(180,180,180,0.25)' -annotate 0 'hamnetdb.net' png:- 2>>$path_errlog";
    $cmd.= $cmd_wartermark;
  }
  $result_profile= qx/$cmd/;
  print("Content-type: image/png\n\n");
}

#catch errors
my $len=length($result_profile);
if ($len < 1000 && $mode<0)
{
  $cmd_err="cat $path_errimg";
  $result_err= qx/$cmd_err/;
  open(my $fh, '>>', $path_errlog) or die "Could not open file";
  print $fh "$cmd\n";
  close $fh;
  print qq($result_err); 
}
else
{
  print qq($result_profile); 
}

#print qq($cmd);

sub checkLabel {
	my $text= shift;
	$text =~ s/[^a-zA-Z0-9\-\_\ ]//g;
	if(length($text) > 30) {
		$text= substr($text, 0, 30 );
	}
	if(length($text) > 0) {
		$text= "-L '$text'";
	}
	return $text;
}
