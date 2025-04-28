/** @odoo-module **/
import { BurgerMenu } from "@web/webclient/burger_menu/burger_menu";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class EistErpBurgerMenu extends BurgerMenu {
	setup() {
		super.setup();
		this.dm = useService("drawer_menu");
	}

	get currentApp() {
		return !this.dm.hasDrawerMenu && super.currentApp;
	}
}

const systrayItem = {
	Component: EistErpBurgerMenu,
};

registry
	.category("systray")
	.add("burger_menu", systrayItem, { sequence: 0, force: true });
