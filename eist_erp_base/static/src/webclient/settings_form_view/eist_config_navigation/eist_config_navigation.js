/** @odoo-module */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";

export class ResConfigERPNavigation extends Component {
	static template = "eist_erp_base.res_config_eist_navigation";
	static props = ["*"];  // could contain view_widget props

	setup() {
		super.setup(...arguments);
	}

	onClickJumpAnchor() {}
}

export const resConfigERPNavigation = {
	component: ResConfigERPNavigation,
};


registry
	.category("view_widgets")
	.add("res_config_eist_navigation", resConfigERPNavigation);
