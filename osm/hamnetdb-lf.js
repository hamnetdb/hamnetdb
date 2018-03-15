// -------------------------------------------------------------------------
// Hamnet IP database - JavaScript parts
//
// Lucas Speckbacher, OE2LSP
// Hubertus Munz
//
//
// Licensed with Creative Commons Attribution-NonCommercial-ShareAlike 3.0
// http://creativecommons.org/licenses/by-nc-sa/3.0/
// - you may change, distribute and use in non-commecial projects
// - you must leave author and license conditions
// -------------------------------------------------------------------------
//


//todo
//OK- KML.js anpassen beim Popupladen inhalt nachladen
//OK- hover
//OK- custom element in map darstellen (info, settings)
//OK- info übernehmen
//OK- mobile
//OK- perl mapsource
//OK- perl position
//OK- perl hover

var map;
var layers;
var SidebarInfo;
var SidebarSetting;
var SidebarRftools;
var hoverpop;
var kmlUrl = "mapelements.cgi?geojson=1&rnd="+Math.random();

var CoverUrl = "coverage/";
var CoverageLayers = new Array();
var GreenCover = new L.layerGroup();

var profileFrecuency = 5800;
var profileWood = 30;
var profileFont = 1;
var profileTowerDefault = 10;
var profileLabelA = "";
var profileLabelB = "";
var profileTowerA = profileTowerDefault;
var profileTowerB = profileTowerDefault;
var profileMa;
var profileMb;
var profileLine;
var profilePopup;

var rfRect;
var rfMark = null;
var rfTowerRx = 0;
var rfMarkerA;
var rfMarkerB;
var rfTiles;
var rfLayer;
var rfLocked = 0;
var rfUp = 0;
var rfLeft = 0;
var rfDown = 0;
var rfRight = 0;

var testg;

function init()
{  
  //get page parameters
  var source = getParameter("source");
  hoverpop = getParameter("hover");
  var country = getParameter("country");
  var as = getParameter("as");
  var site = getParameter("site");
  var ma_lat = getParameter("ma_lat");
  var ma_lon = getParameter("ma_lon");
  var mb_lat = getParameter("mb_lat");
  var mb_lon = getParameter("mb_lon");
  profileTowerA = getParameter("ma_tow");
  profileTowerB = getParameter("mb_tow");
  profileLabelA = getParameter("ma_lab");
  profileLabelB = getParameter("mb_lab");
  var profileFontTmp = getParameter("font");
  rfTowerRx = getParameter("rf_rx");
  rfLabel = getParameter('rf_lab');
  rect_up = getParameter("rf_u");
  rect_left = getParameter("rf_l");
  rect_down = getParameter("rf_d");
  rect_right = getParameter("rf_r");
  rf_vis = getParameter("rf_vis");
  rfRefractiontmp = getParameter("rf_ref");

  if(rfRefractiontmp != 0) { //0 is "0.0"
    rfRefraction = rfRefraction;
  }
  if (profileTowerA == 0) {
    profileTowerA = profileTowerDefault;
  }
  if (profileTowerB == 0) {
    profileTowerB = profileTowerDefault;
  }
  if (profileLabelA == 0) {
    profileLabelA = "";
  }
  if (profileLabelB == 0) {
    profileLabelB = "";
  }
  if (profileFontTmp != 0) {
    profileFont = profileFontTmp;
  }

  var CoverUrl= "coverage/";
  if (country && country.length==2) {
    kmlUrl+= "&only_country="+country;
  }
  if(source == 3)//hamnet
  {
    var mapnikUrl = 'http://osm.oe2xzr.ampr.at/osm/tiles/{z}/{x}/{y}.png';
    var mapnikUrl1 = 'http://karten.db0sda.ampr.org/osm/{z}/{x}/{y}.png';
    var landscapeUrl = 'http://osm.oe2xzr.ampr.at/osm/tiles_topo/{z}/{x}/{y}.png';
    var cycleUrl = 'http://osm.oe2xzr.ampr.at/osm/tiles_cyclemap/{z}/{x}/{y}.pn';
    var satUrl= 'http://osm.oe2xzr.ampr.at/osm/tiles_sat/{z}/{x}/{y}.jpg';
    var mapnikZoom = 16 ; 
    var landscapeZoom =16;
    var cycleZoom = 16;
    var satZoom = 11;
  }
  else
  {
    var mapnikUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var landscapeUrl = 'https://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=4ccd4e27d3a1419fb33801754a62191b';
    var cycleUrl = 'https://{s}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png?apikey=4ccd4e27d3a1419fb33801754a62191b';
    var outdoorUrl = 'https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=4ccd4e27d3a1419fb33801754a62191b';
    var opentopoURL = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png';
    var mapnikZoom = 18;
    var landscapeZoom = 18;
    var outdoorZoom = 18;
    var cycleZoom = 18;
    var opentopoZoom = 17;
  }
  
  var attribution = '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'; 
  map = new L.Map('map', 
    {center: new L.LatLng(49.26, 12.47), 
    zoom: 7, 
    zoomControl:false,
    contextmenu: true,
      contextmenuWidth: 160,
        contextmenuItems: [
        {
          text: 'place Profile "From"',
          callback: placeProfileFrom
        }, '-', {
          text: 'place Profile "To"',
          callback: placeProfileTo
        }
    ]});
  //plugin MousePosition
  L.control.mousePosition({position: 'bottomright'}).addTo(map);
  //plugin Minimap
  var miniMapnik = new L.TileLayer(mapnikUrl, {minZoom: 0, maxZoom: 13, attribution: " " });
  var miniMap = new L.Control.MiniMap(miniMapnik, { toggleDisplay: true }).addTo(map);
  miniMap._minimize();
  //zoombutton top right
  L.control.zoom({position: 'topright'}).addTo(map);
  //scale
  L.control.scale().addTo(map);
  
  var mapnikLayer = L.tileLayer(
    mapnikUrl,
    {
      attribution: attribution,
      maxZoom: mapnikZoom
    }
  )

  var landscapeLayer = L.tileLayer(
   landscapeUrl,
    {
      attribution: attribution,
      maxZoom: landscapeZoom
    }
  );
  var cycleLayer = L.tileLayer(
    cycleUrl,
    {
      attribution: attribution,
      maxZoom: cycleZoom
    }
  );
  var outdoorLayer = L.tileLayer(
    outdoorUrl,
    {
      attribution: attribution,
      maxZoom: outdoorZoom
    }
  );
  var openttopoLayer = L.tileLayer(
    opentopoURL,
    {
      attribution: attribution,
      maxZoom: satZoom
    }
  );

	if(source == 3)
	{
    var mapnikLayer1 = L.tileLayer(
      mapnikUrl1,
      {
        attribution: attribution,
        maxZoom: mapnikZoom
      }
    );
    var satLayer = L.tileLayer(
      satUrl,
      {
        attribution: attribution,
        maxZoom: satZoom
      }
    );
	}
	
  if(hoverpop == "true")
  {
    var hoverS = true;
  }
  else
  {
    var hoverS = false;
  }
  //var hamnetLayer = new L.KML(kmlUrl + "&no_tunnel=1&only_hamnet=1", {async: true, hover:hoverS});
  var settingshamnet = {
    style: function(feature) {
      var color, weight, opacity;
      switch (feature.properties.style)
      {
        case "Tunnel":
          color = "#808080";
          weight = 3.5;
          opacity= 0.5; 
          break;
        case "Routing-Radio":
          color = "#1d97ff";
          weight = 6;
          opacity= 0.5;
          break;        
        case "Routing-Tunnel":
          color = "#808080";
          weight = 3.5;
          opacity= 0.5;
          break;
        case "Radio":
          color = "#1d97ff";
          weight = 6;
          opacity= 0.5;
          zIndex = 400;
          break;
        case "Routing-ISM":
          color = "#ad00e1";
          weight = 6;
          opacity= 0.5;
          zIndex = 400;
          break;
        case "Routing-Ethernet":
          color = "#808080";
          weight = 3.5;
          opacity= 0.5;
          break;
        case "ISM":
          color = "#ad00e1";//d800ff
          weight = 6;
          opacity= 0.85
          zIndex = 400;
          break;
        case "hf1":
          color = "#5dff00";//green
          weight = 6;
          opacity= 0.8;
          break;
        case "hf2":
          color = "#a2ff00";//green-yellow
          weight = 6;
          opacity= 0.8;
          break;
        case "hf3":
          color = "#f1ff00";//yellow
          weight = 6;
          opacity= 0.8;
          break;
        case "hf4":
          color = "#ffde00";//bright-orange
          weight = 6;
          opacity= 0.8;
          break;
        case "hf5":
          color = "#ffa700";//dark-orange
          weight = 6;
          opacity= 0.8;
          break;
        case "hf6":
          color = "#ff000d";//red
          weight = 6;
          opacity= 0.8;
          break;
        case "hf7":
          color = "#ff000d";//red
          weight = 6;
          opacity= 0.8;
          break;
        default:
          color = "#808080";
          weight = 6;
          opacity= 0.5;
      }
      return {color: color, weight:weight, opacity:opacity};//feature.properties.GPSUserColor};
    },
    pointToLayer: function(feature, latlng) {
      return L.marker(latlng, {
        icon: L.icon({
          iconUrl: feature.properties.style+'.png',
          iconSize: [19, 25],
          iconAnchor: [10, 16],
          popupAnchor: [0, 0]
        }),
        contextmenu: true,
        contextmenuItems: [
        {
          text: 'snap "From" to '+feature.properties.callsign,
          callback: function () {
            if (typeof feature !== 'undefined')
            {
              loc= new L.LatLng(feature.geometry.coordinates[1],feature.geometry.coordinates[0])
              profileLabelA = feature.properties.callsign;
              profileTowerA = feature.properties.anthight;
              placeProfileFrom(loc);
              profilePopupUpd();
           }
          }
        },
        {
          text: 'snap "To" to '+feature.properties.callsign,
          callback: function () { 
            loc= new L.LatLng(feature.geometry.coordinates[1],feature.geometry.coordinates[0])
            profileLabelB = feature.properties.callsign;
            profileTowerB = feature.properties.anthight;
            placeProfileTo(loc);
            profilePopupUpd();
          }
        }],
      });

    },
    onEachFeature: function (feature, layer) {
    layer.bindPopup("<div class=\"popup\" ><div id=\"pop_"+feature.properties.callsign+"\">loading...<div id=\"pop_alloc\">&nbsp;</div></div>\
      <a href=\"index.cgi?q=" + feature.properties.callsign + "\" target=\"_blank\" onclick=\"return popupw(this.href);\">more information</a></div>\
      <br> <div id=\"ShowCover\"><b> Display Coverage:</b>\
      <br>press info-button for legend\
      <form action=\"\" id=\"displayCoverage\" >\
      <input name=\"Coverage\" type=\"checkbox\" name=\""+ feature.properties.callsign +"\"  onchange=\"coverage(event)\" \"> </form> </div>",
        {
          minWidth:250,
          maxWidth:260,
          maxHeight:250,
          popupClass: '',
          popupValidity: 100,
          autoPan:!hoverpop  //don't move popup if hoverpop
        });
      layer.on('popupopen', function (e) {
        getHttpRequest("info.cgi?q=" + feature.properties.callsign,"pop_"+feature.properties.callsign );
	 
        if( feature.geometry.type== "LineString")
        {   // TunnelLayer has no Coverage
      	  document.getElementById("ShowCover").outerHTML = "";
        }
        else
        {	// set Checkbox grey if no Coverage Layer available in DB; 	 	
          getCoverage("mapcoverage.cgi?x="+feature.properties.callsign,1);
        }
        if(feature.properties.callsign.match(':')) //link not site
        {
          document.getElementById("ShowCover").style.visibility = "hidden";
        }
        else //site
        {
          document.getElementById("ShowCover").style.visibility = "visible";
          document.getElementsByName("Coverage")[0].style.visibility = "hidden";   
        }
	    
      });
      if(hoverpop == "true")
      {
        layer.on('mouseover', function (e){
          layer.openPopup();
        });
      }
      layer.options.zIndex = index

    }  

  };
  index=300;
  offset=-4000
  var hamnetLayer = new L.GeoJSON.AJAX(kmlUrl + "&no_tunnel=1&only_hamnet=1",settingshamnet);
  index=500;
  offset=3000;
  var hamnetmonitorLayer = new L.GeoJSON.AJAX(kmlUrl + "&no_tunnel=1&only_hamnet=1&radio=1",settingshamnet);
  var nohamnetLayer = new L.GeoJSON.AJAX(kmlUrl + "&no_tunnel=1&no_radio=1&no_hamnet=1&no_ism=1", settingshamnet);
  var tunnelLayer = new L.GeoJSON.AJAX(kmlUrl + "&no_radio=1&only_hamnet=1&no_hamnet=1&no_ism=1", settingshamnet);
  hamnetLayer.on('add', function (e) {
    hamnetLayer.bringToBack()
  });
  nohamnetLayer.on('add', function (e) {
    nohamnetLayer.bringToBack()
  });
  tunnelLayer.on('add', function (e) {
    tunnelLayer.bringToBack()
  });



  map.addLayer(hamnetLayer);
  //map.addLayer(nohamnetLayer);
  //map.addLayer(tunnelLayer);
  map.addLayer(mapnikLayer);

  GreenCover.addTo(map);
  //check if google-lib is loaded 
  if (typeof google === 'undefined' && source <=1) {
    source = 2;
  }

  if(source <=1)
  {
    var roadMutant = L.gridLayer.googleMutant({
      maxZoom: 24,
      type:'roadmap'
    });
    var satMutant = L.gridLayer.googleMutant({
      maxZoom: 24,
      type:'satellite'
    });
    var terrainMutant = L.gridLayer.googleMutant({
      maxZoom: 24,
      type:'terrain'
    });
    var hybridMutant = L.gridLayer.googleMutant({
      maxZoom: 24,
      type:'hybrid'
    });
    //var gglLayer = new L.Google('ROADMAP');
    //var ggl2Layer = new L.Google('TERRAIN');
    //var ggl3Layer = new L.Google('SATELLITE');
    var baseLayers = {  
      'Mapnik': mapnikLayer,
      'Landscape': landscapeLayer,
      'CycleMap':cycleLayer,
      'Outdoor':outdoorLayer, 
      'OpenTopo':openttopoLayer,
      'GoogleMaps': roadMutant,
      'Google Terrain': terrainMutant,
      'Google Satellite': satMutant,
      'Google Hybrid': hybridMutant
    };
  }
  else if(source == 3)
  {
    var baseLayers = {  
      'Mapnik': mapnikLayer,
      'Mapnik Mirror1': mapnikLayer1,//aachen
      'Landscape': landscapeLayer,
      'CycleMap':cycleLayer,
      'Satellite':satLayer
    };
  }
  else //  ==2
  {
    var baseLayers = {  
      'Mapnik': mapnikLayer,
      'Landscape': landscapeLayer,
      'CycleMap':cycleLayer,
      'Outdoor':outdoorLayer,
      'OpenTopo':openttopoLayer,
    };
  }
  
  var overlayLayers = {
    'Hamnet': hamnetLayer,
    'Hamnet RSSI': hamnetmonitorLayer,
    'tunnel connections': tunnelLayer,
    'sites without Hamnet': nohamnetLayer,
  };
  layers = new L.control.layers(baseLayers, overlayLayers).addTo(map);
  var permalink = new L.Control.Permalink({text: 'Permalink', layers: layers});
  permalink._map = map;
  var extPermalink = permalink.onAdd(map);
    //  window.history.pushState("", "HamnetDB Map", url);//add by OE2LSP (end of _update_href)
  document.getElementById('extern-permalink').appendChild(extPermalink);
  document.getElementById('extern-permalink-rf').appendChild(extPermalink);
  SidebarInfo = L.control.sidebar('sidebar-info', {
    position: 'right'
  });  
  SidebarInfo.addTo(map);
  
  SidebarSetting = L.control.sidebar('sidebar-setting',{
  	position: 'right'
  });
  SidebarSetting.addTo(map);
  SidebarRftools = L.control.sidebar('sidebar-rftools',{
    position: 'right'
  });
  SidebarRftools.addTo(map);
  map.addControl(new L.Control.LSP());

  //if as is set over GET
  if(as != 0)
    getAs(as); 
  if(site != 0)
    getSite(site); 
 // map.setView([51.2, 7], 9);

  //Profile init
  if ((ma_lat!=0) && (ma_lon!=0) && (mb_lat!=0) && (mb_lon!=0) && rf_vis == 0)
  {
    ma = new L.LatLng(ma_lat, ma_lon);
    mb = new L.LatLng(mb_lat, mb_lon);
    drawFrom(ma);
    drawTo(mb);
    if (rf_vis == 0) 
    {
      profileProceed();
      profileDraw();
    }
    map.setView([((Number(ma_lon)+Number(ma_lon))/2), ((Number(ma_lat)+Number(mb_lat))/2)], 9);
    //map.setZoom(9);
  }
  // if visibility is set
  if (rf_vis) {
    if(rect_up != 0 && rect_right != 0 && rect_down != 0 && rect_right != 0) 
    {
      rfUp = rect_up;
      rfLeft = rect_left;
      rfDown = rect_down;
      rfRight = rect_right;
    }
    if((ma_lat!=0) && (ma_lon!=0))
    {
      ma = new L.LatLng(ma_lat, ma_lon);
      drawFrom(ma);
    }
    if((mb_lat!=0) && (mb_lon!=0))
    {
      mb = new L.LatLng(mb_lat, mb_lon);
      drawTo(mb);
    }

    rfCalc(1);
    SidebarRftools.toggle();
  }
}
function placeProfileFrom (e) {
  if (typeof e.latlng !== 'undefined') 
  {
    e=e.latlng
  }
  deleteProfileMa();
  drawFrom(e);
  profileProceed();
} 
function placeProfileTo (e) {
  if (typeof e.latlng !== 'undefined') 
  {
    e=e.latlng
  }
  deleteProfileMb();
  drawTo(e);
  profileProceed();
} 
function drawFrom(latlng)
{
  profileMa = L.marker(latlng, {
    icon: L.icon({
        iconUrl: 'osm/images/marker-red.png',
        iconSize: [17, 25],
        iconAnchor: [8, 25],
        popupAnchor: [0, 0],
        zIndex: 9997,
        //zIndexOffset: 3000,
      }),
    draggable: true,
    contextmenu: true,
    contextmenuItems: [
      {
        text: 'calculate p2p-Profile',
        callback: function (e) { 
          profileDraw() ;}
      },
      {
        text: 'delete From',
        callback: function (e) { 
          profileLabelA = "";
          profileTowerA = profileTowerDefault;
          deleteProfileLine(); 
          map.removeLayer(profileMa);
        }
      },
      {
        text: 'delete all',
        callback: function (e) { 
          profileTowerA = profileTowerDefault;
          profileTowerB = profileTowerDefault;
          deleteProfileAll();
          map.removeLayer(profileMa);
        }
      }
    ]
  }).addTo(map);
  profileMa.setZIndexOffset(7000);
  profileMa.on("dragend", function(e){profileProceed();});
  profileMa.on("click", function(e){profileDraw();});
  profileProceed()
}
function drawTo(latlng)
{
  profileMb = L.marker(latlng, {
    icon: L.icon({
        iconUrl: 'osm/images/marker-red.png',
        iconSize: [17, 25],
        iconAnchor: [8, 25],
        popupAnchor: [0, 0],
        zIndex: 9996,
        //zIndexOffset: 3000,
      }),
    draggable: true,
    contextmenu: true,
    contextmenuItems: [
      {
        text: 'calculate p2p-Profile',
        callback: function (e) { 
          profileDraw() ;}
      },
      {
        text: 'delete To',
        callback: function (e) { 
            profileLabelB = "";
            profileTowerB = profileTowerDefault;
            deleteProfileLine();
            map.removeLayer(profileMb); 
          }
      },
      {
        text: 'delete all',
        callback: function (e) { 
          profileTowerA = profileTowerDefault;
          profileTowerB = profileTowerDefault;
          deleteProfileAll();
          map.removeLayer(profileMb); 
        }
      }  
    ]
  }).addTo(map);
  profileMb.setZIndexOffset(7000);
  profileMb.on("dragend", function(e){profileProceed();});
  profileMb.on("click", function(e) {profileDraw();});
  profileProceed()
}
function profileProceed()
{
  document.getElementById('side-draw-del-point1').style.display="inline"
  document.getElementById('side-draw-del-point2').style.display="inline"
  if ((typeof profileMa !== 'undefined') &&(typeof profileMb !== 'undefined')) {
  
    if((profileMa._icon != null) && (profileMb._icon != null))
    {
      deleteProfileLine();
      var pointList = [profileMa._latlng, profileMb._latlng];
      profileLine = new L.Polyline(pointList, {
        color: 'red',
        weight: 3,
        opacity: 0.9,
        smoothFactor: 1,
        zIndex:9994,
      });
      profileLine.addTo(map);
      profileLine.on("click", function(e) {profileDraw();});
      if (map.hasLayer(profilePopup)){
        document.getElementById("popup-updated").style.border= "3px solid red"
      }
    }
  }
}
function deleteProfileLine() {
  if (typeof profileLine !== 'undefined')
  {
   if(profileLine._map != null)
   {
     map.removeLayer(profileLine);
   }
  };
}
function deleteProfileMa() {
  if (typeof profileMa !== 'undefined') {
    map.removeLayer(profileMa);
  }
}
function deleteProfileMb() {
  if (typeof profileMb !== 'undefined') {
    map.removeLayer(profileMb);
  }
}
function deleteProfileAll() {
  profileLabelA = "";
  profileLabelB = "";
  deleteProfileLine(); 
  deleteProfileMa();
  map.removeLayer(profileMb);
  document.getElementById('side-draw-del-point1').style.display="none"
  document.getElementById('side-draw-del-point2').style.display="none"
}
//profile Popup content
function profileDraw () {
  width = 650;
  height = 350;
  if ((typeof profileMa !== 'undefined') && (typeof profileMb !== 'undefined')) {
    if((profileMa._latlng != null) && (profileMb._latlng != null)) {
      if (typeof profilePopup !== 'undefined') { //catch open popup
        if (profilePopup._map !=null) {
          profileRedraw(width,height);
          return;
        }
      }

      var lat1 = profileMa._latlng['lat'];
      var lon1 = profileMa._latlng['lng'];
      var lat2 = profileMb._latlng['lat'];
      var lon2 = profileMb._latlng['lng'];
      var customOptions ={
        className: 'popuppprofile',
        minWidth:550,
        maxWidth:550,
        maxHeight:250,
      }
      profilelink=profileGenLink(width,height);
      if (profileFont <= 1) {
        fontSelected1 = "selected";
        fontSelected2 = "";
        fontSelected3 = "";
      } else if (profileFont == 2) {
        fontSelected1 = "";
        fontSelected2 = "selected";
        fontSelected3 = "";
      } else if (profileFont == 3) {
        fontSelected1 = "";
        fontSelected2 = "";
        fontSelected3 = "selected";
      }

      var popupcontent="<span class='popup-darg'>drag and drop popup and markers</span> \
        <img id='proifleimg' src='"+profilelink+"' style='font-size:40px;' alt='loading...'/>\
        <p><form id='profile'>&nbsp;&nbsp;\
        <b>tower size \"From\"<input id='towera' value='"+profileTowerA+"' size='3' style='width:22px' \
        onchange='profileValUpd();'/>m</b>&nbsp;&nbsp;\
        label \"From\"<input id='labela' value='"+profileLabelA+"' size='30' style='width:57px \
        'onchange='profileValUpd();'/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
        label \"To\"<input id='labelb' value='"+profileLabelB+"' size='30' style='width:57px' \
        onchange='profileValUpd();'/>&nbsp;&nbsp;\
        <b>tower size \"To\"<input id='towerb' value='"+profileTowerB+"' size='3' style='width:22px'\
        onchange='profileValUpd();'>m</b><br>\
        &nbsp;&nbsp;&nbsp;frequency:\
        <input id='frequency' type='text' value='"+profileFrecuency+"' size='6' style='width:40px' \
        onchange='profileValUpd();'/>\
        (MHz) &nbsp;treesize:<input id='wood' type='text' value='"+profileWood+"' size='3' style='width:18px' \
        onchange='profileValUpd();'/>\
        0...100m &nbsp;&nbsp;font size<select id='fontsize' onchange='profileValUpd();'>\
        <option value='1' "+fontSelected1+">10</option><option value='2' "+fontSelected2+">14</option>\
        <option value='3' "+fontSelected3+">20</option></select> \
        <span id='popup-updated'><input type='button' value='recalculate' style='height:24px' onclick='javascript:profileRedraw("+width+","+height+");' ></span>\
        &nbsp;&nbsp;<input type='button' value='open big Profile' \
        style='height:24px' onclick='javascript:profileOpenBig();'></form>\
         &nbsp &nbsp\</p>";


      profilePopup = L.popup({
        closeButton: true,
        closeOnClick:false,
        autoClose: false,
        className: 'popupProfile', 
        minWidth: width,
        //maxWidth: 650,
        Width: width,
        Height: (height+70),
      })
      .setLatLng([(lat1 + lat2)/2, (lon1+lon2)/2])
      .setContent(popupcontent)
      .openOn(map);
    
      map.addLayer(profilePopup);

      var pos = map.latLngToLayerPoint(profilePopup._latlng);
      L.DomUtil.setPosition(profilePopup._wrapper.parentNode,pos);
      var draggable = new L.Draggable(profilePopup._container, profilePopup._wrapper);
      draggable.enable();
      map.panTo(pos)
    }
  }
}
function profilePopupUpd()
{
  document.getElementById("labela").value = profileLabelA; 
  document.getElementById("labelb").value = profileLabelB; 
  document.getElementById("towera").value = profileTowerA; 
  document.getElementById("towerb").value = profileTowerB; 
}
function profileValUpd()
{
  profileLabelA = document.getElementById("labela").value; 
  profileLabelB = document.getElementById("labelb").value; 
  profileTowerA = document.getElementById("towera").value; 
  profileTowerB = document.getElementById("towerb").value; 
  profileFrecuency = document.getElementById("frequency").value; 
  profileWood = document.getElementById("wood").value; 
  profileFont = document.getElementById("fontsize").value; 
  rfUpdForm();
}
function profileRedraw(width,height)
{
  //set proifleimg src
  var src = profileGenLink(width,height);
  document.getElementById("proifleimg").src = src;
  document.getElementById("popup-updated").style.border= "0px";
}
function profileOpenBig()
{
  //get window size
  var height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
  var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
  var src = profileGenLink(width,height);
  //open new window
  window.open(src, '_blank');
}
function profileGenLink(width,height)
{
  var lat1 = profileMa._latlng['lat'];
  var lon1 = profileMa._latlng['lng'];
  var lat2 = profileMb._latlng['lat'];
  var lon2 = profileMb._latlng['lng'];

  src="https://hamnetdb.net/calc_profile.cgi?f="+profileFrecuency+"&lon_a="+
        lon1+"&lat_a="+lat1+"&ant_a="+profileTowerA+"&name_a=\""+profileLabelA+
        "\"&lon_b="+lon2+"&lat_b="+lat2+"&ant_b="+profileTowerB+"&name_b=\""+profileLabelB+
        "\"&wood="+profileWood+"&font="+profileFont+"&h="+height+"&w="+width; 
  return src;
} 
function popupSetting()
{
  var pop = document.getElementById("hoverpopup").checked;
  setGetParameter('hover',pop,true);
}
function rfPlacemarker()
{
  if(rfMark !== null) {
    rfMark.disable();
    rfMark = null;
  }
  else
  {
    rfMark= new L.Draw.Marker(map);
    rfMark.enable();
    map.on('draw:created',rfPlaceA);
  }
}
function rfPlaceA(e)
{
  map.off('draw:created',rfPlaceA);
  var coord;
  coord = {latlng: e.layer._latlng};
  placeProfileFrom(coord);
  rfMark= new L.Draw.Marker(map);
  rfMark.enable();
  map.on('draw:created',rfPlaceB);
}
function rfPlaceB(e)
{
  map.off('draw:created',rfPlaceB);
  var coord;
  coord = {latlng: e.layer._latlng};
  placeProfileTo(coord);
  rfMark = null;
}
function rfOpenprofile()
{
  if (map.hasLayer(profileMa) && map.hasLayer(profileMb)) {
    if((profileMa._latlng != null) && (profileMb._latlng != null)) {
      profileDraw();
    }
    else
      alert("At least one marker missing!");
  }
  else
    alert("At least one marker missing!");
}
function rfRectangle()
{
  var rect= new L.Draw.Rectangle(map,{shapeOptions:{color:'#F00',fill:false}});
  rect.enable();
  map.on('draw:created',rfRectangleFinish)
}
function rfDelRectangle()
{
  if (map.hasLayer(rfRect)) 
  {
    rfRect.removeFrom(map);
    map.removeLayer(rfRect); 
  }
  document.getElementById('side-draw-del-rect').style.display="none";
}
function rfRectangleFinish(e) {
  if (map.hasLayer(rfRect)) {
    rfRect.removeFrom(map);
    map.removeLayer(rfRect); 
  }
  document.getElementById('side-draw-del-rect').style.display="inline";
  var type = e.layerType;
  rfRect = e.layer;
  rfRect.addTo(map);


  map.off('draw:created',rfRectangleFinish);
}
function rfValUpd()
{
  rfLabel = document.getElementById("rfLabel").value; 
  rfTowerRx = document.getElementById("rfTowerRx").value; 
  rfRefraction = document.getElementById("rfRefraction").value; 
  profileTowerA = document.getElementById("rfTowerFrom").value; 
  profileTowerB = document.getElementById("rfTowerTo").value; 
  profilePopupUpd();
}
function rfUpdForm()
{
  document.getElementById("rfTowerRx").value = rfTowerRx; 
  document.getElementById("rfTowerFrom").value = profileTowerA; 
  document.getElementById("rfTowerTo").value = profileTowerB; 
  document.getElementById("rfLabel").value = rfLabel; 
  document.getElementById("rfTowerRx").value = rfTowerRx; 
}
function rfBack()
{
  document.getElementById("rf-result").style.visibility = "hidden";   
  document.getElementById("rf-loading").style.visibility = "hidden";   
  document.getElementById("rfCalcNew").style.visibility = "visible";  
}
function rfCalc(force)
{
  //http query

  //check rectangle
  if (map.hasLayer(rfRect) == false && (typeof force === 'undefined')) {
    document.getElementById("rf-result").style.visibility = "visible";   
    document.getElementById("rfCalcNew").style.visibility = "hidden";   

    var content = "<br><b>No rectangle placed, time of calculation may be long!</b><br><a onclick='rfBack();'>cancel</a>&nbsp;&nbsp;&nbsp;&nbsp;<a onclick='rfBack(); rfCalc(1);'>continue</a>"
    document.getElementById("rf-result").innerHTML=content;
    return; 
  }
  else if (map.hasLayer(rfRect)) {
    var rect_up = rfRect._bounds._southWest.lat
    var rect_left = rfRect._bounds._southWest.lng
    var rect_down = rfRect._bounds._northEast.lat
    var rect_right =  rfRect._bounds._northEast.lng
  }
  else if (rfUp !=0 && rfLeft !=0 && rfDown !=0 && rfRight !=0) {
    var rect_up = rfUp;
    var rect_left = rfLeft;
    var rect_down = rfDown;
    var rect_right =  rfRight;
  }

  //check marker
  if (map.hasLayer(profileMa) && map.hasLayer(profileMb)) {
    var lat1 = profileMa._latlng['lat'];
    var lon1 = profileMa._latlng['lng'];
    var lat2 = profileMb._latlng['lat'];
    var lon2 = profileMb._latlng['lng'];
  }
  else if (map.hasLayer(profileMa)) {
    var lat1 = profileMa._latlng['lat'];
    var lon1 = profileMa._latlng['lng'];
    var lat2 = 0;
    var lon2 = 0;
  }
  else if (map.hasLayer(profileMb)) {
    var lat1 = profileMb._latlng['lat'];
    var lon1 = profileMb._latlng['lng'];
    var lat2 = 0;
    var lon2 = 0;
  }else {
    document.getElementById("rf-result").style.visibility = "visible";   
    document.getElementById("rfCalcNew").style.visibility = "hidden";   

    var content = "<br><b>At least one Marker has to be set!</b><br><a onclick='rfBack();'>back</a>"
    document.getElementById("rf-result").innerHTML=content;
    return;
  }

  document.getElementById("rfCalcNew").style.visibility = "hidden";   
  document.getElementById("rf-loading").style.visibility = "visible";   

  var src="calc_visibility.cgi?lon_a="+
        lon1+"&lat_a="+lat1+"&ant_a="+profileTowerA+
        "\"&lon_b="+lon2+"&lat_b="+lat2+"&ant_b="+profileTowerB+
        "&label=\""+rfLabel+"\"&ant_c="+rfTowerRx+"&ref="+rfRefraction+
        "&up="+rect_up+"&down="+rect_down+"&left="+rect_left+"&right="+rect_right; 

  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          rfLoaded(xmlHttp.responseText);
  }
  xmlHttp.open("GET", src, true); // true for asynchronous 
  xmlHttp.send(null);

}
function rfLoaded(result)
{
  // path ; label; lat1; lon1; tower1; lat2; lon2; tower2; towerRX; ref; top; left; bottom; right;  
  result = result.split('\n'); 
  if (result.length > 1) { 
    var parameter = result[1].split(';');
  }
  else {
    return;
  }
  if(!rfLocked && result[0].length > 1){
    rfLocked=1;

    //if there is old visibility => delete
    if (map.hasLayer(rfLayer)) {
      map.removeLayer(rfLayer);
    }
    for (i=0; i<layers._layers.length;i++) {
      if (layers._layers[i].name == "(RF)-visibility"){
        layers.removeLayer(rfLayer)
        rfTiles = null;
        rfMarkerA = null;
        rfMarkerB = null;
      }
    }
    profileTowerA = parameter[4];
    profileTowerB = parameter[7];
    rfTowerRx = parameter[8];
    rfRefraction = parameter[9];
    rfLabel = parameter[1];
    rect_up = parameter[10];
    rect_left = parameter[11];
    rect_down = parameter[12];
    rect_right = parameter[13];
    rfUpdForm();

    if (parameter[0].length < 2) {
      rfLocked=0;
      return;
    }
    rfTiles = L.tileLayer(parameter[0]+'/{z}/{x}/{y}.png');
    rfLayer = L.layerGroup([rfTiles]);
    if(parameter[2] != 0 && parameter[3] != 0 ) {
      rfMarkerA = L.marker([parameter[2], parameter[3]], {
        icon: L.icon({
            iconUrl: 'osm/images/cross-red.png',
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            zIndex: 9996,
          }),
        draggable: false,
      });
      rfMarkerA.addTo(rfLayer)
    }
    if(parameter[5] != 0 && parameter[6] != 0 ) {
      rfMarkerB = L.marker([parameter[5], parameter[6]], {
        icon: L.icon({
            iconUrl: 'osm/images/cross-blue.png',
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            zIndex: 9996,
          }),
        draggable: false,
      });
      rfMarkerB.addTo(rfLayer)
    }
    if (map.hasLayer(rfRect)) {
      rfRect.removeFrom(map);
      map.removeLayer(rfRect); 
    }
    if(rect_up != 0 &&rect_right != 0 && rect_down != 0 && rect_right != 0) {
      var bounds = [[rect_down,rect_left], [rect_up, rect_right]];
      rfRect = L.rectangle(bounds, {color:'#F00',fill:false}).addTo(rfLayer);
      center_lat = (Number(rect_up)+Number(rect_down))/2;
      center_lon = (Number(rect_left)+Number(rect_right))/2;
      map.setView(new L.LatLng(center_lat,center_lon),9);
    }
    else {
      map.setView(new L.LatLng(Number(parameter[2]),Number(parameter[3])),9);
    }

    layers.addOverlay(rfLayer,"(RF)-visibility");
    rfLayer.addTo(map);

    document.getElementById("rf-loading").style.visibility = "hidden";   
    document.getElementById("rf-result").style.visibility = "visible";   
    var content = "<b>calculation \""+parameter[1]+"\" finished</b><br><a onclick='rfBack();'>back</a>"
    document.getElementById("rf-result").innerHTML=content;
    rfLocked=0;
  }
}
function rfCreateUrl()
{
  var url = '';
  //ma_lat=47.80396&ma_lon=13.109844&ma_tow=12&ma_lab=oe2xzr&mb_lat=48.575137&mb_lon=12.901848&mb_tow=10&mb_lab=nocall_1458237163

  //if profile
  if(map.hasLayer(profileMa) && map.hasLayer(profileMb) && map.hasLayer(profilePopup)){
    url = url + '&ma_lat=' + profileMa._latlng['lat'] + '&ma_lon=' + profileMa._latlng['lng'];
    url = url + '&mb_lat=' + profileMb._latlng['lat'] + '&mb_lon=' + profileMb._latlng['lng'];
    if (profileFrecuency != 5800) {
      url = url + '&=' + profileFrecuency;
    }
    if (profileWood != 30) {
      url = url + '&=' + profileWood;
    }
    if (profileFont != 1) {
      url = url + '&font=' + profileFont;
    }  
    url = url + '&ma_tow=' +  profileTowerA + '&mb_tow=' +  profileTowerB;
    url = url +  '&ma_lab=' + profileLabelA + '&mb_lab=' + profileLabelB;
  }
  else if (map.hasLayer(rfLayer)) //if visibility
  {
    url = url + '&rf_vis=1';
    url = url + '&ma_lat=' + rfMarkerA._latlng['lat'] + '&ma_lon=' + rfMarkerA._latlng['lng'];
    url = url + '&mb_lat=' + rfMarkerB._latlng['lat'] + '&mb_lon=' + rfMarkerB._latlng['lng'];
    url = url + '&ma_tow=' + profileTowerA + '&mb_tow=' +  profileTowerB;
    url = url + '&rf_ref=' + rfRefraction;
    if (rfTowerRx != 0) {
      url = url + '&rf_rx=' + rfTowerRx;
    }
    if (rfLabel != '') {
      url = url + '&rf_lab=' + rfLabel;
    }
    if(map.hasLayer(rfRect)) //if rectangle exists
    {
      url = url + '&rf_u=' + rfRect._bounds._southWest.lat;
      url = url + '&rf_l=' + rfRect._bounds._southWest.lng;
      url = url + '&rf_d=' + rfRect._bounds._northEast.lat;
      url = url + '&rf_r=' + rfRect._bounds._northEast.lng;
    }
  }

  return url;
}
function mapSource()
{
  var ms = document.getElementById("mapsource").value;
  //var url = window.location.href + "&source=" + ms;
  setGetParameter('source',ms,true);
}
function getParameter(paramName)
{
  var url = window.location.href;
  //var paramValue
  var end = url.length;
  if (url.indexOf(paramName + "=") >= 0)
  {
    var start = url.indexOf(paramName + "=");
    var bug = url.indexOf("#",start);
    if(url.indexOf("&",start) >= 0)
    {
      end = url.indexOf("&", start);
    }
    if (bug < end && bug > start) //bug of openlayers url-function
    {
      end = bug;
    }
    paramValue = url.substring(end,start + paramName.length + 1);
      
  }
  else
  {
    paramValue=0;
  } 
  return paramValue;
}
function setGetParameter(paramName, paramValue, reload)
{
    var url = window.location.href;
    //if exists
    if (url.indexOf(paramName + "=") >= 0)
    {
        var prefix = url.substring(0, url.indexOf(paramName));
        var suffix = url.substring(url.indexOf(paramName)).substring(url.indexOf("=") + 1);
        suffix = url.substring(url.indexOf(paramName + "=") + paramName.length +1);
        
        if(suffix.indexOf("&") >= 0)
        {
          if(suffix.indexOf("#") < suffix.indexOf("&") && suffix.indexOf("#") >= 0)
          {
            suffix = "&" + suffix.substring(suffix.indexOf("#"));//from next #
          }
          else
            suffix = suffix.substring(suffix.indexOf("&"));//from next &
        }
        else //last parameter
        {
          suffix = "";
        }
        url = prefix + paramName + "=" + paramValue + suffix;
    }
    else
    {
      //empty url
      if ((url.indexOf("?") < 0) && (url.indexOf("#") <0))
      {
        url += "?" + paramName + "=" + paramValue;
      } //url without parameters with #asdasd
      else if((url.indexOf("?") <0) && (url.indexOf("#") >= 0))
      {
      var prefix = url.substring(0, url.indexOf("#"));
      var suffix = url.substring(url.indexOf("#"));
      url = prefix + "?" +paramName + "=" + paramValue + "&" + suffix;
      }  
      else
      {
        var prefix = url.substring(0, url.indexOf("?"));
        var suffix = url.substring(url.indexOf("?") + 1);
        url = prefix + "?" + paramName + "=" + paramValue + "&" + suffix;
      }
      
    }
    if(reload == true)
      window.location.href = url;
    else
      window.history.pushState("", "HamnetDB Map", url);
    //alert(url);
    //window.location = url;
}

//get Site data and center map to it
function getSite(site) 
{   
  var url = kmlUrl
  var xmlhttp = null;
  // Mozilla
  if (window.XMLHttpRequest) 
  {
    xmlhttp = new XMLHttpRequest();
  }
  // IE
  else if (window.ActiveXObject) 
  {
    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
  }
  xmlhttp.open("GET", url, true);
  xmlhttp.onreadystatechange = function(){
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) //if OK
    {
      var lon_f = 0;
      var lat_f = 0;
      coor = new Array();
      get_str = xmlhttp.responseText;
      if (window.DOMParser)
      {
        parser=new DOMParser();
        xmldoc=parser.parseFromString(get_str,"text/xml");
      }
      else // IE
      {
        xmldoc = new ActiveXObject("Microsoft.XMLDOM");
        xmldoc.async = false;
        xmldoc.loadXML(get_str); 
      }
      jsondoc = JSON.parse(get_str); 
      
      for(var i=0;i<jsondoc.features.length;i++)
      {
        if(jsondoc.features[i].geometry.type== "Point")
        {
          var call, lon, lat;
          call = jsondoc.features[i].properties.callsign;
          
          if(call == site)
          {
            line = jsondoc.features[i].geometry.coordinates;
            lon_f = line[0];  
            lat_f = line[1];
            break;
          }
        }
      }
      if(lon_f != 0 && lat_f != 0)//othervise error happend
      {
        map.setView(new L.LatLng(parseFloat(lat_f),parseFloat(lon_f)),11);
      }
    }
  }  
  xmlhttp.send(null);
}

//get as data and center map to it
function getAs(as) 
{   
  var url = kmlUrl+"&only_hamnet=1&only_as="+as
  var xmlhttp = null;
  // Mozilla
  if (window.XMLHttpRequest) 
  {
    xmlhttp = new XMLHttpRequest();
  }
  // IE
  else if (window.ActiveXObject) 
  {
    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
  }
  xmlhttp.open("GET", url, true);
  xmlhttp.onreadystatechange = function(){
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) //if OK
    {
      var lon_min = 999;
      var lon_max = 0;
      var lon_f = 0;
      var lat_min = 999;
      var lat_max = 0;
      var lat_f = 0;
      coor = new Array();
      get_str = xmlhttp.responseText;
      if (window.DOMParser)
      {
        parser=new DOMParser();
        xmldoc=parser.parseFromString(get_str,"text/xml");
      }
      else // IE
      {
        xmldoc = new ActiveXObject("Microsoft.XMLDOM");
        xmldoc.async = false;
        xmldoc.loadXML(get_str); 
      }
      jsondoc = JSON.parse(get_str); 
      //alert(jsondoc.features.length);
      //get maximum values of coordinate and calculate center
      for(var i=0;i<jsondoc.features.length;i++)
      {
        if(jsondoc.features[i].geometry.type== "Point")
        {
          var line, lon, lat;
          line = jsondoc.features[i].geometry.coordinates;
          lon = line[0];  
          lat = line[1];

          if (lon < lon_min) lon_min = lon;
          if (lon > lon_max) lon_max = lon;
          if (lat < lat_min) lat_min = lat;
          if (lat > lat_max) lat_max = lat;
        }
      }
      if(lon_min != 999 && lat_min != 999)//othervise error happend
      {
        lon_f = (parseFloat(lon_min) + parseFloat(lon_max))/2.0;
        lat_f = (parseFloat(lat_min) + parseFloat(lat_max))/2.0;
       // var center = new OpenLayers.LonLat(lon_f, lat_f).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
      //  map.setCenter (center, 9);
        map.setView(new L.LatLng(lat_f,lon_f),9);
      }
    }
  }  
  xmlhttp.send(null);
}

//when AS-optionbox is changed
function panelChange ()
{
  var as = document.getElementById("only_as").getElementsByTagName("select")[0].value;
  if(as == "-All-")
  {
    as=0;
  }
  getAs(as);
}
function getHttpRequest(url,id) {   
  var xmlhttp = null;
  // Mozilla
  if (window.XMLHttpRequest) {
    xmlhttp = new XMLHttpRequest();
  }
  // IEma
  else if (window.ActiveXObject) {
    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
  }
  xmlhttp.open("GET", url, true);
  xmlhttp.onreadystatechange = function(){
  
    get_data = new Array();

    get_str = xmlhttp.responseText;
    document.getElementById(id).innerHTML=get_str;
  }  
  xmlhttp.send(null);
}
function popupw (url) 
{
   fenster = window.open(url, "Detail Info", "scrollbars=1,width=800,height=600,resizable=yes");
   fenster.focus();
   return false;
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////

function getCoverage(url, only_exist) 
{    
  var xmlhttp = null;
  
// Mozilla
  if (window.XMLHttpRequest) 
  {
    xmlhttp = new XMLHttpRequest();
  }
  // IE
  else if (window.ActiveXObject) 
  {
    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
  }

  xmlhttp.open("GET", url, true);
  
  if(only_exist == "0"){
    xmlhttp.onreadystatechange = function(){
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) //if OK
    {
      get_str = new Array();
      get_str = xmlhttp.responseText;
	
      jsondoc = JSON.parse(get_str);	
	
      var imageBounds = [[jsondoc.South,jsondoc.West],[jsondoc.North,jsondoc.East]];
      var url = CoverUrl + jsondoc.Callsign +'_'+jsondoc.Tag;

      var imageUrl_green = url + '_green.png';

      var image_green = L.imageOverlay(imageUrl_green,imageBounds,{attribution: 'Coverage'});

      //Remove all three Grouplayers from map
      map.removeLayer(GreenCover);

      //Add new coverage images to the coresponding layer; check for layers only necessary as 
      //long as box is always unchecked after closing popup

      if(!GreenCover.hasLayer(CoverageLayers[jsondoc.Callsign +'_'+jsondoc.Tag +"_green"]))
      {
        GreenCover.addLayer(image_green);
        CoverageLayers[jsondoc.Callsign+'_'+jsondoc.Tag + '_green'] =  GreenCover.getLayerId(image_green);
      }
      

      GreenCover.addTo(map);
      
      image_green.setOpacity(0.8);
      }
    }
  }else { //only_exist = 1
    xmlhttp.onreadystatechange = function(){
      if (xmlhttp.readyState == 4 && xmlhttp.status == 200) //if OK
      {
        get_str = new Array();
        get_str = xmlhttp.responseText;
        //hubertus shouldn't c&p

        if(get_str == "0"){
          document.getElementsByName("Coverage")[0].disabled = true;
          document.getElementsByName("Coverage")[0].style.visibility = "hidden";   
        }
        else{	
          document.getElementsByName("Coverage")[0].style.visibility = "visible";   
          jsondoc = JSON.parse(get_str)
          var tags = jsondoc.Tag.split(" ");
          var number = tags.length;
          var text= document.getElementsByName("Coverage")[0].outerHTML;  
          for(var i=1; i<number;i++){
            document.getElementById("displayCoverage").innerHTML+= text;
          }
          for(var j=0; j<number; j++){
            document.getElementsByName("Coverage")[0].outerHTML+=" "+tags[j]+"<br>";
            document.getElementsByName("Coverage")[0].name= jsondoc.Callsign+'_'+tags[j];
	       
            if(GreenCover.hasLayer(CoverageLayers[jsondoc.Callsign +'_'+tags[j]+"_green"]))
            {
              document.getElementsByName(jsondoc.Callsign+'_'+tags[j])[0].checked = true;
            }
          }
        } 
      }
    }
  }
  xmlhttp.send(null);
}


function coverage(event)
{ 

  var callsign= event.target.name;
 
  if(event.target.checked)
  {
    //Get Coverage Data (status, coordinates) from DB by callsign; add images to CoverageLayers
    getCoverage("mapcoverage.cgi?x="+callsign,0);
  }
  else
  {
    GreenCover.removeLayer(CoverageLayers[callsign + "_green"]);

    delete CoverageLayers[callsign + "_green"];
  }
  return 1;
}
