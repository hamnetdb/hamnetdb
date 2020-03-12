#!/usr/bin/perl -w
# ---------------------------------------------------------------
# Hamnet IP database - Antenna management
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
#
# Licensed under the Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commecial projects
# - you must leave author and license conditions
# ---------------------------------------------------------------

# TODO TODO TODO TODO 
#
# fully integrate to form.cgi (restore/recover)
# remove "valid" collum
push @INC,'.';
do "form.cgi" or die;
use Scalar::Util qw(looks_like_number);

$suffix= "antenna";
$table= "hamnet_${suffix}files";
$table_history= "${table}_hist";
$requiredPermission= "site";

my $file;
my $func= $query->param("func");
my $raw_file= $query->param("antennafile");
my $antennatypeReload= $query->param("antennatypeReload");

($name,$file,$valid)=
  &loadFormData
  ("name,file,valid");

#only for antenna
if($func eq "antennarestore")
{
  &reloadAntenna;
}


my $caption= "Hamnet-Antenna management";
&beforeForm($caption);


my $sth= $db->prepare("select name from hamnet_antennafiles where deleted=0 order by name");
$sth->execute;
while (@line= $sth->fetchrow_array) 
{
  push(@antenna, "$line[0]");
}

my $sth2= $db->prepare("select name from hamnet_antennafiles_hist order by name");
$sth2->execute;
while (@line= $sth2->fetchrow_array) 
{
  push(@antenna_hist, "$line[0]");
}


print qq(
    <input type="hidden" name="name" value="">

    </table>
      <h2>Upload Hamnet-Antenna</h2>
      <p>Choose an .ant file from your file system:<br>
        <br>
        <input name="antennafile" type="file" size="50" maxlength="100000" accept="text/*"><br> <br>
        Antenna Description (e.g. omnidirectional, or model number): 
          <input name="antennanameStore" type="text" size="30"><br>
        <button id="storebut" type="button" onclick="doAntennaStore();">
          Add Antenna</button>
      
        <br><br><br>
        <h2>Remove Antenna</h2>
        Select Antennapattern to remove it from DB: <br>
    );

    &comboBox("", "antennatypeRemove", " ", "::-None-", @antenna);

print qq(
      <a id="showant"  href="javascript:hamnetdb.antennaShow('Remove','0')";> Show selected Pattern </a> 
      <br>
      <br>
      <button id="delebut" type="button" onclick="doAntennaDelete();">Delete</button>
   
      <br><br><br>
      <h2>Reload Hamnet-Antenna from Archiv</h2>
  
    <p>Choose a pattern from Archiv:
);
    
    &comboBox("", "antennatypeReload", " ", "::-None-", @antenna_hist);

print qq(
      <a id="antennatyperel"  href="javascript:hamnetdb.antennaShow('Reload','1');"> Show selected Pattern </a> 
      <br>
        Description (must be unique):
        <input name="nameReload" type="text" size="30">
        <br>
        <br>
        <button id="delebut" type="button" onclick="doAntennaRestore();">Reload Antenna</button>
      </p></from>
      <script>
        function doAntennaDelete()
        {
          var name = document.getElementsByName("antennatypeRemove")[0].value;
          document.main.name.value=name;
          document.main.func.value='delete';
          document.main.confirm.value=$confirm;
          document.main.ischanged.value=isChanged;
          unchanged();
          document.main.submit();
        }
        function doAntennaStore()
        {
          var name = document.getElementsByName("antennanameStore")[0].value;
          document.main.name.value=name;
          document.main.func.value='store';
          document.main.submit();
        }
        function doAntennaRestore()
        {
          var name = document.getElementsByName("antennanameStore")[0].value;
          document.main.name.value=document.getElementsByName("nameReload")[0].value;;
          document.main.func.value='antennarestore';
          document.main.submit();
        }
      </script>
    </body>
  </html>
);



sub checkValues {
  my @text= <$raw_file>;
  my $lenght= @text;
  my $wrongend= 0;
  my $error= 0;
  if ($name eq "" || $name eq " " || $name eq "  ") {
    $inputStatus="Failed: Choose a name for the new antenna file.";
  }
  elsif ($name =~/ / || $name =~/:/ || $name =~/\./ || $name =~ /;/) {
    $inputStatus="Failed: Invalid name. No ':', '.', ';' or empty space allowed.";
  }
  elsif(length($name) > 20 ) {
    $inputStatus="Failed: Antenna name to long. Choose a shorter one (less than 20 characters).";
  }
  unless ($inputStatus) {
    unless ($file) { 
      my $nameh=$db->prepare("select name from hamnet_antennafiles");
      $nameh->execute();

      while($that=$nameh->fetchrow_array()) {
        if($that eq $name) {
          $inputStatus="Failed: Invalid name. Name already used.";
        }
      }
      unless ($inputStatus) {
        my $extension =  $raw_file;
        while ($extension =~ s/.*\.//) {}
        if (!($extension eq "ant")) {  
          $wrongend =1;
        } 
        if($lenght != 720 || $wrongend ==1) {
          $inputStatus="Uploaded wrong Format: File need to have 720 numeric values seperated by new line or \" \"  extension needs to be .ant, Extension: $extension.";
        }
        else {
          foreach(@text) {
            if(looks_like_number($_)) {
              $file = "$file $_";
            }
            else {
              $inputStatus="Upload failed. A t least one not numeric value in file.";
            }
          }
        }
      }    
    }
  }

  my $newversion= 0;
  return  "file=".$db->quote($file).", ".
          "name=".$db->quote($name).", ".
          "valid=".$db->quote("1");
}

sub nametoid {
  if ($name eq "" || $name eq " " || $name eq "  ") {
    $inputStatus="No antenna selected!";
  }
  unless($inputStatus) {
    my $sth3= $db->prepare("select id from hamnet_antennafiles where name = '$name'");
    $sth3->execute;
    my $antId =$sth3->fetchrow_array();
    
    return $antId; 
  }  

}

sub reloadAntenna {
  #take old data and do normal store
  if (length($name) > 20) {
    $inputStatus="Failed: Antenna name to long. Choose a shorter one (less than 20 characters).";
  }
  unless ($inputStatus) {
    if($name eq "" || $name eq " " || $name eq "  ") {
      $inputStatus="Failed: Choose a name for the new antenna file.";
    }
    if($name =~/ / || $name =~/:/ || $name =~/\./ || $name =~ /;/) {
      $inputStatus="Failed: Invalid name. No ':', '.', ';' or empty space allowed.";
    }
    unless ($inputStatus) {
      my $antH= $db->prepare("SELECT file from hamnet_antennafiles_hist where name='$antennatypeReload' order by id desc limit 0,1");
      $antH->execute();
      $file=$antH->fetchrow_array();
      $func= "store";
    }
  }   
}

