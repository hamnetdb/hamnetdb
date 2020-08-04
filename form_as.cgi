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

$suffix= "as";
$table= "hamnet_$suffix";
$table_history= "${table}_hist";
$requiredPermission= $suffix;

($name,$as_num,$as_root,$country,$comment,$maintainer,$dns_add,$rw_maint)= 
&loadFormData
("name,as_num,as_root,country,comment,maintainer,dns_add,rw_maint");

&checkMaintainerRW($rw_maint, $maintainer);
unless ($mustLoadFromDB) {
  $as_root= $query->param("as");
}

$caption= "Change AS '$name'";
$caption= "New AS" unless $id;

if ($func eq "delete") {
  my $dep= &asDependency($as_num);
  if ($dep) {
    $func= "store";
    $inputStatus= "Cannot delete: $dep";
  }
}
&beforeForm($caption);

print qq(
  <div class="formnline">
    <div class="formn1" align="left" nowrap>AS-Number:<br>
    <input type="text" name="as_num" value="$as_num" style='width:80px;' $chtrack>
    <input type="hidden" name="as_num_orig" value="$as_num">
    <br>$br10
    </div>
    <div class="formn2" align="left" nowrap>Descriptive Name:<br>
    <input type="text" name="name" value="$name" style='width:250px;' $chtrack>
    </div>
    <div class="formn3" align="left" nowrap>Root AS:<br>
    );
    &asCombo(0,0,1,$as_root,"style='width:200px;overflow:hidden;'");
  print qq(
    </div>
    <div class="formn1" align="left" nowrap>Country 
    <a target='_blank' href='https://en.wikipedia.org/wiki/ISO_3166-1'>TLD</a><br>
    <input type="text" name="country" value="$country" style='width:30px;' $chtrack>
    <small>e.g. <b>at ch de</b></small>
    </div>
  </div>
  <div class="formnline">
    <div class="formn1" align="left" nowrap >List of maintainers 
    (callsigns, comma separated):<br>
    <input type="text" name="maintainer" value="$maintainer" style="width:100%"$chtrack>
    </div>
  </div>
  <div class="formnline">
);

if (&inList($username, $maintainer) || ($mySysPerm && $maintainer)) {
  &checkBox("Restrict write access to list of AS maintainers",
            "rw_maint", 0, $rw_maint);
}

print qq(
  </div>
  <div class="formnline">
    <div class="formnfull">
    Add records to DNS zone for this AS 
    (No check! Be careful: Whole zone may become invalid on errors):<br>
    <textarea name="dns_add" class="txt" $chtrack
              style="width:100%; height:100px;">$dns_add</textarea>
    </div>
  </div>
  <div class="formnline">

  Comment area:<br>
  <textarea name="comment" class="txt" $chtrack
            style="width:100%; height:170px;">$comment</textarea>
  </div>
);
&afterFormn;
exit;


# --------------------------------------------------------------------------
# check and store values
sub checkValues {
  $as_num=~s/as *//i;
  $as_num+= 0;
  my $orig= $query->param("as_num_orig")+0;
  if ($id && $orig>0 && $as_num!=$orig) {
    my $dep= &asDependency($orig);
    if ($dep) {
      $inputStatus= "Cannot rename: $dep";
    }
  }
  if ($as_num<64512) {
    $inputStatus= "AS number must be above 64512";
  }
  $as_root=~s/as *//i;
  $as_root+= 0;
  if ($as_root>0) {
    my $rc= "";
    ($rc)= $db->selectrow_array("select country from $table ".
          "where as_num='$as_root'");
    if ($country ne $rc) {
      $inputStatus= "Country must be the same for Root AS";
    }
    elsif ($as_num == $as_root) {
      $inputStatus= "Root AS cannot point to myself";
    }
  }
  unless ($name) {
    $inputStatus= "Name is missing";
  }
  unless ($inputStatus) {
    if ($db->selectrow_array("select as_num from $table ".
          "where as_num='$as_num' and id<>'$id'")) {
      $inputStatus= "The AS$as_num exists already";
    }
    if ($db->selectrow_array("select name from $table ".
          "where name='$name' and id<>'$id'")) {
      $inputStatus= "The AS '$name' exists already";
    }
  }
  $maintainer= lc $maintainer;
  $country= lc $country;
  unless ($country=~/^[a-z][a-z]$/) {
    $inputStatus= "Country code is incorrect (iso-3166 tld)";
  }
  $rw_maint+= 0;
  &checkMaintainerRW($rw_maint, $maintainer);
  return  "comment=".$db->quote($comment).", ".
          "name=".$db->quote($name).", ".
          "maintainer=".$db->quote($maintainer).", ".
          "rw_maint=".$db->quote($rw_maint).", ".
          "as_root=".$db->quote($as_root).", ".
          "country=".$db->quote($country).", ".
          "dns_add=".$db->quote($dns_add).", ".
          "as_num=$as_num";
}
