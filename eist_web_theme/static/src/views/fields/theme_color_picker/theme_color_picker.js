import { ThemeColorList } from "@eist_web_theme/core/theme_colorlist/theme_colorlist";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component } from "@odoo/owl";

export class ThemeColorPickerField extends Component {
    static template = "eist_web_theme.ThemeColorPickerField";
    static components = {
        ThemeColorList,
    };
    static props = {
        ...standardFieldProps,
        canToggle: { type: Boolean },
    };

    static RECORD_COLORS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

    get isExpanded() {
        return !this.props.canToggle && !this.props.readonly;
    }

    switchColor(colorIndex) {
        this.props.record.update({ [this.props.name]: colorIndex });
    }
}

export const themeColorPickerField = {
    component: ThemeColorPickerField,
    supportedTypes: ["integer"],
    extractProps: ({ viewType }) => ({
        canToggle: viewType !== "list",
    }),
};

registry.category("fields").add("theme_color_picker", themeColorPickerField);
