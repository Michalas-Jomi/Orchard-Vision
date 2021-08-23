/// <reference types="../../../../types/google.maps" />

class Tree {
    constructor(id, type, variant, lat, lng) {
        this.id = id;
        this.type = type;
        this.variant = variant;
        this.pos = {lat: lat, lng: lng};
        /** @type { google.maps.Marker } */
        this.marker = null;

        this.makeMarker()
    }

    applyFilters(filters) {
        this.marker.setVisible(filters[this.type][this.variant])
    }

    showInfoWindow() {
        let tree = this;
        let marker = this.marker;

        infoWindow.close();
        infoWindow.setContent(Utils.htmlentities(this.variant));
        infoWindow.open(marker.getMap(), marker);

        Utils.send('GET', '/map/treeInfo/' + this.id, {}, response => {
            infoWindow.setContent(response.target.response);

            function search(items) {
                for (let i=0; i < items.length; i++) {
                    let item = items.item(i);
                    let parent = item.parentNode;
                    while (parent && parent.id != 'treeInfoContainer') {
                        parent = parent.parentNode;
                    }
                    if (parent)
                        return item;
                }
                throw new ErrorEvent();
            }

            let del = search(document.getElementsByClassName('delete'));
            let move = search(document.getElementsByClassName('move'));
            let copy = search(document.getElementsByClassName('copy'));

            del.addEventListener('click', ev => {
                if (confirm('Czy na pewno chcesz usunąć to drzewo?')) {
                    infoWindow.close()
                    let url = treeDeleteUrl + tree.id;
                    Utils.send('GET', url, {}, ev => {
                        for (let i=0; i < trees.length; i++) {
                            if (trees[i].id == tree.id) {
                                trees.splice(i, 1);
                                marker.setVisible(false);
                                break;
                            }
                        }
                    }, ev => alert('Nie udało się usunąć drzewa'))
                }
            });
            move.addEventListener('click', ev => {
                marker.setDraggable(true);
                infoWindow.close()
                marker.addListener('mouseup', ev => {
                    if (marker.draggable) {
                        marker.setDraggable(false)
                        let data = {id: tree.id, lat: marker.position.lat(), lng: marker.position.lng()}
                        Utils.send('POST', treeMoveUrl, data, loadResponse => {
                            tree.pos = {lat: data.lat, lng: data.lng}
                        }, errResponse => {
                            alert('Nie udało się przesunąć drzewa');
                            marker.setPosition(tree.pos);
                        });
                    }
                });
            });
            copy.addEventListener('click', ev => {
                let listener;
                ev.preventDefault();
                alert('Wybierz miejsce');
                infoWindow.close();
                trees.forEach(tree => tree.marker.setVisible(false));
                listener = map.addListener('click', ev => {
                    listener.remove();
                    applyFilters();

                    let fail = err => alert('Nie udało się skopiować drzewa');

                    Utils.send('GET', treeInfoUrl + tree.id, {}, response => {
                        let json = JSON.parse(response.target.response);

                        let data = {
                            latitude: ev.latLng.lat(),
                            longitude: ev.latLng.lng(),
                            type: tree.type,
                            variant: tree.variant,
                            planting_date: json['planting_date'],
                            note: json['note'],
                        };

                        Utils.send('POST', treeNewBrokerUrl, data, response => {
                            let id = parseInt(response.target.response);
                            if (!id) {
                                fail();
                                return;
                            }
                            let newTree = new Tree(id, tree.type, tree.variant, data.latitude, data.longitude);
                            trees.push(newTree);
                            newTree.applyFilters(filters);
                            if (newTree.marker && newTree.marker.getVisible())
                                newTree.showInfoWindow(); 
                        }, fail);
                    }, fail);
                })
            });
        });
    }

    makeMarker() {
        if (!map || this.marker) return;

        let marker = new google.maps.Marker({
            map: map,
            position: this.pos,
            title: this.info,
            icon: treeMarkerUrl,
        });

        let tree = this;

        marker.addListener('click', () => tree.showInfoWindow());

        this.marker = marker

        return marker;
    }
}