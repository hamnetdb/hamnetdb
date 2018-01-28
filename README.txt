# ---------------------------------------------------------------
# Hamnet IP database - Installation Notes
#
# Flori Radlherr, DL8MBT, http://www.radlherr.de
#
# Licensed under the Attribution-NonCommercial-ShareAlike 3.0
# http://creativecommons.org/licenses/by-nc-sa/3.0/
# - you may change, distribute and use in non-commercial projects
# - you must leave author and license conditions
# ---------------------------------------------------------------

This software runs with Linux / Apache / MySQL / Perl


*** Webserver ***

Apache needs to run CGI programs with extension .cgi
Thus following directive is needed for the current VirtualHost:

-> AddHandler cgi-script .cgi

For correct representation of German Umlaute you MIGHT need to
use UTF-8 character settings. First try it with default settings.
Maybe: -> AddDefaultCharset UTF-8

For the directory of the hamnetdb webserver you need the following options:
<Directory "/your/dir">
  Options +FollowSymLinks +ExecCGI
  DirectoryIndex index.cgi index.html
</Directory>


*** Database ***

You need an instance of a MySQL database and an user having all rights
on it. Maybe you want to create both using a tool like phpMyAdmin.
Lets say we call user and database *hamnet*, but of course you can
choose a different name.

Then set up the initial table structure:
wget -qO- 'http://hamnetdb.net/dump.cgi?tables=1' | mysql -u hamnet -p hamnet

Then fill in the current data content:
wget -qO- 'http://hamnetdb.net/dump.cgi' | mysql -u hamnet -p hamnet

You need Perl-DBI with MySQL module. 
On Debian-based linux: sudo apt-get install libdbd-mysql-perl

Normally all other needed base software should be already present.


*** Configuration ***

- Copy config.cgi.sample to config.cgi
- Fill in your database credentials
- If you want, decorate your page using htmlHead and htmlFoot functions.


*** User login ***

For security reasons the hamnet_maintainer table does not contain any
login credentials in the dump for public download. 

To get access, execute the following mysql command line:

insert hamnet_maintainer set callsign='yourCall',fullname='Your Name',
  email='your@email.com',passwd=PASSWORD('yourPassword'),
  permissions='as,site,subnet,host,maintainer,',version=1;

After that, you can log into the web interface and do the rest.


Have fun,
Flori DL8MBT

