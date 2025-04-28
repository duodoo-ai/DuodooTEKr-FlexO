/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component } from "@odoo/owl";

export class MaterialIconField extends Component {
    static template = "web.MaterialIconField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        useInputField({ getValue: () => this.props.record.data[this.props.name] || "" });
    }

    get name_lower() {
        return this.props.record.data[this.props.name].toLowerCase();
    }
}

export const materialIconField = {
    component: MaterialIconField,
    displayName: _t("Material Icon"),
    supportedTypes: ["char"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
};
registry.category("fields").add("material_icon", materialIconField);


// 表单字段
class FormMaterialIconField extends Component {
    static template = "web.FormMaterialIconField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        useInputField({ getValue: () => this.props.record.data[this.props.name] || "" });
    }

    get name_lower() {
        return this.props.record.data[this.props.name].toLowerCase();
    }
}

export const formMaterialIconField = {
    component: FormMaterialIconField,
    displayName: _t("Form Material Icon"),
    supportedTypes: ["char"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
};

registry.category("fields").add("form_material_icon", formMaterialIconField);

// 看板字段
class KanbanMaterialIconField extends Component {
    static template = "web.KanbanMaterialIconField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        useInputField({ getValue: () => this.props.record.data[this.props.name] || "" });
    }

    get name_lower() {
        return this.props.record.data[this.props.name].toLowerCase();
    }
}

export const kanbanMaterialIconField = {
    component: KanbanMaterialIconField,
    displayName: _t("Kanban Material Icon"),
    supportedTypes: ["char"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
};
registry.category("fields").add("kanbak_material_icon", kanbanMaterialIconField);