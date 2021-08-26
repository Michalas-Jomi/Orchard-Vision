/// <reference types="../../../../types/google.maps" />

/** @type { google.maps.InfoWindow } */
var infoWindow = null;
/** @type { google.maps.Map } */
var map = null;

var treesSummary = null;

function applyFilters() {
   if (map === null) return;

   var visible = 0;

   trees.forEach(tree => {
      tree.applyFilters(filters);
      if (tree.marker)
         visible += tree.marker.getVisible();
   });

   if (treesSummary)
      treesSummary.innerHTML = `Drzewa: ${visible}/${trees.length} (${Math.round(visible / trees.length * 100)}%)`;
}

function generateLinkWithFilters() {
   let url = mapUrl + '?';
   let allOn = true;

   for (type in filters)
      for (variant in filters[type]) {
         let on = filters[type][variant];
         allOn  = allOn  &&  on;

         if (on) {
            if (!url.endsWith('?'))
               url += '&';
            url += `filter_${encodeURI(type)}=${encodeURI(variant)}`; 
         }
      }

   if (url.endsWith('?'))
      url += encodeURI("type_filter_")
   url = allOn ? mapUrl + '?' : url;

   if (filter_harvest_time)
      for (let id in harvests)
         if (harvests[id] === filter_harvest_time) {
            allOn = false;
            if (!url.endsWith('?'))
               url += '&';
            url += 'harvest=' + id;
            break;
         }
   return url;
}

function centerMap() {
   if (!map) return;

   let bounds = new google.maps.LatLngBounds();
   let empty = true;

   trees.forEach(tree => {
      if (tree.marker.visible) {
         bounds.extend(tree.marker.position)
         empty = false;
      }
   })
   if (empty)
      trees.forEach(tree => bounds.extend(tree.marker.position))

   map.fitBounds(bounds);
}

function autoSelectHarvestTime(value) {
   let select = document.getElementById('select_harvestTime_filter');
   select.childNodes.forEach(child => {
      if (child.value == value) {
         child.setAttribute('selected', '');
      } else {
         child.removeAttribute('selected');
      }
   });
}

function initFilters() {
   let def = Object.keys(filters).length === 0 && type_filters.length === 0
   trees.forEach(tree => {
      if (!(tree.type in filters))
         filters[tree.type] = {};
      if (type_filters.includes(tree.type))
         filters[tree.type][tree.variant] = true;
      else if (!(tree.variant in filters[tree.type]))
         filters[tree.type][tree.variant] = def;
   });

   /// apply functionals to aside buttons
   document.getElementById('get_filters_link').addEventListener('click', ev => {
      if (navigator)
         navigator.clipboard.writeText(generateLinkWithFilters()).then(() => alert('Skopiowano link'));
      else
         alert('Czynność niedostępna, użyć innej przeglądarki');
   });
   document.getElementById('center_button').addEventListener('click', centerMap);
   document.getElementById('currentHarvest_button').addEventListener('click', ev => {
      const now = new Date();

      function finalize() {
         autoSelectHarvestTime(filter_harvest_time);
         filter_harvest_time = harvests[filter_harvest_time];
         applyFilters();
      }

      for (const id in harvests)
         if (id == -1)
            continue;
         else if (harvests[id].contains(now)) {
            filter_harvest_time = id;    
            finalize();
            return;
         }
      filter_harvest_time = -1;
      finalize();
   });

   /// making view in DOM
   const root = document.getElementById('filters');

   // treesSummary
   treesSummary = root.appendChild(document.createElement('div'));
   treesSummary.classList.add('summary');
   
   applyFilters();
   
   // type / variant
   let types = document.createElement('ol');
   types.classList.add('types');
   types.classList.add('filter');
   root.appendChild(types);

   function makeLabel(text, listener) {
      let label = document.createElement('label');
      label.textContent = text;

      let checkbox = document.createElement('input')
      checkbox.type = 'checkbox';
      label.appendChild(checkbox);

      label.addEventListener('click', ev => {
         if (ev.target.tagName === "INPUT") {
            listener(ev.target);
            applyFilters();
         }
      });

      return label;
   }
   function checkTypeCheckbox(typeOl) {
      let parentCheckbox = typeOl.parentNode.children[1].lastChild;
      for (let li of typeOl.children) 
         if (!li.lastChild.lastChild.checked) {
            parentCheckbox.checked = false;
            return;
         }
      parentCheckbox.checked = true;
   }
   function makeFoldButton(typeLi) {
      let button = document.createElement('button');
      button.textContent = '-';

      function foldDown() {
         button.textContent = "+";
         typeLi.lastChild.style.display = "none";
      }
      function foldUp() {
         button.textContent = "-";
         typeLi.lastChild.style.display = "block";
      }

      button.addEventListener('click', ev => {
         if (button.textContent === '+')
            foldUp();
         else
            foldDown();
      });

      typeLi.appendChild(button)
   }

   for (let type in filters) {
      let typeLi = document.createElement('li');
      types.appendChild(typeLi);

      makeFoldButton(typeLi);

      let __type = type;
      let typeOl = document.createElement('ol');
      typeLi.appendChild(makeLabel(type, el => {
         for (let variant in filters[__type]) filters[__type][variant] = el.checked;
         for (let li of typeOl.children)      li.lastChild.lastChild.checked = el.checked;
      }));
      typeLi.appendChild(typeOl);
      

      for (let variant in filters[type]) {
         let variantLi = document.createElement('li');
         let _variant = variant;
         let _type = type;
         variantLi.appendChild(makeLabel(variant, el => {
            filters[_type][_variant] = el.checked;
           
            let typeOl = el.parentNode.parentNode.parentNode;
            checkTypeCheckbox(typeOl);
         }));
         variantLi.lastChild.lastChild.checked = filters[type][variant];
         typeOl.appendChild(variantLi);
      }
      checkTypeCheckbox(typeOl);
   }

   // harvestTime
   let hroot = root.appendChild(document.createElement('label'));
   hroot.textContent = "Zbiór:";

   let select = hroot.appendChild(document.createElement('select'));
   select.setAttribute('id', 'select_harvestTime_filter');
   select.classList.add('harvest_time');
   
   // Sorting harvest times
   const harvestsList = []
   for (const harvestId in harvests) {
      harvestsList.push({id: harvestId, obj: harvests[harvestId]})
   }
   harvestsList.sort((a, b) => {
      if (a.obj && b.obj)
         return a.obj.compare(b.obj);
      return a.obj == null ? -1 : 1;
   });

   // making view for harvest time
   harvestsList.forEach(harvest => {
      let option = select.appendChild(document.createElement('option'));
      option.value = harvest.id;
      if (harvest.id == -1)
         option.innerHTML = "Brak";
      else
         option.innerHTML = harvest.obj.title;
      if (filter_harvest_time == harvest.id || (filter_harvest_time === null && harvest.id == -1))
         option.setAttribute('selected', '');
   });

   select.addEventListener('change', ev => {
      let index = ev.target[ev.target.selectedIndex].value;
      filter_harvest_time = index == -1 ? null : harvests[index];
      applyFilters();
   })

   // post

   autoSelectHarvestTime(filter_harvest_time);
   filter_harvest_time = harvests[filter_harvest_time];
}

var asyncDone = 0;
function initAsync() {
   if (++asyncDone == 2) {
      centerMap();
      initFilters();
   }
}
function initTrees() {
   initAsync();
}
function initMap() {
   class InfoWindow extends google.maps.InfoWindow {
      open(a, b) {
         this.visible = true;
         super.open(a, b);
      }
      close() {
         this.visible = false;
         super.close();
      }
   }

   map = new google.maps.Map(document.getElementById("map"), {
      mapTypeId: 'hybrid',

      disableDefaultUI: true,

      rotateControl: true,
      scaleControl: true,
      zoomControl: true,
      
      mapTypeControl: false,
      fullscreenControl: false,
      streetViewControl: false,
   });

   map.addListener('click', ev => {
      if (infoWindow.visible) {
         infoWindow.close();
      } else {
         infoWindow.setContent('Wczytywanie formularza');
         infoWindow.setPosition(ev.latLng);
         infoWindow.open(map);
   
         Utils.send('GET', treeNewUrl + `?lat=${ev.latLng.lat()}&lng=${ev.latLng.lng()}`, {}, 
               response => infoWindow.setContent(response.target.response),
               err => infoWindow.setContent('Wystąpił problem podczas pobierania formularza')
         );
      }
   });

   infoWindow = new InfoWindow();

   trees.forEach(tree => tree.makeMarker());
   initAsync();
}
