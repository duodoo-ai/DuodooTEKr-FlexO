/** @odoo-module **/

import { formatInteger } from "@web/views/fields/formatters";
import { Component, useState, onWillUnmount } from "@odoo/owl";



export class Dashboard extends Component {
    static template = "rtx_project.ProjectLargeScreen.Dashboard";
    static props = {
        pipeline_data: { type: Object },
    };
    setup() {
        this.formatInteger = formatInteger;
        this.state = useState({
            pipeline_data: this.props.pipeline_data,
        })

        this.busService = this.env.services.bus_service;
        this.busService.subscribe("online_sync_pipeline_dashboard_data", (notification) => {
            this.updateDashboardData(notification.dashboard_data);
        });
    }

    updateDashboardData(data) {
        // console.log("更新仪表盘数据", data);
        this.state.pipeline_data = data;
    }

    format(value) {
        return this.formatInteger(value, { humanReadable: true, decimals: 0, minDigits: 3 });
    }
}
