/** @odoo-module **/

import { sprintf } from "@web/core/utils/strings";
import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";
import { router, routerBus } from "@web/core/browser/router";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";
import { cookie as cookieManager } from "@web/core/browser/cookie";
import { EistErpNavBar } from "./navbar/navbar";
import { EistErpSidebarMenu } from "./sidebar_menu/sidebar_menu";
import { EistErpFooter } from "./footer/footer";

import { Component, onMounted, onPatched, onWillStart, useExternalListener, useState } from "@odoo/owl";


export class WebClientEistErp extends WebClient {
	static components = {
		...WebClient.components,
		NavBar: EistErpNavBar,
		EistErpSidebarMenu,
		EistErpFooter,
	};
	// static template = "eist_web_theme.WebClient";


	setup() {
		super.setup();

		this.dm = useService("drawer_menu");
		this.title = useService("title");
		this.actionService = useService("action");


		// const currentMenuId = Number(this.router.current.hash.menu_id || 0);
		this.state = useState({
			...this.state,
			theme: session["theme"],
			// currentMenuId: currentMenuId,
			hasDrawerMenu: this.dm.hasDrawerMenu,
		});



		// console.log("默认的主题颜色", this.state.theme.color.default);



		// 主题
		this.state.theme.sidebarMinimize = false;
		if (this.state.theme.default_minimized) {
			this.state.theme.sidebarMinimize = true;
		}
		if (this.state.theme.color.default !== 0) {

		}

		onMounted(() => {
			// 定义挂载组件时应该执行的代码的钩子
			this.el = document.body;
			this.set_body_data();
		});

		onPatched(() => {
			this.set_body_data();
		});
	}

	set_body_data() {
		this.toggleThemeColor(this.state.theme.color.default);

		this.el.setAttribute(
			"data-theme-color",
			this.state.theme.color.default
		); // 主题颜色
		this.el.setAttribute(
			"data-app-load-method",
			this.state.theme.main.app_load_method.default
		); // 加载方式

		// this.el.setAttribute('data-display-sidebar', this.state.theme.main.display_sidebar);// 是否显示侧边栏

		this.el.setAttribute(
			"data-fullscreen",
			this.state.fullscreen
		); // 是否全屏

		this.el.setAttribute(
			"data-sidebar-default-minimize",
			this.state.theme.sidebar.default_minimized
		); // 侧边栏默认是否最小化

		this.el.setAttribute(
			"data-sidebar-is-minimized",
			this.state.theme.sidebar.is_minimized
		); // 侧边栏是否最小化

		this.state.theme.sidebar.is_minimized;

		this.el.setAttribute(
			"data-sidebar-hover-maximize",
			this.state.theme.sidebar.hover_maximize
		); // 鼠标悬停是否最大化

		// 页脚
		this.el.setAttribute(
			"data-display-footer",
			this.state.theme.footer.display && !this.env.isSmall
		); // 是否显示页脚
	}

	_loadDefaultApp() {
		super._loadDefaultApp();
		if (this.state.theme.main.app_load_method.default === "3") {
			return this.dm.toggle(true);
		}
	}

	toggleThemeColor(color) {
		if (cookieManager.get("color_scheme") !== "dark") {
			// 移除所有主题相关的类名
			const themeClasses = Array.from(this.el.classList)
				.filter(className => className.match(/^o_web_client_theme_colore_\d+$/));
			this.el.classList.remove(...themeClasses);

			// 添加新的主题类名
			this.el.classList.add(`o_web_client_theme_colore_${color}`);

			// 更新状态
			this.state.theme.color.default = color;
		}

	}

	isBackendPage() {
		// 1. 路径判断
		const backendPrefixes = [
			"/web",
			"/odoo",
			"/mail",
			"/web/login",
			"/web/database"
		];
		const path = window.location.pathname;
		if (backendPrefixes.some(prefix => path.startsWith(prefix))) {
			return true;
		}
		// 2. DOM 判断（后台页面有 .o_web_client）
		if (document.querySelector('.o_web_client')) {
			return true;
		}
		// 3. hash 判断（后台常用 hash 路由）
		if (window.location.hash && path.startsWith("/web")) {
			return true;
		}
		if (window.location.hash && path.startsWith("/odoo")) {
			return true;
		}
		return false;
	}
}
