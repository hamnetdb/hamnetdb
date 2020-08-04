#!/usr/bin/perl
# -------------------------------------------------------------------------
# Hamnet IP database - AS input form
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
do "form.cgi" or die;

$suffix= "servicetag";
$table= "hamnet_$suffix";
$table_history= "${table}_hist";
#$requiredPermission= $suffix;

($name,$parameter_label,$parameter_example,$hierarchy)= 
&loadFormData
("name,parameter_label,parameter_example,hierarchy");

#only Sysadmins allowed
&checkMaintainerRW(1, "");

$caption= "Change Service-Tag '$name'";
$caption= "New Service-Tag" unless $id;


#TODO check dependendy
#
#if ($func eq "delete") {
#  my $dep= &asDependency($as_num);
#  if ($dep) {
#    $func= "store";
#    $inputStatus= "Cannot delete: $dep";
#  }
#}
&beforeForm($caption);

print qq(
  <div class="formnline">
    <div class="formn1" align="left" nowrap>Name:<br>
    <input type="text" name="name" value="$name" style='width:80px;' $chtrack>
    <input type="hidden" name="name_orig" value="$name">
    <br>$br10
    </div>
    <div class="formn2" align="left" nowrap>Parameter Label:<br>
    <input type="text" name="parameter_label" value="$parameter_label" style='width:250px;' $chtrack>
    </div>
    <div class="formn3" align="left" nowrap>Parameter Example:<br>
    <input type="text" name="parameter_example" value="$parameter_example" style='width:250px;' $chtrack>
    </div>
  </div>
  <div class="formnline">
    <div class="formn1" align="left" nowrap>Hierarchy:<br>
    <input type="text" name="hierarchy" value="$hierarchy" style='width:80px;' $chtrack>
    <input type="hidden" name="hierarchy_orig" value="$hierarchy">
  </div>

);
&afterFormn;
exit;


# --------------------------------------------------------------------------
# check and store values
sub checkValues {
  unless ($name) {
    $inputStatus= "Name is missing";
  }
  unless ($inputStatus) {
    if ($db->selectrow_array("select name from $table ".
          "where name='name' and id<>'$id'")) {
      $inputStatus= "The TAG $name exists already";
    }
  }
  $maintainer= lc $maintainer;
  $country= lc $country;
 
  return  "name=".$db->quote($name).", ".
          "parameter_label=".$db->quote($parameter_label).", ".
          "parameter_example=".$db->quote($parameter_example).", ".
          "hierarchy=".$db->quote($hierarchy);
}
