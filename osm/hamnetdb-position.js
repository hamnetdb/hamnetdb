function init(netsource,store_lat,store_lon)
{  
  var map;
  var kmlUrl = "mapelements.cgi?geojson=1&rnd="+Math.random();
  var marker_exists = 0;
  var source
  if(netsource)
  {
    source = 3
  }
  else
  {
    source = 1;
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
    var mapnikUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var landscapeUrl = 'http://{s}.tile3.opencyclemap.org/landscape/{z}/{x}/{y}.png';
    var cycleUrl = 'http://{s}.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png';
    var satUrl= 'http://oatile1.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.jpg';
    var mapnikZoom = 18;
    var landscapeZoom =18;
    var cycleZoom = 18;
    var satZoom = 11;
  }
  
  var attribution = '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'; 
  map = new L.Map('map', {center: new L.LatLng(49.26, 12.47), zoom: 7, zoomControl:false});
  //plugin MousePosition
  //L.control.mousePosition({position: 'bottomright'}).addTo(map);
  //zoombutton top right
  L.control.zoom({position: 'topright'}).addTo(map);
  //scale
  L.control.scale().addTo(map);
  var marker = new L.FeatureGroup();
  
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
  var satLayer = L.tileLayer(
    satUrl,
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
  }
    
  //var hamnetLayer = new L.KML(kmlUrl + "&no_tunnel=1&only_hamnet=1", {async: true, hover:hoverS});
  var settingshamnet = {
    style: function(feature) {
      var color, weight;
      switch (feature.properties.style)
      {
        case "Tunnel":
          color = "#808080";
          weight = 3.5;    
          break;
        case "Routing-Radio":
          color = "#1d97ff";
          weight = 6;
          break;        
        case "Routing-Tunnel":
          color = "#808080";
          weight = 3.5;
          break;
        case "Radio":
          color = "#1d97ff";
          weight = 6;
          break;
        case "Routing-ISM":
          color = "#ad00e1";
          weight = 6;
          break;
        case "ISM":
          color = "#ad00e1";//d800ff
          weight = 6;
          break;
        default:
          color = "#f00000";
          weight = 6;
      } 
      return {color: color, weight:weight};//feature.properties.GPSUserColor};
    },
    pointToLayer: function(feature, latlng) {
      return L.marker(latlng, {icon: L.icon({
          iconUrl: feature.properties.style+'.png',
          iconSize: [19, 25],
          iconAnchor: [10, 16],
          popupAnchor: [0, 0]
        }),
        zIndexOffset:feature.properties.zIndex 
      });

    },
    onEachFeature: function (feature, layer) {
    layer.bindPopup(feature.properties.callsign,
        
        {
          minWidth:100,
          maxWidth:150,
          maxHeight:250,
          autoPan:true
        });
      layer.on('popupopen', function (e) {
        
      });
      
    }
  };
  var hamnetLayer = L.geoJson.ajax(kmlUrl + "&no_tunnel=1&only_hamnet=1", settingshamnet);
  var nohamnetLayer = L.geoJson.ajax(kmlUrl + "&no_tunnel=1&no_radio=1&no_hamnet=1&no_ism=1", settingshamnet);
  var tunnelLayer = L.geoJson.ajax(kmlUrl + "&no_radio=1&only_hamnet=1&no_hamnet=1&no_ism=1", settingshamnet);

  //map.addLayer(hamnetLayer);
  
  map.addLayer(mapnikLayer);
 
  if(source <=1)
  {
      
    var gglLayer = new L.Google('ROADMAP');
    var ggl2Layer = new L.Google('TERRAIN');
    var ggl3Layer = new L.Google('SATELLITE');
    var baseLayers = {  
      'Mapnik': mapnikLayer,
      'Landscape': landscapeLayer,
      'CycleMap':cycleLayer,
      'Satellite':satLayer,
      'GoogleMaps': gglLayer,
      'Google Terrain': ggl2Layer,
      'Google Sattelite': ggl3Layer
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
      'Satellite':satLayer
    };
  }
  var overlayLayers = {
    'Hamnet': hamnetLayer,
    'tunnel connections': tunnelLayer,
    'sites without Hamnet': nohamnetLayer
  };
  maker_icon = L.icon({
    iconUrl: 'osm/images/marker-red.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [0, 0]
  });
  map.on("click", function(e) {
    //alert("sd")
    if(marker_exists)
    {
      marker_exists = 0;
      map.removeLayer(marker);
    }
    if(!marker_exists)
    {
      marker_exists = 1;
      marker = new L.marker([e.latlng.lat, e.latlng.lng],{
      icon: maker_icon,
        draggable: true
      }).addTo(map);
      marker.on("dragend", function(e){
      var marker_tmp = e.target;
      var position = marker_tmp.getLatLng();
      makemarker(position.lat,position.lng);
    });

      makemarker(e.latlng.lat, e.latlng.lng); 
    } 
  });
  //map.panTo(new L.LatLng(position.lat, position.lng));  
  if(store_lon != 0 && store_lat != 0)
  {
    marker_exists = 1;
    marker = new L.marker([store_lat, store_lon],{
      icon: maker_icon,
      draggable: true
    }).addTo(map);
    makemarker(store_lat,store_lon);
    //map.panTo(new L.LatLng(store_lat, store_lon),12);
    map.setView([store_lat, store_lon],15);
  }
   
  var layers = new L.control.layers(baseLayers, overlayLayers).addTo(map);
}
function makemarker(lat,lng)
{
  lat = parseFloat(lat).toFixed(5);
  lng = parseFloat(lng).toFixed(5);
  //var result = document.getElementById('positionresult');
  loc = calcLocator(lat,lng);
  document.getElementById('lat_to_store').innerHTML = lat;
  document.getElementById('lon_to_store').innerHTML = lng;
  document.getElementById('locator_to_store').innerHTML = loc;
  to_store_lat = lat;
  to_store_lon = lng;
}
