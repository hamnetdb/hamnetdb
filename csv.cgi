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
do "lib.cgi" or die;
#
$tab= $query->param("tab");

unless ($tab=~/^(site|host|subnet|as|edge)(|_hist)$/) {
  print qq(Content-Type: text/plain\n\n).
        qq(Usage: csv.cgi?tab=[site|host|subnet|as]\n);
  exit;
}

$date= strftime("%Y-%m-%d-%H%M", localtime);
print qq(Content-Type: binary/octet-stream\n).
 qq(Content-Disposition: attachment; filename=hamnetdb-$tab-$date.csv\n\n).
 qq(sep=,\r\n);

my $sth= $db->prepare(qq(select * from hamnet_$tab));
if ($sth->execute) {
  @headers= @{$sth->{"NAME"}};
  my $colnum= int(@headers);

  for ($i= 0; $i<$colnum; $i++) {
    my $n= $headers[$i];
    $n= ucfirst($n) if $n=~/^[a-z]+$/;
    print "," if $i;
    $n=~s/"/'/g;
    print qq("$n");
  }
  print qq(\r\n);
  my $count= 0;
  while(@line= $sth->fetchrow_array) {
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
