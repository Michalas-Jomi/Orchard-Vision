class Tree {
    constructor(id, type, variant, lat, lng) {
        this.id = id;
        this.type = type;
        this.variant = variant;
        this.pos = {lat: lat, lng: lng};
        this.marker = null;
    }

    applyFilters(filters) {
        this.marker.setVisible(filters[this.type][this.variant])
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
            infoWindow.setContent(Utils.htmlentities(this.variant));
            infoWindow.open(marker.getMap(), marker);

            Utils.send('GET', '/map/treeInfo/' + this.id, {}, response => infoWindow.setContent(response.target.response));
        });

        this.marker = marker

        return marker;
    }
}