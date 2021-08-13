var _infoCounter = 0
var curRequestId = undefined
window.addEventListener('click', ev => {
    if (ev.target.classList.contains('model_url')) {
        ev.preventDefault();
        
        let url = ev.target.href;
        let id = _infoCounter++;
        curRequestId = id;

        const XHR = new XMLHttpRequest();
        XHR.addEventListener('load', response => {
            if (id === curRequestId)
                document.getElementById('info').innerHTML = response.target.response;
        });
        XHR.open('GET', url);
        XHR.send();
    }
});