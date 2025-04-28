/** @odoo-module **/

import { session } from '@web/session';
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";

const { Component, useState } = owl;

export class EistErpFooter extends Component {
    static template = 'eist_web_theme.Footer';
    static props = {
        slots: { type: Object, optional: true },
    };
    setup() {
        this.state = useState({
            theme: session['theme'],
            version: sprintf(_t('Version:%s'),session.server_version)
        });
    }
}
