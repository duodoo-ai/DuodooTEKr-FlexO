/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";


const { Component, useState, useRef, onMounted, onRendered, onPatched } = owl;


// --------------------------------------------------------------------------------
// DisplayPasswordChar
// --------------------------------------------------------------------------------
export class PasswordCharField extends Component {

    static template = "web.PasswordCharField";

    static props = {
        ...standardFieldProps,
        string: { type: String, optional: true },
        className: { type: String, optional: true },
        placeholder: { type: String, optional: true },
        shouldTrim: { type: Boolean, optional: true },
        encrypted: { type: Boolean, optional: true },
    };

    setup() {
        this.state = useState({
            ...this.state,
            encrypted: true,
        });

        // this.encrypted = true; // 是否加密
        this.input = useRef("input");
        this.button = useRef("button");
        this.popover = useService("popover");

        useInputField({
            getValue: () => this.props.record.data[this.props.name] || "",
            refName: "input",
            // parse: (v) => this.parse(v),
        });
        onMounted(() => {
            // console.log("-------onMounted", this.input.el)
            if (this.props.record.data[this.props.name].trim() != "" && this.input.el) {
                this.input.el.dataset.encrypted = "true";
            } else if (this.props.record.data[this.props.name].trim() == "" && this.input.el) {
                this.input.el.dataset.encrypted = "false";
            }
        });

        // onRendered(() => {
        //     // console.log("-------2", this.formattedValue)
        //     // if (this.props.record.data[this.props.name].trim() != "") {
        //     //     // this.state.encrypted = true;
        //     //     this.input.el.dataset.encrypted = "true";
        //     // } else {
        //     //     // this.state.encrypted = false;
        //     //     this.input.el.dataset.encrypted = "false";
        //     // }
        // });
    }

    parse(value) {
        if (this.shouldTrim) {
            return value.trim();
        }
        return value;
    }

    // onClick(event, value) {
    onClick() {
        let icon = this.button.el.firstChild;

        if (this.state.encrypted) {
            // 当前状态为加密状态，点击后变为解密状态
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
            this.input.el.dataset.encrypted = "false";
            this.state.encrypted = false;
        } else {
            // 当前状态为解密状态，点击后变为加密状态
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
            this.input.el.dataset.encrypted = "true";
            this.state.encrypted = true;
        }
    }
}


export const passwordCharField = {
    component: PasswordCharField,
    displayName: _t("Text is displayed in password characters"),
    supportedTypes: ["char"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
};

registry.category("fields").add("password_char", passwordCharField);