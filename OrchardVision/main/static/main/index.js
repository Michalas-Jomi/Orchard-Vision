var _infoCounter = 0
var curRequestId = undefined
window.addEventListener('click', ev => {
    let target = ev.target;
    while (target && target != document) {
        if (target.classList.contains('model_url')) {
            ev.preventDefault();
            
            let url = target.href;
            let id = _infoCounter++;
            curRequestId = id;
    
            const XHR = new XMLHttpRequest();
            XHR.addEventListener('load', response => {
                if (id === curRequestId)
                    document.getElementById('info').innerHTML = response.target.response;
            });
            XHR.open('GET', url);
            XHR.send();
            break;
        }
        target = target.parentNode;
    }
});

var x;
window.addEventListener('DOMContentLoaded', ev => {
    let types = document.getElementsByClassName('type')
    let max_width = 1200;
    max_width -= types.length + 1
    let width = max_width / types.length

    for (type of types) {
        type.style.width = width + "px";
    }

    
    // #info z-index
    let info = document.getElementById('info');
    let listenerIn = ev => { info.style.setProperty('z-index', -1); };
    let listenerOut = ev => { info.style.setProperty('z-index', 0); };
    for (let li of document.getElementsByClassName("type")) {
        li.onmouseover = listenerIn;
        li.onmouseout  = listenerOut;
        console.log(li)
    }
});
