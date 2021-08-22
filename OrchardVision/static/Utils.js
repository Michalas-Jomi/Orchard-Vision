class Utils {
    /**
     * 
     * @param {String} action 
     * @param {Object} data 
     * @param {Function} load 
     * @param {Function} error 
     */
     static send(method, url, data = {}, load = null, error = null) {
        const FD = new FormData();
        for (let key in data)
            FD.append(key, data[key]);
        return Utils.sendForm(method, url, FD, load, error);
    }
    static sendForm(method, url, form, load = null, error = null) {
        const XHR = new XMLHttpRequest();
        XHR.addEventListener('load', load);
        XHR.addEventListener('error', error);
        XHR.open(method, url);
        XHR.send(form);

    }

    static htmlentities(str) {
        return str.replace(/[\u00A0-\u9999<>\&]/g, function(i) {
            return '&#' + i.charCodeAt(0) + ';';
         });
    }
}