/** @odoo-module **/

import { useBus, useService } from "@web/core/utils/hooks";
import { Component, useState, onWillUnmount } from "@odoo/owl";
const { DateTime } = luxon;


export class Header extends Component {
    static template = "odoo_project.ProjectLargeScreen.Header";
    static props = {
        title: { type: String },
    };
    setup() {
        this.dm = useService("drawer_menu");
        this.state = useState({ currentDateTtime: this.getCurrentTime() });
        this.timeInterval = setInterval(() => (this.state.currentDateTtime = this.getCurrentTime()), 1000);

        onWillUnmount(() => {
            clearInterval(this.timeInterval);
        });
    }

    getCurrentTime() {
        /*
        * @see https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/DateTimeFormat
        * @param formatOpts {Object} - Intl.DateTimeFormat constructor options and configuration options
        * @param {Object} opts - opts to override the configuration options on this DateTime
        * @example DateTime.now().toLocaleString(); //=> 4/20/2017
        * @example DateTime.now().setLocale('en-gb').toLocaleString(); //=> '20/04/2017'
        * @example DateTime.now().toLocaleString(DateTime.DATE_FULL); //=> 'April 20, 2017'
        * @example DateTime.now().toLocaleString(DateTime.DATE_FULL, { locale: 'fr' }); //=> '28 août 2022'
        * @example DateTime.now().toLocaleString(DateTime.TIME_SIMPLE); //=> '11:32 AM'
        * @example DateTime.now().toLocaleString(DateTime.DATETIME_SHORT); //=> '4/20/2017, 11:32 AM'
        * @example DateTime.now().toLocaleString({ weekday: 'long', month: 'long', day: '2-digit' }); //=> 'Thursday, April 20'
        * @example DateTime.now().toLocaleString({ weekday: 'short', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' }); //=> 'Thu, Apr 20, 11:27 AM'
     * @example DateTime.now().toLocaleString({ hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }); //=> '11:32'
        */
        return DateTime.now().toLocaleString({ weekday: 'short', month: 'long', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    }
}
