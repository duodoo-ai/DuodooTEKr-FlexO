/** @odoo-module **/

import { sprintf } from "@web/core/utils/strings";
import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";
import { router, routerBus } from "@web/core/browser/router";
import { session } from "@web/session";
import { EistErpNavBar } from "./navbar/navbar";
import { EistErpSidebarMenu } from "./sidebar_menu/sidebar_menu";
import { EistErpFooter } from "./footer/footer";

import { Component, onMounted, onPatched, onWillStart, useExternalListener, useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";

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



		// console.log("WebClientEistErp setup state",this.state.theme.main.app_load_method);

		// 设置品牌
		let system_name = session.brand.system_name;
		var current_company_name;
		const display_company_name = session.brand.display_company_name;
		if (display_company_name) {
			let allowed_companies = session.user_companies.allowed_companies; // 允许访问的公司
			let current_company_id = session.user_companies.current_company; // 当前公司 ID
			current_company_name = getCurrentCompanyName(); //当前公司名称
			function getCurrentCompanyName() {
				for (var key in allowed_companies) {
					let company = allowed_companies[key];
					if (company.id === current_company_id) {
						return company.name;
					}
				}
			}
			system_name = sprintf("%s - %s", current_company_name, system_name);
			// console.log(this.actionService.currentController )
			// this.title.setParts({ one: current_company_name, two: system_name, three: this.actionService.currentController }); //设置标题
		}
		this.title.setParts({ zopenerp: system_name }); //设置标题


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
}
