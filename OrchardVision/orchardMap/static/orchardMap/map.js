var infoWindow = null;
var map = null;
var filters = {}

function applyFilters() {
   if (map === null) return;

   trees.forEach(tree => tree.applyFilters(filters));
}


function initFilters() {
   trees.forEach(tree => {
      if (!(tree.type in filters))
         filters[tree.type] = {};
      if (!(tree.variant in filters[tree.type]))
         filters[tree.type][tree.variant] = true;
   });
   
   applyFilters()

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

  initFilters()
}
