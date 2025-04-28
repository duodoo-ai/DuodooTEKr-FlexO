import { _t } from "@web/core/l10n/translation";

import { Component, useRef, useState, useExternalListener } from "@odoo/owl";

export class ThemeColorList extends Component {
    static COLORS = [
        _t("Light"),            // 0.浅色
        _t("Red"),              // 1.红色
        _t("Orange"),           // 2.橙色
        _t("Yellow"),           // 3.黄色
        _t("Green"),            // 4.绿色
        _t("Blue"),             // 5.蓝色
        _t("Indigo"),           // 6.靛色
        _t("Lavender"),         // 7.偏指淡蓝紫色，也就是薰衣草的颜色
        _t("Mauve"),            // 8.指淡紫红色、淡紫色，颜色相对柔和淡雅
        _t("Grey"),             // 9.灰色
    ];
    static template = "eist_web_theme.ThemeColorList";
    static defaultProps = {
        forceExpanded: false,
        isExpanded: false,
    };
    static props = {
        canToggle: { type: Boolean, optional: true },
        colors: Array,
        forceExpanded: { type: Boolean, optional: true },
        isExpanded: { type: Boolean, optional: true },
        onColorSelected: Function,
        selectedColor: { type: Number, optional: true },
    };

    setup() {
        this.colorlistRef = useRef("theme_colorlist");
        this.state = useState({ isExpanded: this.props.isExpanded });
        useExternalListener(window, "click", this.onOutsideClick);
    }
    get colors() {
        return this.constructor.COLORS;
    }
    onColorSelected(id) {
        this.props.onColorSelected(id);
        if (!this.props.forceExpanded) {
            this.state.isExpanded = false;
        }
    }
    onOutsideClick(ev) {
        if (this.colorlistRef.el.contains(ev.target) || this.props.forceExpanded) {
            return;
        }
        this.state.isExpanded = false;
    }
    onToggle(ev) {
        if (this.props.canToggle) {
            ev.preventDefault();
            ev.stopPropagation();
            this.state.isExpanded = !this.state.isExpanded;
            this.colorlistRef.el.firstElementChild.focus();
        }
    }
}
