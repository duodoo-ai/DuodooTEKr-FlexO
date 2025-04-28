/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { RelationalModel } from "@web/model/relational_model/relational_model";


patch(RelationalModel.prototype, {
    setup(params, { action, company, dialog, notification })  {
        super.setup(...arguments);

        this.initialLimit = session["theme"].views.list.rows.limit;
        // this.DEFAULT_GROUP_LIMIT = session["theme"].views.list.rows.limit;

        // console.log("initialLimit", this.initialLimit);
        // console.log("initialCountLimit", this.initialCountLimit);
    },

});