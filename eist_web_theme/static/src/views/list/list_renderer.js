/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from '@web/views/list/list_renderer';
import { session } from "@web/session";;
import { onMounted, useState } from "@odoo/owl";
import { ScrollTopButton } from '@eist_web_theme/components/scroll_top_button/scroll_top_button';




patch(ListRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.theme = session["theme"];

        this.state = useState({
            displayScrollTopButton: this.theme["views"]["display_scroll_top_button"],
            showScrollTopButton:false,
        });

        this.onScrollListEl = (ev) => {
            if (this.state.displayScrollTopButton) {
				if (ev.target.scrollTop > 300) {
					this.state.showScrollTopButton = true;
				} else {
					this.state.showScrollTopButton = false;
				}
			}
		}

        onMounted(() => {
			this.rootRef.el.addEventListener('scroll', this.onScrollListEl);
		});
    },
});
ListRenderer.components = {
    ...ListRenderer.components,
    ScrollTopButton,
};