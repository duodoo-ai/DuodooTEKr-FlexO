/** @odoo-module **/

import { useDebounced } from "@web/core/utils/timing";
import { browser } from "@web/core/browser/browser";
import { sprintf } from "@web/core/utils/strings";
import { useBus, useService } from "@web/core/utils/hooks";
import { _lt, _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { router, routerBus } from "@web/core/browser/router";
const {
	Component,
	onMounted,
	onRendered,
	onWillRender,
	onWillDestroy,
	onWillUnmount,
	onPatched,
	onWillUpdateProps,
	useExternalListener,
	useEffect,
	useState,
	useRef,
	EventBus,
} = owl;

/**
 * SideNav menu
 * 该组件处理不同可用应用程序和菜单之间的显示和导航。
 *
 *! 组件示例图：
 **┌ <div class="accordion accordion-flush" id="menu-accordion-1"> ---------------------------┐
 **│ ┌ <div class="accordion-item" id="menu-item-1"> ---------------------------------------┐ │
 **│ │ ┌ <h2 class="accordion-header"  id="menu-header-1"> -------------------------------┐ │ │
 **│ │ │ ┌ <a class="accordion-button collapsed" id="menu-link-1" href="#"> ------------┐ │ │ │
 **| | | |   data-bs-toggle="collapse"                                                  | | | |
 **| | | |   aria-expanded="false"                                                      │ │ │ │
 **| | | |   data-bs-target="#menu-collapse-1"                                          │ │ │ │
 **| | | |   aria-controls="menu-collapse-1"                                            │ │ │ │
 **| | | | >                                                                            │ │ │ │
 **| │ │ │ ┌ <span class="menu-icon"> ------------------------------------------------┐ │ │ │ │
 **| │ │ │ │  <i class="fa fa-home"></i>                                              │ │ │ │ │
 **| │ │ │ └ </span> -----------------------------------------------------------------┘ │ │ │ │
 **| │ │ │ - <span class="menu-lable"/>                                                 │ │ │ │
 **| │ │ └ <a/> ------------------------------------------------------------------------┘ │ │ │
 **| │ └ </h2> ---------------------------------------------------------------------------┘ │ │
 **| │ ┌ <div class="accordion-collapse collapse" id="menu-collapse-1"  折叠的选项 --------┐ │ │
 **| | |     aria-labelledby="menu-header-1"                                              │ │ │
 **| | |     data-bs-parent="#menu-accordion-1"                                           │ │ │
 **| │ │ >                                                                                │ │ │
 **| │ │ ┌ <div class="accordion-body" id="menu-body-1> --------------------------------┐ │ │ │
 **| │ │ │ - [Next level menu]  从<div class="accordion accordion-flush">开始循环        │ │ │ │
 **| │ │ └ </div>-----------------------------------------------------------------------┘ │ │ │
 **| │ └ </div>---------------------------------------------------------------------------┘ │ │
 **| └ </div> ------------------------------------------------------------------------------┘ │
 **└ </div>-----------------------------------------------------------------------------------┘

 *! 注意:
 1. ".collapse"类用于指定一个折叠元素 (示例中的 <div>); 点击按钮后会在隐藏与显示之间切换。
 2. 控制内容的隐藏与显示，需要在 <a> 或 <button> 元素上添加 data-bs-toggle="collapse" 属性。 data-bs-target="#id" 属性是对应折叠的内容 (<div id="menu-collapse-1">)。
 3. <a> 元素上你可以使用 href 属性来代替 data-bs-target 属性.
 4. 默认情况下折叠的内容是隐藏的，你可以添加 ".show" 类让内容默认显示:
 5. 使用 data-bs-parent 属性来确保所有的折叠元素在指定的父元素下，这样就能实现在一个折叠选项显示时其他选项就隐藏。
 */

export class EistErpSidebarMenu extends Component {
	setup() {
		super.setup();

		this.SidebarMenuRef = useRef("sidebar_menu");
		this.menuService = useService("menu");
		this.actionService = useService("action");

		this.menuData = this.menuService.getMenuAsTree("root");

		this.currentAction = router.current.action;
		this.state = useState({
			theme: session["theme"],
		});

		if (this.currentAction) {
			this.getCurrentMenuItem(this.currentAction);
		}

		this.current_cid = session.user_companies.current_company;
		this.state.theme.sidebar.is_minimized = false;

		if (this.state.theme.sidebar.default_minimized) {
			this.state.theme.sidebar.is_minimized = true;
		}

		useBus(this.env.bus, "SIDEBAR-SUBMENU:TOGGLED", (menu) =>
			this.toggle_sidebar_submenu(menu)
		);

		onMounted(() => {
			this.onMounted();
		});
		onPatched(() => { });
		onWillUpdateProps(() => { });
	}

	onMounted() {
		this.el = this.SidebarMenuRef.el;

		// 定义挂载组件时应该执行的代码的钩子
		this.body = document.body;

		// this.el = this.SidebarMenuRef.el;
		// this.$el = $(this.el);

		// let current_action = Number(this.router.current.hash.menu_id || 0);
		const currentController = this.actionService.currentController;
		let actionId = currentController && currentController.action.id;
		// if (menuId === 0 && !actionId) {
		// 	//TODO 使用 ir.actions.todo 跳转菜单后，侧边栏无法正确菜单状态问题
		// }

		this.initializeMenu();
	}

	//-----------------------------------------------
	// Handlers
	//-----------------------------------------------

	initializeMenu() {
		// 初始化菜单
		if (this.state.currentActionID) {
			const menuPaths = this.getParentMenuPath(this.state.currentMenuId);

			// 展开菜单
			menuPaths.forEach((menuId) => {
				const menu_condition = sprintf(
					'div.accordion-collapse[data-menu="%s"]',
					menuId
				);
				const menuEl = this.el.querySelector(menu_condition);
				menuEl.classList.add("show");

				const link_condition = sprintf(
					'a.accordion-button[data-menu="%s"]',
					menuId
				);
				const linkEl = this.el.querySelector(link_condition);
				linkEl.classList.add("active");
			});
		}
	}

	/*
	允许加载子菜单
	*/
	allowLoadAppSubMenus() {
		if (
			this.state.theme.sidebar_default_minimized &&
			!this.state.theme.sidebar.hover_maximize
		) {
			return false;
		} else if (this.state.theme.main.submenu.position === 1) {
			return false;
		} else {
			return true;
		}
	}

	currentAppSections(appid) {
		return this.menuService.getMenuAsTree(appid).childrenTree || [];
	}

	currentMenuSections(menuid) {
		return this.menuService.getMenuAsTree(menuid).childrenTree || [];
	}

	getMenuItemHref(payload) {
		if (payload.actionPath) {
			return "/odoo/" + payload.actionPath;
		} else if (payload.actionID) {
			return "action-" + payload.actionID;
		} else {
			const submenu = this.currentMenuSections(payload.id);
			if (submenu.length > 0) {
				return "action-" + submenu[0].actionID;
			} else {
				return "#";
			}
		}
	}

	getChildrenMenu(menuid) {
		return this.menuService.getMenuAsTree(menuid).children || [];
	}

	/*
	深度查找子元素
	*/
	deepFindChild(arr, key, value) {
		let result = [];
		function searchInObject(obj) {
			for (let prop in obj) {
				if (obj.hasOwnProperty(prop)) {
					if (prop === key && obj[prop] === value) {
						result.push(obj);
					} else if (typeof obj[prop] === "object") {
						searchInObject(obj[prop]);
					}
				}
			}
		}
		arr.forEach((item) => {
			searchInObject(item);
		});
		return result;
	}

	/*
	获取当前菜单
	*/
	getCurrentMenuItem(action) {
		// console.log(action);
		let menu;
		if (typeof action === "string") {
			menu = this.deepFindChild(
				this.menuData.childrenTree,
				"actionPath",
				action
			);
		} else if (typeof action === "number") {
			menu = this.deepFindChild(
				this.menuData.childrenTree,
				"actionID",
				action
			);
		}
		if (menu.length > 1) {
			menu = menu[1];
		} else {
			menu = menu[0];
		}
		// console.log("获取当前菜单-------------", menu);
		if (menu) {
			this.state.currentMenuId = menu.id;
			this.state.currentAppId = menu.appID;
			this.state.currentActionID = menu.actionID;
		}
	}

	deepFindParent(data, targetId) {
		let path = [];
		let found = false;

		function traverse(current, ancestors) {
			if (found) return; // 如果已经找到目标元素，停止遍历

			if (current.id === targetId) {
				found = true;
				path = [...ancestors, current];
				return;
			}

			if (current.children) {
				for (const child of current.children) {
					traverse(child, [...ancestors, current]);
				}
			}
		}

		for (const item of data) {
			traverse(item, []);
		}

		return path;
	}

	/*
	获取上级菜单路径
	*/
	getParentMenuPath(menuID) {
		let paths = [];
		const menu_condition = sprintf(
			'a.accordion-button[data-menu="%s"]',
			menuID
		);
		const menuEl = this.el.querySelector(menu_condition);
		const allMenuEl = this.el.querySelectorAll("div.accordion-collapse");
		const allMenuElArray = Array.from(allMenuEl);
		allMenuElArray.forEach((item) => {
			if (item.hasAttribute("data-menu")) {
				const menu_id = Number(item.dataset.menu);
				if (item.contains(menuEl) && menu_id !== menuID) {
					paths.push(menu_id);
				}
			}
		});
		return paths;
	}

	toggle_sidebar_submenu(menu) {
		// TODO
		const currentMenuId = menu["detail"]["menu"]["id"];
		if (this.state.currentMenuId !== currentMenuId) {
			this.currentMenuId = currentMenuId;
			this.state.currentMenuId = currentMenuId;

			this.el.querySelectorAll(".accordion-collapse").forEach((item) => {
				item.classList.remove("show");
			});
			// let $menu = this.$el.find(
			// 	"a#menu-link-" + this.state.currentMenuId
			// );
			// $menu.addClass("active");
			if (!this.state.theme.sidebar.is_minimized) {
				// $menu.parents(".collapse").addClass("show");
			}
			// 'active' 菜单滚动到可视区域
			// this.accordion_menu = this.$el.find("#o_sidebar_menu_accordion");
		}
	}

	//-----------------------------------------------
	// Private
	//-----------------------------------------------

	_expandOrCollapseSideMenu(target, state) {
		// ----------------------------
		// 侧边栏展开或收起
		// ----------------------------
		if (
			!this.state.theme.sidebar.is_minimized ||
			!this.state.theme.sidebar.hover_maximize
		) {
			return;
		}
		if (state) {
			// 滑入侧边栏时，展开侧边栏
			this.el.classList.add("sidebar-maximize");

			// 展开应用菜单
			const appCollapseEl = this.el.querySelector(
				"#menu-collapse-" + this.state.currentAppId
			);
			console.log(appCollapseEl)
			if (appCollapseEl) {
				appCollapseEl.classList.remove("collapse");
				appCollapseEl.classList.add("show");
			}

			const menuPaths = this.getParentMenuPath(this.state.currentMenuId);
			// 展开子菜单
			menuPaths.forEach((menuId) => {
				const menu_condition = sprintf(
					'div.accordion-collapse[data-menu="%s"]',
					menuId
				);
				const menuEl = this.el.querySelector(menu_condition);
				menuEl.classList.add("show");

				const link_condition = sprintf(
					'a.accordion-button[data-menu="%s"]',
					menuId
				);
				const linkEl = this.el.querySelector(link_condition);
				linkEl.classList.add("active");
			});
		} else {
			// 滑出侧边栏时，收起侧边栏
			this.el.classList.remove("sidebar-maximize");
			this.el.querySelectorAll(".accordion-collapse").forEach((item) => {
				item.classList.remove("show");
				item.classList.add("collapse");
			});
		}
	}

	/*
	鼠标划过logo，
	隐藏logo，
	显示切换状态按钮
	*/
	_showToggleSideMenuButton(target) {
		// console.log("鼠标划过logo", target);

		if (!this.state.theme.sidebar.show_minimize_button) {
			return;
		}
		const logoEl = target.closest(".o_sidebar_menu_brand_logo");

		if (this.state.theme.sidebar.is_minimized) {
			this.el
				.querySelector("button.o_sidebar_menu_toggler")
				.classList.remove("o_hidden");
			logoEl.classList.add("o_hidden");
		}
	}

	/*
	鼠标离开切换按钮，
	隐藏切换按钮，
	显示logo
	*/
	_hideToggleSideMenuButton(target) {
		// console.log("鼠标离开切换按钮", target);
		const logoEl = this.el.querySelector(".o_sidebar_menu_brand_logo");
		if (this.state.theme.sidebar.is_minimized) {
			target.classList.add("o_hidden");
			logoEl.classList.remove("o_hidden");
		}
	}

	/*
	 * 切换侧边栏状态
	 */
	_toggleSideMenu(target, minimize) {
		this.state.theme.sidebar.is_minimized = !minimize;
		this.state.theme.sidebar.default_minimized =
			this.state.theme.sidebar.is_minimized;

		if (!this.state.theme.sidebar.is_minimized) {
			// 处理LOGO
			const logoEl = this.el.querySelector(".o_sidebar_menu_brand_logo");
			logoEl.classList.remove("o_hidden");

			// 处理菜单
			// 展开应用菜单
			const appCollapseEl = this.el.querySelector(
				"#menu-collapse-" + this.state.currentAppId
			);
			if (appCollapseEl) {
				appCollapseEl.classList.remove("collapse");
				appCollapseEl.classList.add("show");
			}

			const menuPaths = this.getParentMenuPath(this.state.currentMenuId);
			// 展开子菜单
			menuPaths.forEach((menuId) => {
				const menu_condition = sprintf(
					'div.accordion-collapse[data-menu="%s"]',
					menuId
				);
				const menuEl = this.el.querySelector(menu_condition);
				menuEl.classList.add("show");

				const link_condition = sprintf(
					'a.accordion-button[data-menu="%s"]',
					menuId
				);
				const linkEl = this.el.querySelector(link_condition);
				linkEl.classList.add("active");
			});
		} else {
			this.el.classList.remove("sidebar-maximize");
			this.el.querySelectorAll(".accordion-collapse").forEach((item) => {
				item.classList.remove("show");
				item.classList.add("collapse");
			});
		}
	}

	_openMenu(ev, menu) {
		// 移除所有的 'active'
		let allMenu =
			this.SidebarMenuRef.el.querySelectorAll(".accordion-button");
		allMenu.forEach((m) => {
			m.classList.remove("active");
		});

		if (this.env.isSmall) {
			// 手机端，点击菜单时，隐藏
			const close_btn = this.SidebarMenuRef.el.querySelector(
				"#o_sidenav_mobile_close"
			);
			close_btn.click();
		}

		if (menu) {
			// 应用菜单
			const appID = menu.appID;
			const menuID = menu.id;

			const app_menu = this.SidebarMenuRef.el.querySelector(
				"a#menu-link-" + appID
			);
			app_menu.classList.add("active");
			const app_collapse = this.SidebarMenuRef.el.querySelector(
				"div#menu-collapse-" + appID
			);
			if (
				!this.state.theme.sidebar.is_minimized ||
				!this.state.theme.sidebar.hover_maximize
			) {
				app_collapse.classList.add("show");

				// 子菜单
				const sub_menu = this.SidebarMenuRef.el.querySelector(
					"a#menu-link-" + menuID
				);
				sub_menu.classList.add("active");
			} else {
				app_collapse.classList.remove("show");
			}
			this.state.currentMenuId = menuID;
			return this.menuService.selectMenu(menu);
		}
	}

	getMenuItemIcon(level) {
		// 获取应用下的子菜单图标
		// 5级子菜单的图标，应该够使用了，不够请自行添加
		let icon = "";
		switch (level) {
			case 1:
				icon = "fa fa-circle";
				break;
			case 2:
				icon = "fa fa-dot-circle-o";
				break;
			case 3:
				icon = "fa fa-circle-o";
				break;
			case 4:
				icon = "fa fa-square";
				break;
			case 5:
				icon = "fa fa-square-o";
				break;
			default:
				icon = "fa fa-square-o";
		}
		return icon;
	}
}
EistErpSidebarMenu.template = "eist_web_theme.SidebarMenu";
EistErpSidebarMenu.components = {};
EistErpSidebarMenu.props = {
	currentMenuId: {
		type: Number,
		optional: true,
	},
};
