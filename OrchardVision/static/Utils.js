class Utils {
    /**
     * 
     * @param {String} action 
     * @param {Object} data 
     * @param {Function} load 
     * @param {Function} error 
     */
     static send(method, url, data = {}, load = null, error = null) {
        const XHR = new XMLHttpRequest(), FD  = new FormData();
        XHR.addEventListener('load', load);
        XHR.addEventListener('error', error);
        for (let key in data)
            FD.append(key, data[key]);
        XHR.open(method, url);
        XHR.send(FD);
    }

    static htmlentities(str) {
        return str.replace(/[\u00A0-\u9999<>\&]/g, function(i) {
            return '&#' + i.charCodeAt(0) + ';';
         });
    }
}