/** @odoo-module **/

import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { onMounted, onWillUnmount, useRef } from '@odoo/owl';
import { ScrollTopButton } from '@eist_web_theme/components/scroll_top_button/scroll_top_button';
import { SettingsPage } from '@web/webclient/settings_form_view/settings/settings_page';

patch(SettingsPage.prototype, {
    setup() {
        super.setup(...arguments);

        // 初始化滚动按钮相关的状态
        this.offset = 300;
        this.theme = session.theme || {};
        this.displayScrollTopButton = this.theme.views?.display_scroll_top_button || false;

        // 滚动处理函数
        this.onScrollSettingsEl = (ev) => {
            if (this.displayScrollTopButton && ev.target) {
                const show = ev.target.scrollTop > this.offset;
                if (show !== this.state.show) {
                    this.state.show = show;
                }
            }
        };

        // 组件挂载时添加事件监听
        onMounted(() => {
            if (this.settingsRef.el) {
                this.scrollTopButton = this.settingsRef.el.parentElement.querySelector('.o_scroll_top');
                this.settingsRef.el.addEventListener('scroll', this.onScrollSettingsEl);
            }
        });

        // 组件卸载时清理事件监听
        onWillUnmount(() => {
            if (this.settingsRef?.el) {
                this.settingsRef.el.removeEventListener('scroll', this.onScrollSettingsEl);
            }
        });
    },

    /**
     * @override
     */
    get defaultProps() {
        return {
            ...super.defaultProps,
            slots: {
                default: { isVisible: true },
                NoContentHelper: { isVisible: false },
            },
        };
    },
});

// 注册子组件
Object.assign(SettingsPage.components, {
    ScrollTopButton,
});
