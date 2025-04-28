/* @odoo-module */

import { SIZES } from "@web/core/ui/ui_service";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { FormCompiler } from "@web/views/form/form_compiler";
import { append, createElement, extractAttributes, setAttributes } from "@web/core/utils/xml";
import { session } from "@web/session";
import { onMounted, useRef, useState } from "@odoo/owl";

patch(FormCompiler.prototype, {
    setup() {
        super.setup(...arguments);
        this.theme = session["theme"];
        this.uiService = useService("ui");
        
    },
    compile(node, params) {
        /*
        不换行: o_form_renderer o_form_editable d-flex d-print-block o_form_saved flex-nowrap h-100
        换行:   o_form_renderer o_form_editable d-flex d-print-block o_form_saved flex-column
        */
        /*
        setAttributes(chatterContainerXml, {
            isChatterAside: "false",
            isInFormSheetBg: "false",
            saveRecord: "__comp__.props.saveRecord",
        });
        */
        /*
        EXTERNAL_COMBO_XXL: chatter在侧栏，附件在单独的标签中
        EXTERNAL_COMBO: chatter在底部，附件在单独的标签中
        COMBO: chatter在底部，附件在侧栏
        SIDE_CHATTER: chatter在侧栏，没有附件
        BOTTOM_CHATTER:chatter在底部，没有附件
        NONE
        */
        const res = super.compile(node, params);


        return res;
    },
});
