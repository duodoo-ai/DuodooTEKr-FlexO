import { _t } from "@web/core/l10n/translation";
import { Component, useRef, useState, useExternalListener, onWillStart } from "@odoo/owl";

export class ThemeColorList extends Component {
    static COLORS = [
        _t("Default"),             // 0.默认 #e6edf5
        _t("Sky"),                 // 1.晴空 #315cd2
        _t("Bamboo"),              // 2.青竹 #687d56
        _t("Turquoise"),           // 3.松石 #40bda5
        _t("Sakura"),              // 4.花火 #eb8499
        _t("Ink"),                 // 5.沉墨 #3e465d
        _t("Lavender"),            // 6.菖蒲 #5a3f54
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
        // return session.theme.color.list;
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