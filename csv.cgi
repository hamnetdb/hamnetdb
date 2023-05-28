#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Dump CSV
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
#
# Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# -------------------------------------------------------------------------
#
push @INC,'.';
do "lib.cgi" or die;
#
use JSON;
use Data::Dumper;


$tab= $query->param("tab");
$json= $query->param("json");

$json+= 0;


unless ($tab=~/^(site|host|subnet|as|edge|check)(|_hist)$/) {
  print qq(Content-Type: text/plain\n\n).
        qq(Usage: csv.cgi?tab=[site|host|subnet|as|check]&json=[1]\n);
  exit;
}

$date= strftime("%Y-%m-%d-%H%M", localtime);
if ($json) {
  print qq(Content-Type: application/json filename=hamnetdb-$tab-$date.json\n\n);
}
else {
  print qq(Content-Type: binary/octet-stream\n).
  qq(Content-Disposition: attachment; filename=hamnetdb-$tab-$date.csv\n\n).
  qq(sep=,\r\n);
}

my $sth= $db->prepare(qq(select * from hamnet_$tab));
if ($sth->execute) {
  @headers= @{$sth->{"NAME"}};
  my $colnum= int(@headers);
  if (!$json) {
    for ($i= 0; $i<$colnum; $i++) {
      my $n= $headers[$i];
      $n= ucfirst($n) if $n=~/^[a-z]+$/;
      print "," if $i;
      $n=~s/"/'/g;
      print qq("$n");
    }
    print qq(\r\n);
  }  
  my @mydata;
  my $json_out = JSON->new;
#  if ($json) {
#    $json_out = JSON->new;	
#  }
  my $count= 0;
  while(@line= $sth->fetchrow_array) {
    if ($json) {
      my $row = {};
      my @row1;
      for ($i= 0; $i<$colnum; $i++) {
        my $f= $line[$i];
        $f=~s/\s/ /sg;
        $f=~s/"/'/sg;
        if ($f=~/^\d+\.\d+$/) {
          $f=~s/\./,/;
        }
        #$row{$headers[$i]} = $f;
        $row->{$headers[$i]} = $f;
      }
      #my $convert = JSON->new->pretty;
      #print $convert->encode(\%row);
      #$row_out = $convert->encode(\%row);
      push @mydata, $row;
      #push @mydata, $row;
      #$mydata[$count]= \%row;
      #print Dumper(\%row);
      #print Dumper(\%{ $mydata[$count-1] });
    }
    else {
      for ($i= 0; $i<$colnum; $i++) {
        my $f= $line[$i];
        print "," if $i;
        $f=~s/\s/ /sg;
        $f=~s/"/'/sg;
        if ($f=~/^\d+\.\d+$/) {
          $f=~s/\./,/;
        }
        print qq("$f");
      }
      print qq(\r\n);
    }
    
  }
  $count++;
  if ($json) {
    my $convert = JSON->new->pretty;
    print $convert->encode(\@mydata);
    #print $convert->encode(\@mydata);
  }
}
