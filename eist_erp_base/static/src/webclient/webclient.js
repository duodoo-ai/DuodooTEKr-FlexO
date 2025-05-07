/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { sprintf } from "@web/core/utils/strings";
import { session } from "@web/session";

patch(WebClient.prototype, {

	setup() {
		super.setup();

		// 设置品牌
		let system_name = document.title;
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
		}
		this.title.setParts({ zopenerp: system_name });
	}

});
