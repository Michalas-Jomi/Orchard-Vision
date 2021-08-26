class HarvestTime {
    constructor(title, start, end) {
        function date(str) {
            let m = str.match(/(\d{2})-(\d{2})-(\d{4})/)
            return new Date(m[3], m[2] - 1, m[1]);
        }

        this.title = title;
        this.start = date(start);
        this.end = date(end);

        if (this.end.getTime() < this.start.getTime())
            this.end.setFullYear(this.end.getFullYear() + 1);
    }

    compare(harvest) {
        if (this.start > harvest.start) return +1;
        if (this.start < harvest.start) return -1;
        if (this.end > harvest.end)     return +1;
        if (this.end < harvest.end)     return -1;
        return 0;
    }

    /**
     * chceck a date is beetwend start and end of harvestTime
     * 
     * @param {Date} date 
     * @returns {Boolean} true if harvest Time contains date
     */
    contains(date) {
        date.setFullYear(this.start.getFullYear());
        date = date.getTime();
        return date >= this.start.getTime() && date <= this.end.getTime();
    }
}