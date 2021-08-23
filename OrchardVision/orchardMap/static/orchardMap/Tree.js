class Tree {
    constructor(id, type, variant, lat, lng) {
        this.id = id;
        this.type = type;
        this.variant = variant;
        this.pos = {lat: lat, lng: lng};
        this.marker = null;

        this.makeMarker()
    }

    applyFilters(filters) {
        this.marker.setVisible(filters[this.type][this.variant])
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

        marker.addListener('click', () => {
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

                del.addEventListener('click', ev => {
                    if (confirm('Czy na pewno chcesz usunąć to drzewo?')) {
                        infoWindow.close()
                        let url = treeDeleteUrl + tree.id;
                        Utils.send('GET', url, {}, ev => {
                            for (let i=0; i < trees.length; i++) {
                                if (trees[i].id == tree.id) {
                                    delete trees[i];
                                    marker.setVisible(false);
                                    break;
                                }
                            }
                        }, ev => {
                            alert('Nie udało się usunąć drzewa');
                        })
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
            });
        });

        this.marker = marker

        return marker;
    }
}