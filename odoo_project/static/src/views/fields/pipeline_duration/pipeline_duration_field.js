import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

import { Component, onWillRender, useEffect, useExternalListener, useRef } from "@odoo/owl";

export class PipelineDurationField extends Component {
    // related_related
    static template = "odoo_project.PipelineDurationField";
}

export const pipelineDurationField = {
    component: PipelineDurationField,
}

registry.category("fields").add("pipeline_duration", pipelineDurationField);
