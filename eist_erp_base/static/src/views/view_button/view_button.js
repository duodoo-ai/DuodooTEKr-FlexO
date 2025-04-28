/** @odoo-module **/

import { ViewButton } from "@web/views/view_button/view_button";
import { patch } from "@web/core/utils/patch";


patch(ViewButton.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.props.icon) {
            if (this.props.icon.startsWith("bi-")) {
                this.icon.tag = "i";
                this.icon.class = `o_button_icon fa-fw bi ${this.props.icon}`;
            }
        }
    }
});
