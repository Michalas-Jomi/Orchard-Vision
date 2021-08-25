class HarvestTime {
    constructor(title, start, end) {
        function date(str) {
            let m = str.match(/(\d{2})-(\d{2})-(\d{4})/)
            return new Date(m[3], m[2], m[1]);
        }

        this.title = title;
        this.start = date(start);
        this.end = date(end);
    }

    compare(harvest) {
        if (this.start > harvest.start) return +1;
        if (this.start < harvest.start) return -1;
        if (this.end > harvest.end)     return +1;
        if (this.end < harvest.end)     return -1;
        return 0;
    }
}