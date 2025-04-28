/* @odoo-module */

import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(Chatter.prototype, {
    setup() {
        super.setup();
        this.theme = session["theme"];
        this.state.form_chatter_position = this.theme["views"]["form"]["chatter"]["position"];
    },

    _onMounted() {
        super._onMounted();
        const self = this;

        // 定义定时器 ID
        let timerId = null;
        // 设定查询间隔（毫秒）
        const interval = 500;

        // 开始定时查询元素
        timerId = setInterval(() => {
            const targetElement = this.rootRef.el;
            if (targetElement) {
                // 当查询到元素时，清除定时器
                clearInterval(timerId);
                self.set_form_chatter_position()
            }
        }, interval);
    },
    set_form_chatter_position() {

        const chatterContainerEl = this.rootRef.el.closest(".o-mail-ChatterContainer");
        const formRendereEl = this.rootRef.el.closest(".o_form_renderer");
        const attachmentPreviewEl = formRendereEl.querySelector(".o_attachment_preview");

        if (!attachmentPreviewEl) {
            /*
            * o_form_renderer 的变化
            !不换行: o_form_renderer o_form_editable d-flex d-print-block o_form_saved flex-nowrap h-100
            !        > o_form_sheet_bg
            !           > o_form_sheet position-relative
            !        > o-mail-ChatterContainer o-mail-Form-chatter o-aside w-print-100
            !           > o-mail-Chatter w-100 h-100 flex-grow-1 d-flex flex-column overflow-auto
            !               > o-mail-Chatter-top d-print-none position-sticky top-0
            !               > o-mail-Chatter-content d-flex flex-column flex-grow-1
            !换行:   o_form_renderer o_form_editable d-flex d-print-block o_form_saved flex-column
            !        > o_form_sheet_bg
            !        > o-mail-ChatterContainer o-mail-Form-chatter mt-4 mt-md-0
            !           > o-mail-Chatter w-100 h-100 flex-grow-1 d-flex flex-column
            !               > o-mail-Chatter-top d-print-none position-sticky top-0
            !               > o-mail-Chatter-content d-flex flex-column flex-grow-1
            */
            if (this.state.form_chatter_position === 2) {
                formRendereEl.classList.remove('flex-nowrap');
                formRendereEl.classList.remove('h-100');
                formRendereEl.classList.add('flex-column');

                chatterContainerEl.classList.remove('o-aside');
                chatterContainerEl.classList.remove('w-print-100');
                chatterContainerEl.classList.add('mt-4');
                chatterContainerEl.classList.add('mt-md-0');
            }
        } else {
            formRendereEl.classList.remove('flex-column');
            formRendereEl.classList.add('flex-nowrap');
            formRendereEl.classList.add('h-100');

        }
    }
});
