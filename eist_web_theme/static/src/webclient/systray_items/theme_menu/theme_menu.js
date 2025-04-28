/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ThemePanel } from "./theme_panel";
import { _lt, _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { user } from "@web/core/user";

import {
	Component,
	onMounted,
	onWillStart,
	useExternalListener,
	useState,
} from "@odoo/owl";

export class ThemeMenu extends Component {
	setup() {
		this.user = user;
		this.state = useState({
			isopen: false,
			theme: session["theme"],
		});
	}

	openThemePanel() {
		this.state.isopen = true;
	}
}

ThemeMenu.components = {
	ThemePanel,
};
ThemeMenu.template = "eist_web_theme.ThemeMenu";
ThemeMenu.props = {};

export const systrayItem = {
	Component: ThemeMenu,
	isDisplayed(env) {
		const disable_customization = session.theme.disable_customization;
		return !disable_customization;
	},
};
registry.category("systray").add("ThemeMenu", systrayItem, { sequence: -1 });
