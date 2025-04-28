/** @odoo-module */

import { Component, onMounted, onWillStart, onPatched, onWillUpdateProps, useState, useRef } from "@odoo/owl";

export class ProjectRouteMapInfoWindow extends Component {
    static template = "project.ProjectRouteMapInfoWindow";
    static props = {
        // infoWindow: { type: Object, optional: true },
        geometry_id: { type: String },
        title: { type: String },
        distance: { type: String, optional: true },
        status: { type: String, optional: true },
        real_input_traffic: { type: Number, optional: true },
        real_output_traffic: { type: Number, optional: true },
        lat: { type: Number, optional: true },
        lng: { type: Number, optional: true },
        normal_state_color: { type: String, optional: true },
        exception_state_color: { type: String, optional: true },
        showCloseButton: { type: Boolean, optional: true },
        onClose: { type: Function, optional: true },
    };
    static defaultProps = {
        showCloseButton: false,
    };
    setup() {
        console.log("ProjectRouteMapInfoWindow setup", this.props);
    }

    get backgroundColor() {
        return this.props.status === "normal" ? this.props.exception_state_color : this.props.exception_state_color;
    }

    onCloseInfoWindow() {
        console.log("调用父组件方法");
        this.props.onClose();  // 调用父组件方法
    }
}