/// <reference types="../../../../types/google.maps" />

/** @type { google.maps.InfoWindow } */
var infoWindow = null;
/** @type { google.maps.Map } */
var map = null;

function applyFilters() {
   if (map === null) return;

   trees.forEach(tree => tree.applyFilters(filters));
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
      return url + encodeURI("type_filter_")
   return allOn ? mapUrl : url;
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
   
   applyFilters();

   // apply functionals to aside buttons
   document.getElementById('get_filters_link').addEventListener('click', ev => {
      if (navigator)
         navigator.clipboard.writeText(generateLinkWithFilters()).then(() => alert('Skopiowano link'));
      else
         alert('Czynność niedostępna, użyć innej przeglądarki');
   });
   document.getElementById('center_button').addEventListener('click', centerMap);

   // making view in DOM
   const root = document.getElementById('filters');
   
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
}
function initMap() {
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
      infoWindow.close();
      infoWindow.setContent('Wczytywanie formularza');
      infoWindow.setPosition(ev.latLng);
      infoWindow.open(map);

      Utils.send('GET', treeNewUrl + `?lat=${ev.latLng.lat()}&lng=${ev.latLng.lng()}`, {}, 
            response => infoWindow.setContent(response.target.response),
            err => infoWindow.setContent('Wystąpił problem podczas pobierania formularza')
      );
   });

   infoWindow = new google.maps.InfoWindow();

   trees.forEach(tree => tree.makeMarker(map));

   initFilters();

   centerMap();
}
