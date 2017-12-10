// -------------------------------------------------------------------------
// Hamnet IP database - JavaScript parts
//
// Flori Radlherr, DL8MBT, http://www.radlherr.de
// Hubertus Munz
// Lucas Speckbacher, OE2LSP
//
// Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
// http://creativecommons.org/licenses/by-nc-sa/3.0/
// - you may change, distribute and use in non-commecial projects
// - you must leave author and license conditions
// -------------------------------------------------------------------------
//

// Limit DOM-namespace to a fixed prefix to avoid collisions
var hamnetdb= new Object;

// -------------------------------------------------------------------------
// Info popup metadata
hamnetdb.info= new Object;
hamnetdb.info.lastX= 0;
hamnetdb.info.lastY= 0;
hamnetdb.info.obj= "";
hamnetdb.info.timer= null;

// -------------------------------------------------------------------------
// Show info popup while mouse is over an element
hamnetdb.info.show= function(newInfoObject) {
  if (newInfoObject != hamnetdb.info.obj) {
    hamnetdb.info.obj= newInfoObject;
    hamnetdb.info.doHide();
    hamnetdb.info.timer= setTimeout(function () {
      if (hamnetdb.info.obj && hamnetdb.info.obj!='') {
        hamnetdb.info.doHide();
        var scrollPos;
        if (typeof window.pageYOffset != 'undefined') {
          scrollPos = window.pageYOffset;
        }
        else if (typeof document.compatMode != 'undefined' &&
             document.compatMode != 'BackCompat') {
          scrollPos = document.documentElement.scrollTop;
        }
        else if (typeof document.body != 'undefined') {
          scrollPos = document.body.scrollTop;
        }
        if (hamnetdb.info.lastX > (jQuery(window).width()-350)) {
          jQuery("#infoPopup").css("left","auto");
          jQuery("#infoPopup").css("right",
                (jQuery(window).width()-hamnetdb.info.lastX+10)+"px");
        }
        else {
          jQuery("#infoPopup").css("right","auto");
          jQuery("#infoPopup").css("left",(hamnetdb.info.lastX+10)+"px");
        }
        jQuery("#infoPopup").css("top", (hamnetdb.info.lastY+10)+"px");
        jQuery("#infoPopup").load("info.cgi?q="+hamnetdb.info.obj);
        jQuery("#infoPopup").fadeIn(600);
      }
    }, 400);
  }
}

// -------------------------------------------------------------------------
// Hide info popup
hamnetdb.info.doHide= function() {
  if (jQuery("#infoPopup").css("display") != "none") {
    jQuery("#infoPopup").fadeOut(600, function() {
      if (! hamnetdb.info.timer) {
        jQuery("#infoPopup").html("");
      }
    });
  }
} 

// -------------------------------------------------------------------------
// Trigger hide timer for info popup
hamnetdb.info.hide= function() {
  hamnetdb.info.obj= "";
  if (hamnetdb.info.timer) {
    clearTimeout(hamnetdb.info.timer);
    hamnetdb.info.timer= null;
  }
  hamnetdb.info.doHide();
}


// -------------------------------------------------------------------------
// Remember mouse move coordinates
hamnetdb.info.move= function(event) {
  if (event) {
    if (typeof(event.clientX) != "undefined") {
      hamnetdb.info.lastX= event.clientX; 
      hamnetdb.info.lastY= event.clientY;
    }
    else {
      hamnetdb.info.lastX= event.pageX;   
      hamnetdb.info.lastY= event.pageY;
    }
  }
}
document.onmousemove= hamnetdb.info.move;

// -------------------------------------------------------------------------
// Initialize mouse over info popup
jQuery(document).ready(function() {
  setTimeout(function() {
    // traverse over elements with class ovinfo and install handler
    jQuery(".ovinfo").each(function() {
      jQuery(this).mouseover(function() { 
        var inf= jQuery(this).attr('ovinfo');
        if (! inf) {
          inf= jQuery(this).text();
        }
        hamnetdb.info.show(inf);
      });
      jQuery(this).mouseout(function() {
        hamnetdb.info.hide();
      });
    });
  }, 500);
});

// -------------------------------------------------------------------------
// Open popup window to show extended information for an element
hamnetdb.info.open= function(q) {
  var win= window.open('index.cgi?q='+q,'hd',
        'width=800,height=600,scrollbars=yes');
  setTimeout(function() { 
    win.focus();
  }, 300);
}

// -------------------------------------------------------------------------
// Edit a particular element, maybe using default values
hamnetdb.edit= function(typ,id,fill) {
  if (fill === undefined) {
    fill= "";
  }
  var wname= typ+"_"+id;
  var geo= "width=800,height=600";
  if (typ=='site') {
    geo= "width=900,height=700";
  }
  var win= window.open('form_'+typ+'.cgi?id='+id+fill, 'edit_'+wname,
      geo+',menubar=no,scrollbars=yes,status=no,toolbar=no,resizable=yes');
  win.focus();
}

// -------------------------------------------------------------------------
// Open map as a popup Window
hamnetdb.openMap= function(fullscreen,as,site,hamnet) {
  var size= "width=800,height=700";
  var fs= "";
  if (fullscreen) {
    size= "width=4000,height=3000";
    fs= "fs";
  }
  var para= "";
  if (as>0) {
    para= "?as="+as;
  }
  else if (site!="") {
    para= "?site="+site;
  }
  var map= "map.cgi";
  if (hamnet) { //map-source=hamnet
    if(para != "")
    {
      para= para+"&source=3";
    }
    else
    {
      para= "?source=3";
    }
  }
  
  var win= window.open(map+para, 'hdmap'+fs,
    size+',menubar=no,scrollbars=no,status=no,toolbar=no,resizable=yes');
  win.focus();
}
//---------------------------------------------------------------------------
// Show antennapattern popup
hamnetdb.antennaShow= function(number, old){
  var oldparam = "";
  var name = document.getElementsByName("antennatype"+number)[0].value;
  var popup = document.getElementById('infoPopup');
  //create iframe
  popup.innerHTML= "<iframe class='infopopContent' style='height:0; border:0; background-color:#fff; height:100%; ' src=''>You need Iframes to see this content!</iframe>"+popup.innerHTML;
  
  var frm = popup.getElementsByTagName('iframe')[0];
  
  
  
  if(name == "")
  {
    window.alert("No antenna selected!");
  }
  else
  {
    if(old == 1)
    {
      oldparam = "&old=1"
    }
    popup.style.height = "370px";
    popup.style.width = "575px"
    frm.src = "antennapattern.cgi?name="+name+oldparam;
    //popup.style.visibility = "visible";
    frm.style.height = "370px";
    frm.style.width = "575px";
    jQuery("#infoPopup").css("right","auto");
    jQuery("#infoPopup").css("left","112px");
    jQuery("#infoPopup").css("top", "150px");
    jQuery("#infoPopup").fadeIn(300);
    
  }
}
//---------------------------------------------------------------------------
// Show position selection popup
hamnetdb.positionShow= function(number, old){
  var oldparam = "";
  var lat_popup = document.getElementById("latitude").value;
  var lon_popup = document.getElementById("longitude").value;
  var popup = document.getElementById('infoPopup');
  //create iframe
 

  popup.innerHTML= "<div class='infopopContent' style=\"font-size:15px;  margin-top:10px; margin-left:10px; display:block; float:left; width:470px;\" > \
    <a href=\"#\" onclick='hamnetdb.fullscreen(document.getElementById(\"map\"))'>fullscreen</a>&nbsp;&nbsp;\
    <span id='lat_to_store'></span>°&nbsp;&nbsp;<span id='lon_to_store'></span>° &nbsp;&nbsp<span id='locator_to_store'></span></div> \
    <div class='infopopContent' style=\"font-size:15px;  margin-top:10px;  display:block;\"> \
    <a href=\"javascript:hamnetdb.positionUse()\">use this position</a> &nbsp;&nbsp;&nbsp;&nbsp;<a href=\"javascript:hamnetdb.infopopHide()\">Cancel</a></div><div id='map' class='infopopContent'></div>"+popup.innerHTML;

  var frm = document.getElementById('map');
  
 
  popup.style.height = "450px";
  popup.style.width = "700px"
  //popup.style.visibility = "visible";
  frm.style.marginTop = "10px";
  frm.style.height = "100%";//"410px";
  frm.style.width = "100%";
  jQuery("#infoPopup").css("right","auto");
  jQuery("#infoPopup").css("left","45px");
  jQuery("#infoPopup").css("top", "80px");
  jQuery("#infoPopup").fadeIn(300);
  init(0,lat_popup,lon_popup);
}
hamnetdb.positionUse= function(){ 
  var lat = document.getElementById("lat_to_store").innerHTML;
  var lon = document.getElementById("lon_to_store").innerHTML;
  var locator = document.getElementById("locator_to_store").innerHTML;
  if(lat != "")
  {
    document.getElementById("latitude").value =  lat;
    document.getElementById("longitude").value = lon;
    document.getElementById("locator").value = locator;
    changed();
  }

  hamnetdb.infopopHide();
}
// -------------------------------------------------------------------------
//inline popup for antennapattern
hamnetdb.infopopHide= function(){
  
  var popup = document.getElementById('infoPopup');
  jQuery("#infoPopup").fadeOut(300);
  var frm =  popup.getElementsByClassName('infopopContent');
  var length = frm.length;
  for(i=length;i;i--)
  {
    frm[i-1].parentNode.removeChild(frm[i-1]);
  }
}

// -------------------------------------------------------------------------
//add UserAccess-line to form_site
hamnetdb.addUserAccess= function(number)
{

  //number is the index of the now added access

  if (number < 11)
  {
    var freq = 0;
    var az = 0;
    var al = 0;
    var tag = "";
    var power = 0;
    var gain = 0;
    var loss = 0;

    var next = number+1;

    var antenna = document.getElementsByName("antenna_dummy")[0].outerHTML;


    //text for new line of UserAccess
    var text="<td valign=\"top\" align=\"left\" nowrap width=\"90px\">&nbsp; &nbsp;  Tag:<br> \
            <a id=\"delete"+number+"\" href=\"javascript:hamnetdb.removeUserAccess("+number+")\"><img src=\"delete.png\"> </a>\
            <input type=\"text\" name=\"tag"+number+"\" value =\""+tag+"\"style=\"width:50px;\"$chtrack>  \
      </td> <td valign =\"top\" align =\"left\"nowrap width=\"110px\"> \
        Frequency: <br>\
        <input type=\"text\" name=\"frequency"+number+"\" value=\""+freq+"\" style=\"width:70px;\"$chtrack>MHz\
      </td> <td valign =\"top\" align =\"left\"nowrap> \
        Elevation <br>  \
        <input type=\"text\" name=\"altitude"+number+"\" value=\""+al+"\" style=\"width:60px;\"$chtrack>° \
      </td> <td valign =\"top\" align =\"left\"nowrap> \
        Azimuth:<br>\
        <input type=\"text\" name=\"azimuth"+number+"\" value=\"" +az+"\" style=\"width:60px;\"$chtrack>° \
      </td> <td valign =\"top\" align =\"left\"nowrap> \
        Power:<br>\
        <input type=\"text\" name=\"power"+number+"\" value=\""+power+"\" style=\"width:50px;\"$chtrack>dBm \
      </td> <td valign =\"top\" align =\"left\"nowrap> \
        Antennagain:<br> \
        <input type=\"text\" name=\"gain"+number+"\" value=\""+gain+"\" style=\"width:50px;\" $chtrack>dBi\
      </td> <td valign =\"top\" align =\"left\"nowrap> \
        Cableloss:<br> \
        <input type=\"text\" name=\"cableloss"+number+"\" value=\""+loss+"\" style=\"width:50px;\"$chtrack>dB</td> \
      <td valign =\"top\" align =\"left\"nowrap class=\"select_site_width\"> Antennatype <br>"+antenna+" \
        <a id = \"show"+number+"\" href=\"javascript:hamnetdb.antennaShow("+number+")\"><br \> Show selected Pattern </a></td>";


    document.getElementById('plusUser'+number).innerHTML+=text;
    document.getElementById('plusUser'+number).outerHTML+="<tr id =\"plusUser"+next+"\"></tr>";

    document.getElementById('menu').outerHTML= 
      "<tr id='menu'><td colspan=8>"+
      "<a href='javascript:hamnetdb.addUserAccess("+next+")'>"+
      "Add additional User Access / Antenna Configuration</a></td></tr>";

    document.getElementsByName("addAnt")[0].value++;
    document.getElementsByName("antenna_dummy")[1].setAttribute('name', "antennatype"+(number));
    changed();

  }

}

// -------------------------------------------------------------------------
//remove UserAccess-line to form_site
hamnetdb.removeUserAccess = function(index){

  var number= document.getElementsByName('addAnt')[0].value; //number of accesses
  var tiefer = number -1;

  //Alle Nummern kleiner als die zu löschende bleiben gleich, alle größeren werden um 1 reduziert.
  //Anzahl angezeigter Zugänge
  if(index >= 0)
  {
    if(index == (number-1)) 
    {
      document.getElementById('plusUser'+index).outerHTML="<tr id =\"plusUser"+index+"\"></tr>";

      var hightPlus = index+1;

      document.getElementById('menu').outerHTML = "<tr id =\"menu\" > <td colspan=2><a href=\"javascript:hamnetdb.addUserAccess(" + index +")\"> \
                                                   Add additional User Access/ Antenna Configuration </a><br></td></tr>";

      document.getElementById('plusUser'+hightPlus).outerHTML="";

      document.getElementsByName("addAnt")[0].value--;
      changed();
    }
    else{
      document.getElementById('plusUser'+index).outerHTML="";

      var i;
      for(i = index + 1; i < number; i++)
      {
        var neue= i-1;
        document.getElementsByName("frequency"+i)[0].setAttribute ("name","frequency"+neue);
        document.getElementsByName("azimuth"+i)[0].setAttribute("name","azimuth"+neue);
        document.getElementsByName("altitude"+i)[0].setAttribute ("name","altitude"+neue);
        document.getElementsByName("tag"+i)[0].setAttribute ("name","tag"+neue);
        document.getElementsByName("power"+i)[0].setAttribute ("name","power"+neue);
        document.getElementsByName("gain"+i)[0].setAttribute ("name","gain"+neue);
        document.getElementsByName("cableloss"+i)[0].setAttribute ("name","cableloss"+neue);

        document.getElementsByName("antennatype"+i)[0].setAttribute('name',"antennatype"+neue);

        document.getElementById('plusUser'+i).setAttribute ("id","plusUser"+neue);
        document.getElementById('delete'+i).outerHTML = "<a id=\"delete"+neue+"\" href=\"javascript:hamnetdb.removeUserAccess("+neue+")\"> <img src=\"delete.png\"> </a>";

        document.getElementById('show'+i).outerHTML="<a id = \"show"+neue+"\" href=\"javascript:hamnetdb.antenna("+neue+",'0')\"><br \> Show selected Pattern </a></td>";
      }
      document.getElementById('menu').outerHTML = "<tr id =\"menu\" > <td colspan=2><a href=\"javascript:hamnetdb.addUserAccess(" + (tiefer) +")\">\
                                                Add additional User Access/ Antenna Configuration </a><br></td></tr>";
      document.getElementById('plusUser'+i).outerHTML="<tr id =\"plusUser"+tiefer+"\"></tr>";
      document.getElementsByName("addAnt")[0].value--;
    }
    changed();
  }
}

//ip-calculator
hamnetdb.ipcalcShow= function(number, old){
  var oldparam = "";
  var popup = document.getElementById('infoPopup');
  //create iframe
  popup.innerHTML= "<iframe  style='height:0; border:0; background-color:#fff; height:100%; ' src=''>You need Iframes to see this content!</iframe>"+popup.innerHTML;
  
  popup.style.height = "260px";
  popup.style.width = "550px"
  
  var frm = popup.getElementsByTagName('iframe')[0];
  
  frm.src = "ip-calculator.html";
  //popup.style.visibility = "visible";
  frm.style.height = "260px";
  frm.style.width = "550px";
  jQuery("#infoPopup").css("right","auto");
  jQuery("#infoPopup").css("left","112px");
  jQuery("#infoPopup").css("top", "250px");
  jQuery("#infoPopup").fadeIn(600);
}
hamnetdb.fullscreen= function(elem)
{
  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.msRequestFullscreen) {
    elem.msRequestFullscreen();
  } else if (elem.mozRequestFullScreen) {
    elem.mozRequestFullScreen();
  } else if (elem.webkitRequestFullscreen) {
    elem.webkitRequestFullscreen();
  }
}
