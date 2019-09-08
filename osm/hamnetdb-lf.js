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
var GreenCover;

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
var profileMpos;
var profileLine;
var profilePopup;
var profileMetadata = new Array();


var rfRect;
var rfMark = null;
var rfTowerRx = 2;
var rfMarkerA;
var rfMarkerB;
var rfTiles;
var rfLayer;
var rfLocked = 0;
var rfUp = 0;
var rfLeft = 0;
var rfDown = 0;
var rfRight = 0;
var rfRefraction = 0.25;
var rfLabel= "";

var rfTowerFromP = 10;
var rfElevation = 0;
var rfAngle = 50;
var rfRefractionPanorama = 0.25;
var rfFontPanorama = 1 ;
var rfZoom = 1;
var rfPoiInput;
var rfPoiHamnet;
var rfPoiFWC;
var rfPoiMT;
var rfPoiSota;
var rfPoi;
var rfSnow1 = 2500;
var rfSnow2 = 500;
var rfSunAz = 0; 
var rfSunEL = 0;
var rfDesert = 0;
var rfVisTree = 1;

var rfPanoramaPopup;
var panoramaMetadata = new Array();

var rect= null;



var elem;
var testg;
window.addEventListener("load",function() {
	// Set a timeout...
	setTimeout(function(){
		// Hide the address bar!
		window.scrollTo(0, 1);
	}, 0);
});

//window.addEventListener("load", function(){ if(!window.pageYOffset){ hideAddressBar(); } } );
//window.addEventListener("orientationchange", hideAddressBar );

function init()
{  
  GreenCover = new L.layerGroup();
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
  rfTowerRxtmp = getParameter("rf_rx");
  rfLabeltmp = getParameter('rf_lab');
  rect_up = getParameter("rf_u");
  rect_left = getParameter("rf_l");
  rect_down = getParameter("rf_d");
  rect_right = getParameter("rf_r");
  rf_vis = getParameter("rf_vis");
  rf_tools = getParameter("rf_tools");
  rf_pan = getParameter("rf_pan"); 
  rfRefractiontmp = getParameter("rf_ref");
  rfRefractionPtmp = getParameter("rf_p_ref");
  rfElevation = getParameter("rf_el");
  rfAngletmp = getParameter("rf_ang");
  rfZoomtmp = getParameter("rf_z");
  rfFontPanoramatmp = getParameter("rf_p_font");
  rfPoiInput = getParameter("rf_poi"); 
  rfTowerFromPtmp = getParameter("rf_p_tow");
  rfSnow1tmp = getParameter("rf_snow1");
  rfSnow2tmp = getParameter("rf_snow2");
  rfSunAztmp = getParameter("rf_sun_az");
  rfSunEltmp = getParameter("rf_sun_el");
  rfDeserttmp = getParameter("rf_desert");
  rfVisTreetmp  = getParameter("rf_tree");

  if (rfTowerRxtmp != 0) {
    rfTowerRx = rfTowerRxtmp;
  }
  if (rfLabeltmp != 0) {
    rfLabel = rfLabeltmp; 
  }
  if (rfRefractiontmp != 0) { //0 is "0.0"
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
  if (rfRefractionPtmp != 0) { //0 is "0.0"
    rfRefractionPanorama = rfRefractionPtmp;
  }
  if (rfAngletmp != "0") { 
    rfAngle = rfAngletmp;
  }
  if (rfFontPanoramatmp != "0") { 
    rfFontPanorama = rfFontPanoramatmp;
  }
  if (rfTowerFromPtmp != "0") { 
    rfTowerFromP = rfTowerFromPtmp;
  }
  if (rfZoomtmp != 0) {
    rfZoom = rfZoomtmp;
  }
  if (rfSnow1tmp != 0) {
    rfSnow1 = rfSnow1tmp;
  }
  if (rfSnow2tmp != 0) {
    rfSnow2 = rfSnow2tmp;
  }
 if (rfSunAztmp != 0) {
    rfSunAz = rfSunAztmp;
  }
  if (rfSunEltmp != 0) {
    rfSunEl = rfSunEltmp;
  }
  if (rfVisTreetmp === "0") {
    rfVisTree = 0;
  } 
  if (rfDeserttmp == "0") {
    rfDesert = 0;
  } 
  else {
    rfDesert = 1;
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
    var opentopoURL = 'webcam/map/otm/{z}/{x}/{y}.png';
    //var opentopoURL = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png';
    var osmbwURL = 'http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png';
    var mapnikZoom = 18;
    var landscapeZoom = 18;
    var outdoorZoom = 18;
    var cycleZoom = 18;
    var opentopoZoom = 17;
  }
  
  var attribution = '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a> | <a href="osm/copyright.html" target="_blank">Copyright</a>'; 
  map = new L.Map('map', 
    {center: new L.LatLng(49.26, 12.47), 
    zoom: 7, 
    zoomControl:false,
    preferCanvas: true,
    //renderer: L.canvas(),
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
  //var miniMapnik = new L.TileLayer(mapnikUrl, {minZoom: 0, maxZoom: 13, attribution: " " });
  //var miniMap = new L.Control.MiniMap(miniMapnik, { toggleDisplay: true }).addTo(map);
  //miniMap._minimize();
  
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
  var osmbwLayer = L.tileLayer(
    osmbwURL,
    {
      attribution: attribution,
      maxZoom: mapnikZoom
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
          opacity= 0.5
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
              rfTowerFromP = feature.properties.anthight;
              placeProfileFrom(loc);
              rfUpdForm();
              rfPanUpdForm();
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
            rfTowerFromP = feature.properties.anthight;
            placeProfileTo(loc);
            rfUpdForm();
            rfPanUpdForm();
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
      'OSM b&w' :osmbwLayer,
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
      'OSM b&w' :osmbwLayer
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
  map.addControl( new L.Control.Search({
    url: 'map_search.cgi?q={s}',
    //url: 'https://nominatim.openstreetmap.org/search?format=json&q={s}',
    //jsonpParam: 'json_callback',
    propertyName: 'display_name',
    propertyLoc: ['lat','lon'],
    markerLocation: true,
    autoCollapse: true,
    autoType: false,
    minLength: 2,
    zoom: 11,
    position: 'topright'
  }) );

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

  //Profile init
  if ((ma_lat!=0) && (ma_lon!=0) && (mb_lat!=0) && (mb_lon!=0) && rf_vis == 0 && rf_pan == 0)
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
    map.setView([((Number(ma_lat)+Number(ma_lat))/2), ((Number(ma_lon)+Number(mb_lon))/2)], 9);
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
  if (rf_tools) {
    SidebarRftools.toggle(); 
  }
  if (rf_pan) {
    ma = new L.LatLng(ma_lat, ma_lon);
    mb = new L.LatLng(mb_lat, mb_lon);
    drawFrom(ma);
    drawTo(mb);


    rfPanUpdForm();
    rfPanUpd();
    if(rfPoiInput.length > 2)
    {
      if(rfPoiInput.includes('hamnet'))
        document.getElementById("rfPoiHamnet").checked = 1;
      else
        document.getElementById("rfPoiHamnet").checked = 0;
      if(rfPoiInput.includes('wc'))
        document.getElementById("rfPoiFWC").checked = 1;
      else
        document.getElementById("rfPoiFWC").checked = 0;
      if(rfPoiInput.includes('mt'))
        document.getElementById("rfPoiMT").checked = 1;
      else
        document.getElementById("rfPoiMT").checked = 0;
      if(rfPoiInput.includes('small'))
        document.getElementById("rfPoi").checked = 1;
      else 
        document.getElementById("rfPoi").checked = 0;
      if(rfPoiInput.includes('sota'))
        document.getElementById("rfPoiSota").checked = 1;
      else 
        document.getElementById("rfPoiSota").checked = 0;
    }

    var sel;
    if(rfRefractionPanorama == 0.0)
      sel = 0;
    else if(rfRefractionPanorama == 0.13)
      sel = 1;
    else if(rfRefractionPanorama == 0.25)
      sel = 2;
    else 
      sel = 2;
    document.getElementById("rfRefractionPanorama").selectedIndex=sel;
    var selFont;
    if(rfPanoramaFont == 0.0)
      selFont = 0;
    else if(rfPanoramaFont == 1)
      selFont = 1;
    else if(rfPanoramaFont == 2)
      selFont = 2;
    else if(rfPanoramaFont == 3)
      selFont = 3;
    else 
      selFont = 1;
    document.getElementById("rfPanoramaFont").selectedIndex=selFont;

    SidebarRftools.toggle();
    rfOpenpanorama(); 
  }
  rfLoadPreset();
  panoramaMsgInit();
}
function placeProfileFrom (e) {
  if (typeof e.latlng !== 'undefined') 
  {
    e=e.latlng
  }
  deleteProfileMa();
  drawFrom(e);
  profileProceed();
  document.getElementById('rfTowerFromLine').style.color="#000";

} 
function placeProfileTo (e) {
  if (typeof e.latlng !== 'undefined') 
  {
    e=e.latlng
  }
  deleteProfileMb();
  drawTo(e);
  profileProceed();
  document.getElementById('rfTowerToLine').style.color="#000";
  if (typeof profileMa == 'undefined') {
    document.getElementById('rfTowerFromLine').style.color="#aaa";
  }
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
          deleteProfileMa();
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
            deleteProfileMb();
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
  document.getElementById('side-draw-del-point3').style.display="inline"
  if ((typeof profileMa !== 'undefined') &&(typeof profileMb !== 'undefined')) {
    if((profileMa._icon != null) && (profileMb._icon != null))
    {
      deleteProfileLine();
      var pointList = [profileMa._latlng, profileMb._latlng];
      var ua = window.navigator.userAgent;
      var msie = ua.indexOf("MSIE ");

      if (msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./))// If Internet Explorer, puke
      {
        profileLine = new L.Polyline(pointList, {
          color: 'red',
          weight: 4,
          opacity: 0.9,
          smoothFactor: 1,
          zIndex:9994,
        });
      }
      else
      {
        profileLine = new L.geodesic([[profileMa.getLatLng(), profileMb.getLatLng()]], {
          color: 'red',
          weight: 4,
          opacity: 0.9,
          //smoothFactor: 1,
          zIndex:9994,
        });
      }
      profileLine.addTo(map);
      profileLine.on("click", function(e) {profileDraw(); profilePosition(e)});
      //profileLine.on("mouseover", function (e) {profilePosition(e);}); 
      profileLine.on("mousemove", function (e) {profilePosition(e);}); 
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
  deleteProfileMpos();
}
function deleteProfileMa() {
  if (typeof profileMa !== 'undefined') {
    map.removeLayer(profileMa);
  }
  if (typeof profileMb !== 'undefined') {
    if(profileMb._latlng != null) {
      document.getElementById('rfTowerFromLine').style.color="#aaa";
    }
  }
  deleteProfileMpos();
}
function deleteProfileMb() {
  if (typeof profileMb !== 'undefined') {
    map.removeLayer(profileMb);
    document.getElementById('rfTowerFromLine').style.color="#000";
    document.getElementById('rfTowerToLine').style.color="#aaa";
  }
  deleteProfileMpos();
}
function deleteProfileMpos(){
  if (map.hasLayer(profileMpos)) {
    if(profileMpos._latlng != null) {
      map.removeLayer(profileMpos);
    }
  }
  if (typeof profilePopup !== 'undefined') { //catch open popup
    if (profilePopup._map !=null) {
      document.getElementById('profile-free').innerHTML = "";
    }
  }
}
function deleteProfileAll() {
  profileLabelA = "";
  profileLabelB = "";
  deleteProfileLine(); 
  deleteProfileMa();
  deleteProfileMb();
  document.getElementById('side-draw-del-point1').style.display="none"
  document.getElementById('side-draw-del-point2').style.display="none"
  document.getElementById('side-draw-del-point3').style.display="none"
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

      var popupcontent="<span class='popup-darg'>drag and drop popup and markers</span><span id='profile-free'></span> \
        <img id='proifleimg' src='"+profilelink+"' style='font-size:40px;'\
         onmouseover='javascript:profileProcessMetadata(event);' onmousemove='javascript:profileProcessMetadata(event);' alt='loading...'/>\
        <img id='profile-marker' src='osm/images/mouse_marker.png'>\
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
      .setLatLng([(Number(lat1) + Number(lat2))/2, (Number(lon1)+Number(lon2))/2])
      .setContent(popupcontent)
      .openOn(map);
    
      map.addLayer(profilePopup);

      var pos = map.latLngToLayerPoint(profilePopup._latlng);
      L.DomUtil.setPosition(profilePopup._wrapper.parentNode,pos);
      var draggable = new L.Draggable(profilePopup._container, profilePopup._wrapper);
      draggable.enable();
      map.setView(new L.LatLng((Number(lat1) + Number(lat2))/2, (Number(lon1)+Number(lon2))/2));
      deleteProfileMpos();
      document.getElementById("profile-marker").style.visibility = "hidden";
      var meta_url=profileGenMetaLink(width,height);
      profileGetMetadata(meta_url);
    }
  }
}
function profilePopupUpd()
{
  if (map.hasLayer(profilePopup)) {
    document.getElementById("labela").value = profileLabelA; 
    document.getElementById("labelb").value = profileLabelB; 
    document.getElementById("towera").value = profileTowerA; 
    document.getElementById("towerb").value = profileTowerB; 
  }
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
  document.getElementById("profile-marker").style.visibility = "hidden";
  //profile metadata
  deleteProfileMpos();
  document.getElementById("profile-marker").style.visibility = "hidden";
  var meta_url=profileGenMetaLink(width,height);
  profileGetMetadata(meta_url);
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
function profileCalcParameters(width,height)
{
  var lat1 = profileMa._latlng['lat'];
  var lon1 = profileMa._latlng['lng'];
  var lat2 = profileMb._latlng['lat'];
  var lon2 = profileMb._latlng['lng'];
  src = "f="+profileFrecuency+"&lon_a="+
        lon1+"&lat_a="+lat1+"&ant_a="+profileTowerA+"&name_a=\""+profileLabelA+
        "\"&lon_b="+lon2+"&lat_b="+lat2+"&ant_b="+profileTowerB+"&name_b=\""+profileLabelB+
        "\"&wood="+profileWood+"&font="+profileFont+"&h="+height+"&w="+width;
  return src;
}
function profileGenLink(width,height)
{
  var lat1 = profileMa._latlng['lat'];
  var lon1 = profileMa._latlng['lng'];
  var lat2 = profileMb._latlng['lat'];
  var lon2 = profileMb._latlng['lng'];
  src = host_calc_profile+"calc_profile.cgi?f="+profileFrecuency+"&lon_a="+
        lon1+"&lat_a="+lat1+"&ant_a="+profileTowerA+"&name_a=\""+profileLabelA+
        "\"&lon_b="+lon2+"&lat_b="+lat2+"&ant_b="+profileTowerB+"&name_b=\""+profileLabelB+
        "\"&wood="+profileWood+"&font="+profileFont+"&h="+height+"&w="+width;
  return src;
} 
function profileGenMetaLink(width,height)
{
  var lat1 = profileMa._latlng['lat'];
  var lon1 = profileMa._latlng['lng'];
  var lat2 = profileMb._latlng['lat'];
  var lon2 = profileMb._latlng['lng'];
  src = host_calc_profile+"calc_profile_metadata.cgi?mode=1&f="+profileFrecuency+"&lon_a="+
        lon1+"&lat_a="+lat1+"&ant_a="+profileTowerA+
        "&lon_b="+lon2+"&lat_b="+lat2+"&ant_b="+profileTowerB+
        "&wood="+profileWood+"&font="+profileFont+"&h="+height+"&w="+width;
  return src;
}
function profilePosition(e)
{
  if (map.hasLayer(profilePopup)) {
    var lat1 = profileMa._latlng['lat'];
    var lon1 = profileMa._latlng['lng'];
    var lat2 = profileMb._latlng['lat'];
    var lon2 = profileMb._latlng['lng'];
    var lon_mouse = e.latlng.lng;
    var lat_mouse = e.latlng.lat;
    if (profileFont == 1) {
      offset = 36;
      netto_pixels = 608;
    }else if (profileFont == 2) {
      offset = 46;
      netto_pixels = 598;
    }else if (profileFont == 3) {
      offset = 56;
      netto_pixels = 588;
    }
    length = getDistance(lat1,lon1,lat2,lon2);
    length_mouse = getDistance(lat1,lon1,lat_mouse,lon_mouse);
    position_marker = length_mouse/length*netto_pixels;
    document.getElementById("profile-marker").style.visibility = "visible";
    document.getElementById("profile-marker").style.left = offset-1+position_marker+"px";
    deleteProfileMpos();
  }
}
function profileProcessMetadata(event)
{
  img = document.getElementById("proifleimg");
  pos_x = event.offsetX?(event.offsetX):event.pageX-img.offsetLeft;
  pos_y = event.offsetY?(event.offsetY):event.pageY-img.offsetTop;
  if(typeof profileMetadata[pos_x] !== 'undefined')
  {
    document.getElementById("profile-marker").style.visibility = "visible";
    document.getElementById("profile-marker").style.left = pos_x-1.5+"px";
    deleteProfileMpos();
    rfPoint(profileMetadata[pos_x].lat, profileMetadata[pos_x].lon);
    document.getElementById('profile-free').innerHTML = "Free space to ground: " + profileMetadata[pos_x].free + "m &nbsp;&nbsp; Radius of 1st order Fresnel zone: " + profileMetadata[pos_x].fresnel + "m" ;
  }
}

function profileGetMetadata(url)
{
  profileMetadata = []; //empty array
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
      get_str = xmlhttp.responseText;
      if (get_str.length > 5)
      {
        profileGotMetadata(get_str);
      }
    }
  }  
  xmlhttp.send(null);
}
function profileGotMetadata(meta_content)
{
  result = meta_content.split('\n');
  for (i = 0; i < result.length; i++) {
    //parse csv & fill object
    line=result[i].split(',');
    pixel = Number(line[0]);
    profileMetadata[pixel] = new Object()
    profileMetadata[pixel].lat = Number(line[1]);
    profileMetadata[pixel].lon = Number(line[2]);
    profileMetadata[pixel].free = Number(line[3]);
    profileMetadata[pixel].fresnel = Number(line[4]);
  }
}
function popupSetting()
{
  var pop = document.getElementById("hoverpopup").checked;
  setGetParameter('hover',pop,true);
}
function rfPlacemarker()
{
  var createnew= true;
  if(typeof rect !== 'undefined') {
    if (rect != null) {
      rect.disable();
      rfMarkRect(0);
    }
  }
  map.off('draw:created',rfPlaceA);
  map.off('draw:created',rfPlaceB);
  map.off('draw:created',rfRectangleFinish);
  if (rfMark !== null) {
    if (typeof rfMark._enabled !== "undefined")
    {
      if (rfMark._enabled == true){
        rfMark.disable();
        rfMark = null;
        createnew=0;
        rfMarkPlace(0);
      }
    }
  }
  
  if (createnew)
  {
    rfMark= new L.Draw.Marker(map);
    rfMark.enable();
    map.on('draw:created',rfPlaceA);
    rfMarkPlace(1);
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
  rfMarkPlace(0);
}
function rfMarkPlace(e) {
  if(e)
  {
    document.getElementById('side-draw-add-point1').style.backgroundColor="#bbb";
    document.getElementById('side-draw-add-point2').style.backgroundColor="#bbb";
    document.getElementById('side-draw-add-point3').style.backgroundColor="#bbb";
  }
  else {
    document.getElementById('side-draw-add-point1').style.backgroundColor="#fff";
    document.getElementById('side-draw-add-point2').style.backgroundColor="#fff";
    document.getElementById('side-draw-add-point3').style.backgroundColor="#fff";
  }
}
function rfMarkRect(e) {
  if(e)
  {
    document.getElementById('side-draw-add-rect').style.backgroundColor="#bbb";
  }
  else {
    document.getElementById('side-draw-add-rect').style.backgroundColor="#fff";
  }
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
  var createnew= true;
  if (typeof rfMark !== 'undefined') {
    if (rfMark != null) {
      rfMark.disable();
      rfMarkPlace(0);
    }
  }
  map.off('draw:created',rfPlaceA);
  map.off('draw:created',rfPlaceB);

  if (rect != null) {
    if (typeof rect._enabled !== "undefined") {
      if (rect._enabled == true) {
        rect.disable();
        rect = null;
        createnew = false
        rfMarkRect(0);
      }
    }
  }

  if (createnew) {
    rect= new L.Draw.Rectangle(map,{shapeOptions:{color:'#F00',fill:false}});
    rect.enable();
    map.on('draw:created',rfRectangleFinish);
    rfMarkRect(1);
  }
  
}
function rfDelRectangle()
{
  if (map.hasLayer(rfRect)) 
  {
    rfRect.removeFrom(map);
    map.removeLayer(rfRect); 
    rfUp= 0;
    rfLeft= 0;
    rfDown= 0;
    rfRight= 0;
  }
  document.getElementById('side-draw-del-rect').style.display="none";
}
function rfRectangleFinish(e) {

  map.off('draw:created',rfRectangleFinish);
  if (map.hasLayer(rfRect)) {
    rfRect.removeFrom(map);
    map.removeLayer(rfRect); 
  }
  document.getElementById('side-draw-del-rect').style.display="inline";
  var type = e.layerType;
  rfRect = e.layer;
  rfRect.addTo(map);
  rfMarkRect(0);
}
function rfValUpd()
{
  rfLabel = document.getElementById("rfLabel").value; 
  rfTowerRx = document.getElementById("rfTowerRx").value; 
  rfRefraction = document.getElementById("rfRefraction").value
  profileTowerA = document.getElementById("rfTowerFrom").value; 
  profileTowerB = document.getElementById("rfTowerTo").value; 

  rfTowerFromP = document.getElementById("rfTowerFromP").value;
  rfElevation = document.getElementById("rfElevation").value;
  rfAngle = document.getElementById("rfAngle").value;
  rfZoom = document.getElementById("rfZoom").value;
  rfRefractionPanorama = document.getElementById("rfRefractionPanorama").value;
  rfFontPanorama = document.getElementById("rfPanoramaFont").value;
  rfPoiHamnet = document.getElementById("rfPoiHamnet").checked;
  rfPoiFWC = document.getElementById("rfPoiFWC").checked;
  rfPoiSota = document.getElementById("rfPoiSota").checked;
  rfPoiMT = document.getElementById("rfPoiMT").checked;
  rfPoi = document.getElementById("rfPoi").checked;
  rfSnow1 = document.getElementById("rfSnow1").value;
  rfSnow2 = document.getElementById("rfSnow2").value;
  rfSunAz = document.getElementById("rfSunAz").value;
  rfSunEl = document.getElementById("rfSunEl").value;
  rfVisTree = document.getElementById("rfVisTree").checked;
  rfDesert = document.getElementById("rfDesert").checked;

  profilePopupUpd();
}
function rfPanUpd()
{
  document.getElementById("rfAngletlbl").innerHTML=document.getElementById("rfAngle").value+"°";
  document.getElementById("rfElevationlbl").innerHTML=document.getElementById("rfElevation").value+"°";
  document.getElementById("rfZoomlbl").innerHTML=document.getElementById("rfZoom").value;
  document.getElementById("rfSnow1lbl").innerHTML=document.getElementById("rfSnow1").value+" m";
  document.getElementById("rfSnow2lbl").innerHTML=document.getElementById("rfSnow2").value+" m";
  document.getElementById("rfSunAzlbl").innerHTML=document.getElementById("rfSunAz").value+"°";
  document.getElementById("rfSunEllbl").innerHTML=document.getElementById("rfSunEl").value+"°";
  rfValUpd();
}
function rfUpdForm()
{
  document.getElementById("rfTowerRx").value = rfTowerRx; 
  document.getElementById("rfTowerFrom").value = profileTowerA; 
  document.getElementById("rfTowerTo").value = profileTowerB; 
  document.getElementById("rfLabel").value = rfLabel; 
  document.getElementById("rfTowerRx").value = rfTowerRx; 
  document.getElementById("rfVisTree").checked = rfVisTree;
}
function rfBack()
{
  document.getElementById("rf-result").style.display = "none";   
  document.getElementById("rf-loading").style.display = "none";   
  document.getElementById("rfCalcNew").style.display = "inline";  
}
function rfLoadPreset()
{
  var src=host_calc_visibility+"calc_visibility.cgi?list=1"; 

  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          rfUpdatePreset(xmlHttp.responseText);
  }
  xmlHttp.open("GET", src, true); // true for asynchronous 
  xmlHttp.send(null);
}
function rfUpdatePreset(value)
{
  result = value.split('\n');


  e=document.getElementById('rfPreset').options;
  e.length=0;
  for (i = 0; i < result.length; i++) {
    e[i]= new Option(result[i], result[i], false, false);
  }
}
function rfGetPreset()
{
  rfLabel = document.getElementById('rfPreset').value;
  if (rfLabel.length > 0) {
    rfCalc(2);
  }
}
function rfCalc(force)
{
  //http query

  //check rectangle
  if (map.hasLayer(rfRect) == false && (typeof force === 'undefined')) {
    //document.getElementById("rf-result").style.visibility = "visible";   
    //document.getElementById("rfCalcNew").style.visibility = "hidden";   
    document.getElementById("rf-result").style.display = "inline";   
    document.getElementById("rfCalcNew").style.display = "none";   
    var content = "<br><b>No rectangle placed, time of calculation may be long!</b><br><a onclick='rfBack();'>cancel</a>&nbsp;&nbsp;&nbsp;&nbsp;<a onclick='rfBack(); rfCalc(1);'>continue</a><br>"
    document.getElementById("rf-result").innerHTML=content;
    return; 
  }
  else if (map.hasLayer(rfRect)) {
    var rect_down = rfRect._bounds._southWest.lat
    var rect_left = rfRect._bounds._southWest.lng
    var rect_up = rfRect._bounds._northEast.lat
    var rect_right =  rfRect._bounds._northEast.lng
  }
  else { //(rfUp !=0 && rfLeft !=0 && rfDown !=0 && rfRight !=0) {
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
  }else if (force != 2 ) {
    document.getElementById("rf-result").style.display = "inline";   
    document.getElementById("rfCalcNew").style.display = "none";   

    var content = "<br><b>At least one Marker has to be set!</b><br><a onclick='rfBack();'>back</a><br>"
    document.getElementById("rf-result").innerHTML=content;
    return;
  }

  //document.getElementById("rfCalcNew").style.visibility = "hidden";   
  //document.getElementById("rf-loading").style.visibility = "visible";   
  document.getElementById("rfCalcNew").style.display = "none";   
  document.getElementById("rf-loading").style.display = "inline"; 
  var rfVisTreeOut;
  if (rfVisTree) // true => 1
    rfVisTreeOut = 1;
  else
    rfVisTreeOut = 0;

  var src=host_calc_visibility+"calc_visibility.cgi?lon_a="+
        lon1+"&lat_a="+lat1+"&ant_a="+profileTowerA+
        "\"&lon_b="+lon2+"&lat_b="+lat2+"&ant_b="+profileTowerB+
        "&label=\""+rfLabel+"\"&ant_c="+rfTowerRx+"&ref="+rfRefraction+
        "&tree="+rfVisTreeOut+
        "&up="+rect_up+"&down="+rect_down+"&left="+rect_left+"&right="+rect_right; 
  if (force == 2) {
    src=host_calc_visibility+"calc_visibility.cgi?load=1&label="+rfLabel;
  }

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
  if (result.length > 1 && result[0].indexOf('OK') != -1) { //&& $result[0].indexOf('OK') !== -1
    var parameter = result[1].split(';');
  }
  else {
    document.getElementById("rf-loading").style.display = "none";   
    document.getElementById("rf-result").style.display = "inline";   
    var content = "<br><b>error calculating visibility</b><br><a onclick='rfBack();'>back</a><br>"
    document.getElementById("rf-result").innerHTML=content;
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
    rfLabel = parameter[1];
    
    profileTowerA = parameter[4];
    profileTowerB = parameter[7];
    rfTowerRx = parameter[8];
    rfRefraction = parameter[9];
    rfVisTree = parseInt(parameter [10]);
    rect_up = parameter[11];
    rect_left = parameter[12];
    rect_down = parameter[13];
    rect_right = parameter[14];
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
            zIndex: -996,
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
            zIndex: -996,
          }),
        draggable: false,
      });
      rfMarkerB.addTo(rfLayer)
      document.getElementById('rfTowerToLine').style.color="#000";
    }
    if (map.hasLayer(rfRect)) {
      rfRect.removeFrom(map);
      map.removeLayer(rfRect); 
    }
    if(rect_up != 0 &&rect_right != 0 && rect_down != 0 && rect_right != 0) {
      var bounds = [[rect_down,rect_left], [rect_up, rect_right]];
      rfRect = L.rectangle(bounds, {color:'#F00F',fill:false}).addTo(rfLayer);
      center_lat = (Number(rect_up)+Number(rect_down))/2;
      center_lon = (Number(rect_left)+Number(rect_right))/2;
      map.setView(new L.LatLng(center_lat,center_lon),9);
    }
    else {
      map.setView(new L.LatLng(Number(parameter[2]),Number(parameter[3])),9);
    }
    document.getElementById('side-draw-del-rect').style.display="inline";
    layers.addOverlay(rfLayer,"(RF)-visibility");
    rfLayer.addTo(map);

    document.getElementById("rf-loading").style.display = "none";   
    document.getElementById("rf-result").style.display = "inline";  
    var content = "<br><b>calculation \""+parameter[1]+"\" finished</b><br><a onclick='rfBack();'>back</a><br>"
    document.getElementById("rf-result").innerHTML=content;
    rfLoadPreset();
    rfLocked=0;
  }
}
function rfCreateUrl()
{
  var url = '';

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
    if (map.hasLayer(rfMarkerA)) {
      url = url + '&ma_lat=' + rfMarkerA._latlng['lat'] + '&ma_lon=' + rfMarkerA._latlng['lng'];
    }
    if (map.hasLayer(rfMarkerB)) {
      url = url + '&mb_lat=' + rfMarkerB._latlng['lat'] + '&mb_lon=' + rfMarkerB._latlng['lng'];
    }
    url = url + '&ma_tow=' + profileTowerA + '&mb_tow=' +  profileTowerB;
    url = url + '&rf_ref=' + rfRefraction;
    if (rfTowerRx != 0) {
      url = url + '&rf_rx=' + rfTowerRx;
    }
    if (rfLabel != '') {
      url = url + '&rf_lab=' + rfLabel;
    }
    var rfVisTreeOut;
    if (rfVisTree)
      rfVisTreeOut = 1;
    else
      rfVisTreeOut = 0; 
    url = url + '&rf_tree=' + rfVisTreeOut; 
    if(map.hasLayer(rfRect)) //if rectangle exists
    {
      url = url + '&rf_d=' + rfRect._bounds._southWest.lat;
      url = url + '&rf_l=' + rfRect._bounds._southWest.lng;
      url = url + '&rf_u=' + rfRect._bounds._northEast.lat;
      url = url + '&rf_r=' + rfRect._bounds._northEast.lng;
    }
  }
  else if(map.hasLayer(profileMa) && map.hasLayer(profileMb) && map.hasLayer(rfPanoramaPopup)){ //if panorama
    url = url + '&ma_lat=' + profileMa._latlng['lat'] + '&ma_lon=' + profileMa._latlng['lng'];
    url = url + '&mb_lat=' + profileMb._latlng['lat'] + '&mb_lon=' + profileMb._latlng['lng'];
    
    url = url + '&rf_p_ref=' + rfRefractionPanorama;

    if(rfAngle != "50")
    {
      url = url + '&rf_ang=' + rfAngle;
    }
    if(rfZoom != "1")
    {
      url = url + '&rf_z=' + rfZoom;
    }
    if(rfElevation != "0")
    {
      url = url + '&rf_el=' + rfElevation;
    }
    if (rfFontPanorama != 1) {
      url = url + '&rf_p_font=' + rfFontPanorama;
    }  
    url = url + '&rf_poi=' + rfPoiInput;
    url = url + '&rf_pan=1';
    if (rfSnow1 != 2500) {
      url= url + "&rf_snow1="+rfSnow1;
    }
    if (rfSnow2 != 500) {
      url = url +"&rf_snow2="+rfSnow2;
    }
    if (rfDesert) {
      url = url +"&rf_desert=1";
    }
    url = url + "&rf_sun_az="+rfSunAz+"&rf_sun_El="+rfSunEl;
  }
  return url;
}
function rfPoint(lat,lon) //point with marker to map
{
  deleteProfileMpos();
  latlngpos = new L.LatLng(lat, lon);
  profileMpos = L.marker(latlngpos, {
    icon: L.icon({
      iconUrl: 'osm/images/marker-red-round.png',
      iconSize: [16, 16],
      iconAnchor: [8, 8],
      zIndex: 9997,
    }),
    draggable: false,
    contextmenu: false
  }).addTo(map);
  profileMpos.setZIndexOffset(7099);
}
function rfOpenpanorama()
{
  if (map.hasLayer(profileMa) && map.hasLayer(profileMb)) {
    if((profileMa._latlng != null) && (profileMb._latlng != null)) {
      panoramaDraw();
    }
    else
      alert("At least one marker missing!");
  }
  else
    alert("At least one marker missing!");
}
function panoramaDraw()
{
  width = 650;
  height = 350;
  if ((typeof profileMa !== 'undefined') && (typeof profileMb !== 'undefined')) {
    if((profileMa._latlng != null) && (profileMb._latlng != null)) {
      if (typeof rfPanoramaPopup !== 'undefined') { //catch open popup
        if (rfPanoramaPopup._map !=null) {
          panoramaRedraw(width,height);
          return;
        }
      }
      rfValUpd();
      panoramaMetadata = new Array(); //init

      var lat1 = profileMa._latlng['lat'];
      var lon1 = profileMa._latlng['lng'];
      var lat2 = profileMb._latlng['lat'];
      var lon2 = profileMb._latlng['lng'];
      var customOptions ={
        className: 'popuppanorama',
        minWidth:550,
        maxWidth:550,
        maxHeight:250,
      }
      panoramalink=panoramaGenLink(width,height);
      panoramaCalc(panoramalink);

      var popupcontent="<span class='popup-darg'>drag and drop popup and markers &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;double-click on panorama to jump to location or open Webcam!</span> \
        <div id='panorama-loading'><img src='hdb.gif'\
          alt='loading...'/>calculating...</div>\
        <div><img id='panorama-img' src='' onmouseover='javascript:panoramaProcessMetadata(event);' \
        onmousemove='javascript:panoramaProcessMetadata(event);' ondblclick='javascript:panoramaProcessMetadata(event);'\
        onclick='javascript:panoramaProcessMetadata(event);' /></div>\
        <form id='panorama'>&nbsp;&nbsp;\
        <span id='panorama-updated'><input type='button' value='recalculate' style='height:24px' onclick='javascript:panoramaRedraw("+width+","+height+");' ></span>\
        &nbsp;&nbsp;<input type='button' value='open big Panorama' \
        style='height:24px' onclick='javascript:panoramaOpenBig();'></form>&nbsp;<span id='panorama-meta'></span>  ";

      rfPanoramaPopup = L.popup({
        closeButton: true,
        closeOnClick:false,
        autoClose: false,
        className: 'popupPanorama', 
        minWidth: width,
        //maxWidth: 650,
        Width: width,
        Height: (height+40),
      })
      .setLatLng([(Number(lat1) + Number(lat2))/2, (Number(lon1)+Number(lon2))/2])
      .setContent(popupcontent)
      .openOn(map);
    
      map.addLayer(rfPanoramaPopup);

      var pos = map.latLngToLayerPoint(rfPanoramaPopup._latlng);
      L.DomUtil.setPosition(rfPanoramaPopup._wrapper.parentNode,pos);
      var draggable = new L.Draggable(rfPanoramaPopup._container, rfPanoramaPopup._wrapper);
      draggable.enable();
      map.setView(new L.LatLng((Number(lat1) + Number(lat2))/2, (Number(lon1)+Number(lon2))/2));
      document.getElementById("panorama-loading").style.display = "inline"; 
      document.getElementById("panorama-img").src = "";
//      deleteProfileMpos();
    }
  }
}
function panoramaRedraw()
{
  panoramalink=panoramaGenLink(width,height);
  panoramaCalc(panoramalink);
  document.getElementById("panorama-loading").style.display = "inline"; 
  document.getElementById("panorama-img").src = "";
  panoramaMetadata = new Array(); //init
}
function rfPanoramaAdvanced() //toogle advanced menu
{
  adv = document.getElementById("panoramaAdv").style.display;
  if(adv == "block")
  {
    document.getElementById("panoramaAdv").style.display = "none";
  }
  else 
  {
    document.getElementById("panoramaAdv").style.display = "block"
  }  
}
function panoramaGenLink(width,height)
{
  if (map.hasLayer(profileMa) && map.hasLayer(profileMb)) {
    if((profileMa._latlng == null) || (profileMb._latlng == null)) {
      alert("At least one marker missing!");
      return;
    }
  }
  else
  {
    alert("At least one marker missing!");
    return;
  }
  var lat1 = profileMa._latlng['lat'];
  var lon1 = profileMa._latlng['lng'];
  var lat2 = profileMb._latlng['lat'];
  var lon2 = profileMb._latlng['lng'];
  var poi ="l"
  if (rfPoiHamnet)
    poi+="hamnet";
  if (rfPoiFWC)
    poi+="wc";
  if (rfPoiMT)
    poi+="mt";
  if (rfPoiSota)
    poi+="sota";
  if (rfPoi)
    poi+="small";
  rfPoiInput=poi; //also output to permalink

  if(rfDesert)
    rfDesertOut = 1;
  else 
    rfDesertOut = 0; 
  src = "?lon_a="+lon1+"&lat_a="+lat1+"&ant_a="+rfTowerFromP+"&poi="+poi+
        "&lon_b="+lon2+"&lat_b="+lat2+"&el="+rfElevation+"&angle="+rfAngle+"&z="+rfZoom+
        "&ref="+rfRefractionPanorama+"&font="+rfFontPanorama+
        "&desert="+rfDesertOut+"&snow1="+rfSnow1+"&snow2="+rfSnow2+
        "&sun_az="+rfSunAz+"&sun_el="+rfSunEl+"&y="+height+"&x="+width;
  return src;
} 
function panoramaCalc(url)
{
  src=host_calc_profile+"calc_panorama.cgi"+url;
  var xmlHttpP = new XMLHttpRequest();
  //xmlHttpP.timeout = 180000;
  xmlHttpP.open("GET", src, true); // true for asynchronous 
  xmlHttpP.send(null);
  xmlHttpP.onreadystatechange = function() { 
    if (xmlHttpP.readyState == 4 && xmlHttpP.status == 200) {
      panoramaCalcReady(url);
    }
  }
}
function panoramaCalcReady(url)
{
  document.getElementById("panorama-loading").style.display = "none"; 
  if (document.getElementById("panorama-img-parent") != null)
    document.getElementById("panorama-img-parent").style.display = "block"; 
  document.getElementById("panorama-img").src = host_calc_profile+"calc_panorama_image.cgi"+url;
  panoramaGetMeta(url);
}
function panoramaGetMeta(url)
{
  src=host_calc_profile+"calc_panorama_metadata.cgi"+url;
  var xmlHttpP = new XMLHttpRequest();
  //xmlHttpP.timeout = 180000;
  xmlHttpP.open("GET", src, true); // true for asynchronous 
  xmlHttpP.send(null);
  xmlHttpP.onreadystatechange = function() { 
    if (xmlHttpP.readyState == 4 && xmlHttpP.status == 200) {
      //xmlhttp.responseText;
      panoramaGotMetadata(xmlHttpP.responseText);
    }
  }
}
function panoramaGotMetadata(meta_content)
{
  //parse csv, => panorama array
  //panoramaMetadata[x][y]
  result = meta_content.split('\n');
  panoramaMetadata = []; //cleanup old content
  for (i = 0; i < result.length; i++) {
    //parse csv & fill object
    line = result[i].split(',');
    testg = result;
    pixelX = Number(line[0]);
    pixelY = Number(line[1]);
    if(typeof panoramaMetadata[pixelX] === 'undefined')
      panoramaMetadata[pixelX] = new Array();
    if(typeof panoramaMetadata[pixelX][pixelY] !== 'undefined')
    {
      if (typeof line[6] !== 'undefined' )
      {   
        if (line[6].length > 0)
        {
          pixelY +=1;
        }
      }
    }
    panoramaMetadata[pixelX][pixelY] = new Object();
    panoramaMetadata[pixelX][pixelY].lat = Number(line[2]);
    panoramaMetadata[pixelX][pixelY].lon = Number(line[3]);
    panoramaMetadata[pixelX][pixelY].hm = line[4];
    panoramaMetadata[pixelX][pixelY].info = line[5];
    panoramaMetadata[pixelX][pixelY].typ = line[6];
  }
}
function rfPanUpdForm()
{
  document.getElementById("rfTowerFromP").value = rfTowerFromP;
  document.getElementById("rfElevation").value = rfElevation;
  document.getElementById("rfAngle").value = rfAngle;
  document.getElementById("rfZoom").value = rfZoom;
  document.getElementById("rfSnow1").value = rfSnow1;
  document.getElementById("rfSnow2").value = rfSnow2;
  document.getElementById("rfDesert").checked = rfDesert;
}
function panoramaOpenBig()
{
  
  if (document.documentMode || /Edge/.test(navigator.userAgent)) 
  {
    alert('Does not work for Microsoft "Browsers"!');
  }
  else
  {
    newwindow=window.open('panorama.cgi','HamnetDB Panorama','width=650,height=410,toolbar=0,menubar=0,location=0');  
    if (window.focus) {newwindow.focus()}
  }
}
function panoramaBig()//create new panorama
{
  //recalc big image 
  //  get parameter from main window
  //  get window size or alternative size
  var height;
  var width;
  var prepare = true;
  document.getElementById("panorama-loading").style.display = "block"; 
  document.getElementById("panorama-img-parent").style.display = "none"; 
  document.getElementById("panorama-img-parent").src = ""; 
  if (document.getElementById('pan-custom').checked)
  {
    width = document.getElementById('pan-x-custom').value;
    height = document.getElementById('pan-y-custom').value;
    if (width > 6000)
    {
      document.getElementById('panorama-meta-big').innerHTML = "";
      document.getElementById('panorama-error').innerHTML = "max width = 6000px !!";
      prepare = false;
    }
    else if (height > 2160)
    {
      document.getElementById('panorama-meta-big').innerHTML = "";
      document.getElementById('panorama-error').innerHTML = "max height = 2160px !!";
      prepare = false;
    }
    else
    {
      //document.getElementById('panorama-meta').innerHTML = "";
      document.getElementById('panorama-error').innerHTML = "";
    }
  }
  else
  {
    height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    height -= 60;
  }
  if (prepare)
    channel.postMessage({cmd: 'preplnk', width: width, height: height, id: windowID})
}
function panoramaResize()
{
  var height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
  height = ""+(height - 50)+"px";
  if ( document.getElementById('panorama-img-parent')  != null)
  {
    document.getElementById('panorama-img-parent').style.height = height;
  }
  //#panorama-img  height: 350px;   width: 650px;
}
function panoramaBigChg() //manage input fields
{
  if (document.getElementById('pan-custom').checked)
  {
    document.getElementById('pan-x-custom').disabled=false;
    document.getElementById('pan-y-custom').disabled=false;
  }
  else
  {
    document.getElementById('pan-x-custom').disabled=true;
    document.getElementById('pan-y-custom').disabled=true;    
  }
}
function panoramaMsgInit() //setup messageing
{
  channel = new BroadcastChannel('panorama');
  channel.onmessage = panoramaGotMsg;
}
function panoramaBigInit()
{
  panoramaMsgInit();
  panoramaBig();
  document.getElementById('panorama-img-parent').style.display = 'none';
}
function panoramaGotMsg(msg)
{
  if (typeof msg.data.cmd !== 'undefined')
  {
    if (msg.data.cmd == 'preplnk')
    {
      var lnk = panoramaGenLink(msg.data.width,msg.data.height)
      channel.postMessage({ cmd: 'recalc', value: lnk, id: msg.data.id, lat: profileMa._latlng['lat'],lon: profileMa._latlng['lng'] });
    }
    if (msg.data.cmd == 'recalc')
    { 
      if (msg.data.id == windowID)
      {
        panoramaCalc(msg.data.value);
        panoramaResize();
        own_lat = msg.data.lat;
        own_lon = msg.data.lon;
      }
    }
    if (msg.data.cmd == 'point')
    {
      rfPoint(msg.data.lat,msg.data.lon);
    }
    if (msg.data.cmd == 'move')
    {
      map.setView([msg.data.lat, msg.data.lon], 13);

    }
  }
}
function panoramaProcessMetadata(event)
{
  //also trigger on click => center map
  img = document.getElementById("panorama-img");
  pos_x = event.offsetX?(event.offsetX):event.pageX-img.offsetLeft;
  pos_y = event.offsetY?(event.offsetY):event.pageY+img.offsetTop;
  pos_y = parseInt(img.offsetHeight-pos_y);
  //check region x, y,  
  pixel = checkArray(panoramaMetadata,pos_x,pos_y);

  if(pixel.length > 0)
  {
    var link = "";

    if ( typeof panoramaMetadata[pixel[0][0]][pixel[0][1]].info === 'undefined') //generic poi no name
    {
     link = ""; 
    }
    else if(panoramaMetadata[pixel[0][0]][pixel[0][1]].info.includes('Webcam'))//if POI==webcam
    {
      wc = panoramaMetadata[pixel[0][0]][pixel[0][1]].info.split(' ');
      link = "POI: <a href='"+panoramaMetadata[pixel[0][0]][pixel[0][1]].info.split(';')[1]+"' target='_blank'>"+panoramaMetadata[pixel[0][0]][pixel[0][1]].info.split(';')[0]+"</a>";  
      if (event.type == 'dblclick')
      {
        var win = window.open(panoramaMetadata[pixel[0][0]][pixel[0][1]].info.split(';')[1], '_blank');
        win.focus();
      }
    }
    else //no webcam
      link = "POI: "+panoramaMetadata[pixel[0][0]][pixel[0][1]].info;
    //meters above sea level
    var hm = '';
    if (panoramaMetadata[pixel[0][0]][pixel[0][1]].hm.length > 0)
      hm = panoramaMetadata[pixel[0][0]][pixel[0][1]].hm+"m "
    else 
      hm = '';
    //catch small panorama
    if (typeof own_lat === 'undefined')
    {
      own_lat = profileMa._latlng['lat'];
      own_lon = profileMa._latlng['lng'];
    }
    distance = getDistance(panoramaMetadata[pixel[0][0]][pixel[0][1]].lat,panoramaMetadata[pixel[0][0]][pixel[0][1]].lon,own_lat,own_lon);
    link = distance.toFixed(2)+"km "+hm+link; //+'x:'+pixel[0][0]+'y:'+pixel[0][1];
    //if BIG-panorama window
    if(window.location.pathname.includes('panorama.cgi'))
    {
      channel.postMessage({ cmd: 'point', lat: panoramaMetadata[pixel[0][0]][pixel[0][1]].lat, lon: panoramaMetadata[pixel[0][0]][pixel[0][1]].lon });
      document.getElementById('panorama-meta-big').innerHTML = link;
      //move map on click
      if (event.type == 'dblclick')
      {
        channel.postMessage({ cmd: 'move', lat: panoramaMetadata[pixel[0][0]][pixel[0][1]].lat, lon: panoramaMetadata[pixel[0][0]][pixel[0][1]].lon });
      }
    }
    else //inline popup
    {
      rfPoint(panoramaMetadata[pixel[0][0]][pixel[0][1]].lat, panoramaMetadata[pixel[0][0]][pixel[0][1]].lon);
      document.getElementById('panorama-meta').innerHTML = link;
      //move map on click
      if (event.type == 'dblclick')
      {
        map.setView([panoramaMetadata[pixel[0][0]][pixel[0][1]].lat, panoramaMetadata[pixel[0][0]][pixel[0][1]].lon]);
        rfPanoramaPopup.setLatLng([panoramaMetadata[pixel[0][0]][pixel[0][1]].lat, panoramaMetadata[pixel[0][0]][pixel[0][1]].lon]);
      }
    }
    //point to metapixel debug only
    //document.getElementById('rf-point').style.left = pixel[0][0]+5+'px';
    //document.getElementById('rf-point').style.top = img.offsetHeight-pixel[0][1]+20+'px';
  }
}
function checkArray(input,x,y)
{
  output = new Array();
  x_cnt = [0,1,-1,2,-2,3,-3,4,-4,5,-5];
  for (i=0;i<x_cnt.length;i++)
  {
    if (typeof input[x+x_cnt[i]] !== 'undefined')//x is valid
    {
      for (j=y+2;j>=y-29;j--)
      {
        if (typeof input[x+x_cnt[i]][j] !== 'undefined')//y  is valid
        {
          delta = Math.abs(j-y);
          if (input[x+x_cnt[i]][j].typ !== 'undefined')   
          {        
            if (delta < 29 && input[x+x_cnt[i]][j].typ == "wc")
            {
              output[0]=[x+x_cnt[i],j];
            }
            else if (delta < 14 && input[x+x_cnt[i]][j].typ == "h") //hamnet //bigger poi for webcam
            {
              output[0]=[x+x_cnt[i],j];
              return output;
            }
            else if (delta < 7 && input[x+x_cnt[i]][j].typ == "MT")
              output.push([x+x_cnt[i],j]);
            else if (delta < 8 && input[x+x_cnt[i]][j].typ == "sota")
              output.push([x+x_cnt[i],j]);
            else if (delta < 5) //generic poi
              output.push([x+x_cnt[i],j]);
          }
        }
      }
    }
  }
  //console.log(output);
  return output;
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
function getFullscreen()
{
  elem=document.getElementById("map");

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
function getDistance(lat1,lon1,lat2,lon2) {
  var r = 6371;     
  var pi = Math.atan2(1,1)*4;

  lat1= lat1  * (pi/180);
  lon1= lon1 * (pi/180);
  lat2= lat2  * (pi/180);
  lon2= lon2 * (pi/180);

  return Math.acos(Math.cos(lat1)*Math.cos(lon1)*Math.cos(lat2)*Math.cos(lon2) + Math.cos(lat1)*Math.sin(lon1)*Math.cos(lat2)*Math.sin(lon2) + Math.sin(lat1)*Math.sin(lat2)) * r;
}
