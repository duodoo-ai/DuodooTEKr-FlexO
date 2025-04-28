/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { Mutex } from "@web/core/utils/concurrency";
import { useService } from "@web/core/utils/hooks";
import {
	computeAppsAndMenuItems,
	reorderApps,
} from "@web/webclient/menus/menu_helpers";
import {
	ControllerNotFoundError,
	standardActionServiceProps,
} from "@web/webclient/actions/action_service";
import { DrawerMenu } from "./drawer_menu";

import {
	Component,
	onMounted,
	onWillUnmount,
	useState,
	reactive,
	xml,
} from "@odoo/owl";

export const drawerMenuService = {
	dependencies: ["action"],
	start(env) {
		const state = reactive({
			hasDrawerMenu: false, // true iff the DrawerMenu is currently displayed
			hasBackgroundAction: false, // true iff there is an action behind the DrawerMenu
			toggle,
		});
		const mutex = new Mutex(); // used to protect against concurrent toggling requests
		class DrawerMenuAction extends Component {
			static components = { DrawerMenu };
			static target = "current";
			static props = { ...standardActionServiceProps };
			static template = xml`<DrawerMenu t-props="drawerMenuProps"/>`;
			static displayName = _t("Home");

			setup() {
				this.menus = useService("menu");
				const drawermenuConfig = JSON.parse(
					user.settings?.drawermenu_config || "null"
				);
				const apps = useState(
					computeAppsAndMenuItems(this.menus.getMenuAsTree("root"))
						.apps
				);
				if (drawermenuConfig) {
					reorderApps(apps, drawermenuConfig);
				}
				this.drawerMenuProps = {
					apps: apps,
					reorderApps: (order) => {
						reorderApps(apps, order);
					},
				};
				onMounted(() => this.onMounted());
				onWillUnmount(this.onWillUnmount);
			}
			async onMounted() {
				const { breadcrumbs } = this.env.config;
				state.hasDrawerMenu = true;
				state.hasBackgroundAction = breadcrumbs.length > 0;
				this.env.bus.trigger("DRAWER-MENU:TOGGLED");
			}
			onWillUnmount() {
				state.hasDrawerMenu = false;
				state.hasBackgroundAction = false;
				this.env.bus.trigger("DRAWER-MENU:TOGGLED");
			}
		}

		registry.category("actions").add("menu", DrawerMenuAction);

		env.bus.addEventListener("DRAWER-MENU:TOGGLED", () => {
			document.body.classList.toggle(
				"o_drawer_menu_background",
				state.hasDrawerMenu
			);
		});

		async function toggle(show) {
			return mutex.exec(async () => {
				show =
					show === undefined ? !state.hasDrawerMenu : Boolean(show);
				if (show !== state.hasDrawerMenu) {
					if (show) {
						await env.services.action.doAction("menu");
					} else {
						try {
							await env.services.action.restore();
						} catch (err) {
							if (!(err instanceof ControllerNotFoundError)) {
								throw err;
							}
						}
					}
				}
				// hack: wait for a tick to ensure that the url has been updated before
				// switching again
				return new Promise((r) => setTimeout(r));
			});
		}

		return state;
	},
};

registry.category("services").add("drawer_menu", drawerMenuService);
