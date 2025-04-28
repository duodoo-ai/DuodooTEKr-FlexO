/** @odoo-module **/

import { session } from "@web/session";
import { NavBar } from "@web/webclient/navbar/navbar";
import { useService, useBus } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { useState, useEffect, useRef } from "@odoo/owl";

export class EistErpNavBar extends NavBar {
	static template = "eist_web_theme.EistErpNavBar";

	setup() {
		super.setup();
		this.dm = useState(useService("drawer_menu"));
		this.pwa = useService("pwa");
		this.menuAppsRef = useRef("menuApps");
		this.navRef = useRef("nav");

		this.state = useState({
			...this.state,
			theme: session["theme"],
		});


		this._busToggledCallback = () => this._updateMenuAppsIcon()
		useBus(this.env.bus, "DRAWER-MENU:TOGGLED", this._busToggledCallback);
		useEffect(() => this._updateMenuAppsIcon());
	}

	get hasBackgroundAction() {
		return this.dm.hasBackgroundAction;
	}
	get isInApp() {
		return !this.dm.hasDrawerMenu;
	}

	_openAppMenuSidebar() {
		if (this.dm.hasDrawerMenu) {
			this.dm.toggle(false);
		} else {
			this.state.isAppMenuSidebarOpened = true;
		}
	}

	_updateMenuAppsIcon() {
		const menuAppsEl = this.menuAppsRef.el;
		menuAppsEl.classList.toggle(
			"o_hidden",
			!this.isInApp && !this.hasBackgroundAction
		);
		menuAppsEl.classList.toggle(
			"o_menu_toggle_back",
			!this.isInApp && this.hasBackgroundAction
		);
		if (!this.isScopedApp) {
			const title =
				!this.isInApp && this.hasBackgroundAction
					? _t("Previous view")
					: _t("Drawer menu");
			menuAppsEl.title = title;
			menuAppsEl.ariaLabel = title;
		}

		const menuBrand = this.navRef.el.querySelector(".o_menu_brand");
		if (menuBrand) {
			menuBrand.classList.toggle("o_hidden", !this.isInApp);
		}

		const menuBrandIcon =
			this.navRef.el.querySelector(".o_menu_brand_icon");
		if (menuBrandIcon) {
			menuBrandIcon.classList.toggle("o_hidden", !this.isInApp);
		}

		const appSubMenus = this.appSubMenus.el;
		if (appSubMenus) {
			appSubMenus.classList.toggle("o_hidden", !this.isInApp);
		}

		const breadcrumb = this.navRef.el.querySelector(".o_breadcrumb");
		if (breadcrumb) {
			breadcrumb.classList.toggle("o_hidden", !this.isInApp);
		}
	}

	/**
	 * @override
	 */
	onAllAppsBtnClick() {
		super.onAllAppsBtnClick();
		this.dm.toggle(true);
		this._closeAppMenuSidebar();
	}
}
