/** @odoo-module **/

import { _t } from '@web/core/l10n/translation';
import { AssetsLoadingError, loadBundle, loadCSS, loadJS } from '@web/core/assets';
import { registry } from '@web/core/registry';
import { useBus } from '@web/core/utils/hooks';
import { standardFieldProps } from '@web/views/fields/standard_field_props';
import { Component, onMounted, onWillStart, onRendered, useRef, useState } from '@odoo/owl';
import { useRecordObserver } from '@web/model/relational_model/utils';
import { cookie } from '@web/core/browser/cookie';

export class JsonEditorField extends Component {
    static template = 'web.JsonEditorField';
    static props = {
        ...standardFieldProps,
        className: { type: String, optional: true },
        mode: { type: String, optional: true },
        modes: { type: Array, element: String, optional: true },
        darktheme: { type: Boolean, optional: true },
    };
    static defaultProps = {
        className: '',
        mode: 'code',
        darktheme: false,
    };

    setup() {
        this.editorRef = useRef('jsoneditor');
        // this.alertRef = useRef("alert");
        this.options = {
            mode: this.mode,
            modes: this.modes,
        };

        this.state = useState({});
        useRecordObserver((record) => {
            this.state.initialValue = record.data[this.props.name];
        });

        this.isDirty = false;
        const { model } = this.props.record;
        useBus(model.bus, 'WILL_SAVE_URGENTLY', () => this.commitChanges());
        useBus(model.bus, 'NEED_LOCAL_CHANGES', ({ detail }) => detail.proms.push(this.commitChanges()));

        const self = this;
        onWillStart(async () => {
            // await loadBundle({
            //     jsLibs: ['/web_jsoneditor/static/libs/jsoneditor/jsoneditor.js'],
            //     cssLibs: ['/web_jsoneditor/static/libs/jsoneditor/jsoneditor.css'],
            // });
            try {
                await Promise.all([
                    loadJS('/web_jsoneditor/static/libs/jsoneditor/jsoneditor.js'),
                    loadCSS('/web_jsoneditor/static/libs/jsoneditor/jsoneditor.css'),
                ]);
                if (this.darktheme) {
                    // 加载深色主题
                    loadBundle({
                        cssLibs: ['/web_jsoneditor/static/libs/jsoneditor/darktheme.css'],
                    });
                }
            } catch (error) {
                if (!(error instanceof AssetsLoadingError)) {
                    throw error;
                }
            }

            if (this.props.readonly) {
                // 只读模式
                this.options.onEditable = function (node) {
                    return false;
                };
            } else {
                // 编辑模式
                this.options.onChangeText = function (editedValue) {
                    // 变更内容
                    try {
                        const jsonObject = JSON.parse(editedValue);
                        self.handleChange(jsonObject);
                    } catch (error) {
                        // console.error('error:', error);
                    }
                };
                this.options.onValidationError = function (errors) {
                    // 检验json合法
                    // console.log('onValidationError', errors);
                    // this.alertRef.el
                };
                this.options.onValidate = function (editedValue) {
                    // 检验json合法
                    // console.log('onValidate', editedValue, typeof editedValue);
                };
            }
        });
        onMounted(() => {
            this.editor = new JSONEditor(this.editorRef.el, this.options, this.jsonValue);
            if (typeof this.jsonValue === 'string') {
                this.editor.updateText(this.jsonValue);
            }
        });
        // console.log('this.jsonValue', this.jsonValue);
        // console.log('this.jsonValue typeof', typeof this.jsonValue);
    }

    get formattedValue() {
        const value = this.props.record.data[this.props.name];
        return value ? JSON.stringify(value) : '';
    }

    get jsonValue() {
        let jsonValue = this.props.record.data[this.props.name];
        return jsonValue;
    }

    get initialValue() {
        return this.props.record.data[this.props.name];
    }

    get mode() {
        return this.props.mode || 'code';
    }

    get modes() {
        var modes = this.props.modes;
        if (!modes.includes('code')) {
            // 将 "code" 插入到数组的第一个位置
            modes.unshift('code');
        }
        return modes;
    }
    get darktheme() {
        if (cookie.get('color_scheme') === 'dark' || this.props.darktheme) {
            return true;
        } else {
            return false;
        }
    }

    handleChange(editedValue) {
        if (JSON.stringify(this.state.initialValue) !== JSON.stringify(editedValue)) {
            this.isDirty = true;
        } else {
            this.isDirty = false;
        }
        this.props.record.model.bus.trigger('FIELD_IS_DIRTY', this.isDirty);
        this.editedValue = editedValue;
    }

    async commitChanges() {
        if (!this.props.readonly && this.isDirty) {
            if (this.state.initialValue !== this.editedValue) {
                await this.props.record.update({ [this.props.name]: this.editedValue });
            }
            this.isDirty = false;
            this.props.record.model.bus.trigger('FIELD_IS_DIRTY', false);
        }
    }
}

export const jsonEditorField = {
    component: JsonEditorField,
    displayName: _t('Json Editor'),
    supportedTypes: ['jsonb'],
    supportedOptions: [
        {
            label: _t('Mode'),
            name: 'mode',
            type: 'string',
        },
        {
            label: _t('Modes'),
            name: 'modes',
            type: 'string',
        },
        {
            label: _t('Dark theme'),
            name: 'darktheme',
            type: 'boolean',
        },
    ],
    extractProps: ({ attrs, options }) => ({
        className: attrs.class,
        mode: options.mode || 'code',
        modes: options.modes || ['text', 'code', 'tree', 'form', 'view', 'preview'],
        darktheme: options.darktheme || false,
    }),
};

registry.category('fields').add('jsoneditor', jsonEditorField);
