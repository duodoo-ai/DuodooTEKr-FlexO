/* @odoo-module */

import { FormRenderer } from "@web/views/form/form_renderer";
import { SIZES } from "@web/core/ui/ui_service";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { onMounted, useRef, useState } from "@odoo/owl";
import { ScrollTopButton } from '@eist_web_theme/components/scroll_top_button/scroll_top_button';

patch(FormRenderer.prototype, {
    setup() {
        super.setup(...arguments);

        this.uiService = useService("ui");


        const rootRef = useRef("compiled_view_root");


    },

    mailLayout(hasAttachmentContainer) {
        // src\addons\mail\static\src\chatter\web\form_renderer.js
        /*
        EXTERNAL_COMBO_XXL: chatter在侧栏，附件在单独的标签中
        EXTERNAL_COMBO: chatter在底部，附件在单独的标签中
        COMBO: chatter在底部，附件在侧栏
        SIDE_CHATTER: chatter在侧栏，没有附件
        BOTTOM_CHATTER:chatter在底部，没有附件
        NONE
        */

        let layout = super.mailLayout(...arguments);

        // console.log("mailLayout---------------------hasAttachmentContainer", hasAttachmentContainer)


        return layout

    }
})