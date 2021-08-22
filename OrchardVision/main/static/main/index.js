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
    
            Utils.send('GET', url, {}, response => {
                if (id === curRequestId) {
                    let info = document.getElementById('info');
                    info.innerHTML = response.target.response;
                    
                    let forms = info.getElementsByTagName("form");
                    for (const form of forms)
                        form.addEventListener('submit', ev => {
                            ev.preventDefault();
                            Utils.sendForm(ev.target.method, ev.target.action, new FormData(ev.target), response => {
                                window.location.reload();
                            }, err => {
                                alert('Nie udało się wykonać operacji');
                            });
                        });
                }

            });
            break;
        } else if (target.classList.contains('needReload') || target.classList.contains('needReloadYesNo')) {
            ev.preventDefault();
            if (!target.classList.contains('needReloadYesNo') || confirm('Jesteś pewnien?'))
                Utils.send('GET', target.href, {}, () => window.location.reload(), err => alert('Nie udało się wykonać operacji'));
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
    }
});
