import { _t } from '@web/core/l10n/translation';
import { sprintf } from '@web/core/utils/strings';
import { EistErpFooter } from '@eist_web_theme/webclient/footer/footer';
import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { formatDuration } from '@web/core/l10n/dates';

const { Component, useState } = owl;


patch(EistErpFooter.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            ...this.state,
            running_days: session['project']['running_days'],
        });
    },
    getRunningTime() {
        let runningTimeString = '';
        if (this.state.running_days == '0') {
            runningTimeString = sprintf(_t('The system continuously monitors %s days'), this.state.running_days);
        } else {
            const shortTimeString = formatDuration(this.state.running_days, false);
            const fullTimeString = formatDuration(this.state.running_days, true);
            runningTimeString = sprintf(_t('The system continuously monitors %s'), fullTimeString);
        }
        return runningTimeString;
    },
});
