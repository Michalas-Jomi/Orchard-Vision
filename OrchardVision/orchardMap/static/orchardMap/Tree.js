class Tree {
    constructor(id, info, lat, lng) {
        this.id = id;
        this.info = info;
        this.pos = {lat: lat, lng: lng};
    }

    makeMarker(map) {
        let marker = new google.maps.Marker({
            map: map,
            position: this.pos,
            title: this.info,
            icon: treeMarkerUrl,
        });

        marker.addListener('click', () => {
            infoWindow.close();
            infoWindow.setContent(Utils.htmlentities(this.info));
            infoWindow.open(marker.getMap(), marker);

            Utils.send('GET', '/map/treeInfo/' + this.id, {}, response => infoWindow.setContent(response.target.response));
        });

        return marker;
    }
}