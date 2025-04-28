/** @odoo-module **/

import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';
import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { onMounted, useState } from '@odoo/owl';
import { ScrollTopButton } from '@eist_web_theme/components/scroll_top_button/scroll_top_button';

patch(KanbanRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.theme = session["theme"];

        this.state = useState({
            ...this.state,
            displayScrollTopButton: this.theme["views"]["display_scroll_top_button"],
            showScrollTopButton: false,
            useParentEl: false,
        });

        this.onScrollKanbanEl = (ev) => {
            // console.log(ev.target.scrollTop);
            if (this.state.displayScrollTopButton) {
                if (ev.target.scrollTop > 300) {
                    this.state.showScrollTopButton = true;
                } else {
                    this.state.showScrollTopButton = false;
                }
            }
        }

        onMounted(() => {
            this.scrollKanBanEl = this.rootRef.el.parentNode;
            if (this.scrollKanBanEl.classList.contains("o_component_with_search_panel")) {
                this.state.useParentEl = false;
                this.rootRef.el.addEventListener('scroll', this.onScrollKanbanEl);
            } else {
                this.state.useParentEl = true;
                this.scrollKanBanEl.addEventListener('scroll', this.onScrollKanbanEl);
            }

        });
    },
});
KanbanRenderer.components = {
    ...KanbanRenderer.components,
    ScrollTopButton,
};