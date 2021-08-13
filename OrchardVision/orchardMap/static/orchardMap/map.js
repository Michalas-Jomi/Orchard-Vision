function initMap() {
   map = new google.maps.Map(document.getElementById("map"), {
      center: { lat: 52.8319872, lng: 20.8208321 },
      zoom: 20,
      mapTypeId: 'hybrid',

      disableDefaultUI: true,

      rotateControl: true,
      fullscreenControl: true,
      scaleControl: true,
      zoomControl: true,

      mapTypeControl: false,
      streetViewControl: false,
  });

  infoWindow = new google.maps.InfoWindow();

  trees.forEach(tree => tree.makeMarker(map));
}
