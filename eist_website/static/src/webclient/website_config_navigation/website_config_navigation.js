/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class ResConfigWebsiteNavigation extends Component {
	static template = "eist_website.res_config_website_navigation";
	static props = ["*"];  // could contain view_widget props

	setup() {
		super.setup(...arguments);
	}

	onClickJumpAnchor() {}
}

export const resConfigWebsiteNavigation = {
	component: ResConfigWebsiteNavigation,
};


registry
	.category("view_widgets")
	.add("res_config_website_navigation", resConfigWebsiteNavigation);
