// -------------------------------------------------------------------------
// Hamnet IP database - Map processing - JavaScript parts
//
// Flori Radlherr, DL8MBT, http://www.radlherr.de
//
// Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
// http://creativecommons.org/licenses/by-nc-sa/3.0/
// - you may change, distribute and use in non-commecial projects
// - you must leave author and license conditions
// -------------------------------------------------------------------------
//
// -------------------------------------------------------------------------
// Some variables used for map rendering
mapwindow= new Object;
mapwindow.elements= new Array;
mapwindow.map= null;
mapwindow.centerLat= 50.5;
mapwindow.centerLong= 10.0;
mapwindow.zoom= 6;
mapwindow.siteCount= 0;
mapwindow.scrollwheel= true;
mapwindow.shallShow= false;
mapwindow.as= 0;
mapwindow.site= "";
mapwindow.country= "";
mapwindow.onlyHamnet= false;
mapwindow.noTunnel= false;
mapwindow.fitBounds= true;

// -------------------------------------------------------------------------
// Initialize google map
mapwindow.open= function () {
  if (mapwindow.shallShow) {
    mapwindow.map= 
      new google.maps.Map(document.getElementById("map_canvas"), {
      zoom: mapwindow.zoom,
      center: new google.maps.LatLng(mapwindow.centerLat,
                                     mapwindow.centerLong),
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      scrollwheel: mapwindow.scrollwheel
    });
    mapwindow.load();
  }
}

// -------------------------------------------------------------------------
// Load network elements into the map
mapwindow.load= function() {
  var maxLat= (-180);
  var maxLong= (-180);
  var minLat= (180);
  var minLong= (180);

  for (var i= 0; i<mapwindow.elements.length; i++) {
    mapwindow.elements[i].setMap(null);
  }
  mapwindow.elements= new Array;
  mapwindow.siteCount= 0;

  var filter= "";
  if (mapwindow.country!= "") {
    filter= "?only_country="+mapwindow.country;
  }

  jQuery.getJSON("mapelements.cgi"+filter, function(data) {
    for (var i= 0; i<data.site.length; i++) {
      var site= data.site[i];
      if (mapwindow.country!="" && mapwindow.country!=site.country) {
        site.useBounds= false;
      }
      if (mapwindow.as>0 && mapwindow.as!=site.as) {
        site.useBounds= false;
      }
      if (mapwindow.site!="" && mapwindow.site!=site.callsign) {
        site.useBounds= false;
      }
      if (mapwindow.onlyHamnet && !site.hasHamnet) {
        continue;
      }
      if (site.useBounds) {
        mapwindow.siteCount++;
        if (site.latitude>maxLat) maxLat= site.latitude;
        if (site.latitude<minLat) minLat= site.latitude;
        if (site.longitude>maxLong) maxLong= site.longitude;
        if (site.longitude<minLong) minLong= site.longitude;
      }

      var pos= new google.maps.LatLng(site.latitude,site.longitude);

      mapwindow.elements[mapwindow.elements.length]= 
        new google.maps.Marker({ 
        map: mapwindow.map,
        position: pos,
        icon: site.icon,
        zIndex: site.zIndex
      });
      var e= mapwindow.elements[mapwindow.elements.length-1];
      e.link= site.callsign;
      e.info= site.callsign;

      google.maps.event.addListener(e, 'click', function() {
        hamnetdb.info.open(this.link);
      });
      google.maps.event.addListener(e, 'mouseover', function() {
        hamnetdb.info.show(this.info)
      });
      google.maps.event.addListener(e, 'mouseout', 
        hamnetdb.info.hide
      );
    }
    for (i= 0; i<data.edge.length; i++) {
      var edge= data.edge[i];
      if (false) {
      if (mapwindow.as>0 && 
         (mapwindow.as!=edge.left.as ||
          mapwindow.as!=edge.right.as)) {
        continue;
      }
      if (mapwindow.site!="" &&
          mapwindow.site!=edge.left.site && 
          mapwindow.site!=edge.right.site) {
        continue;
      }
      }
      var stroke= 8;
      var col= "#0086db";
      if (edge.typ.match(/Tunnel/)) {
        stroke= 4;
        col= "#a0a0a0";
        if (mapwindow.noTunnel) {
          continue;
        }
      }
      mapwindow.elements[mapwindow.elements.length]= 
        new google.maps.Polyline({
         path: [
           new google.maps.LatLng(edge.left.latitude,edge.left.longitude),
           new google.maps.LatLng(edge.right.latitude,edge.right.longitude)
         ],
         strokeColor: col,
         strokeOpacity: 0.4,
         strokeWeight: stroke
      });
      var e= mapwindow.elements[mapwindow.elements.length-1];
      e.setMap(mapwindow.map);
      e.link= edge.link;
      e.info= edge.left.site+":"+edge.right.site;

      google.maps.event.addListener(e, 'click', function() {
        hamnetdb.info.open(this.link);
      });
      google.maps.event.addListener(e, 'mouseover', function() {
        hamnetdb.info.show(this.info)
      });
      google.maps.event.addListener(e, 'mouseout', 
        hamnetdb.info.hide
      );
    }
    if (mapwindow.fitBounds) {
      if (mapwindow.siteCount>1) {
        var southWest= new google.maps.LatLng(minLat,minLong);
        var northEast= new google.maps.LatLng(maxLat,maxLong);
        var bounds= new google.maps.LatLngBounds(southWest,northEast);
        mapwindow.map.fitBounds(bounds);
      }
      if (mapwindow.siteCount==1) {
        var coord= new google.maps.LatLng(minLat,minLong);
        mapwindow.map.setCenter(coord);
        mapwindow.map.setZoom(12);
      }
      mapwindow.fitBounds= false;
      mapwindow.site= "";          // honour site only the first time
    }
  });
}

// -------------------------------------------------------------------------
// Redraw network elements when control panel has issued a change
mapwindow.panelChange= function() {
  var as= document.mapcont.as;
  var newAs= as.options[as.selectedIndex].value;
  if (newAs == "-All-") {
    newAs= 0;
  }
  if (newAs != mapwindow.as) {
    mapwindow.as= newAs;
    mapwindow.fitBounds= true;
  }
  mapwindow.onlyHamnet= document.mapcont.onlyHamnet.checked;
  mapwindow.noTunnel= document.mapcont.noTunnel.checked;
  mapwindow.load();
}

// -------------------------------------------------------------------------
// Show and hide symbol legend
mapwindow.legendChange= function() {
  if (document.mapcont.showLegend.checked) {
    jQuery("#map_legend").fadeIn(500);
  }
  else {
    jQuery("#map_legend").fadeOut(500);
  }
}

// -------------------------------------------------------------------------
// Show control panel when entering mouse
mapwindow.panelOver= function() {
  jQuery("#map_control").css("height", "auto");
  jQuery("#map_control").css("width", "auto");
  clearTimeout(mapwindow.paneltimer);
}

// -------------------------------------------------------------------------
// Hide the control panel after some time when mouse is out
mapwindow.panelOut= function() {
  mapwindow.paneltimer= setTimeout(function() {
    jQuery("#map_control").css("height", "18px")
    jQuery("#map_control").css("width", "140px")
  }, 5000);
}

// -------------------------------------------------------------------------
// Let the map run, if necessary
jQuery(document).ready(function() {
  setTimeout(mapwindow.open, 500);
});

