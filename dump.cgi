#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - Dump MySQL tables
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
$date= strftime("%Y-%m-%d-%H%M", localtime);
print("Content-Type: text/plain\n");
print("Content-Disposition: attachment; filename=hamnetdb-$date.sql\n\n");

$no_data= "";
$tables= "hamnet_site hamnet_antennafiles hamnet_as hamnet_coverage hamnet_host hamnet_subnet hamnet_edge";
$tables.= " hamnet_site_hist hamnet_antennafiles_hist hamnet_as_hist hamnet_coverage_hist hamnet_host_hist";
$tables.= " hamnet_subnet_hist hamnet_edge_hist hamnet_check";

if ($query->param("tables")) {
  $tables.= " hamnet_maintainer hamnet_maintainer_hist hamnet_session";
  $no_data= "--no-data";
}

$tmpname= "/tmp/hamnetdb-dump-$$.sql";
system("mysqldump $no_data -u $db_user --password=$db_pass $db_name $tables >$tmpname");

open(F, "<$tmpname") || die("cannot open dump file");
while (read(F, $buffer, 16384)) {
  print $buffer;
}
close(F);
unlink($tmpname);
