/* @odoo-module */

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { KanbanHeader } from "@web/views/kanban/kanban_header";

import { _t } from "@web/core/l10n/translation";
import { user } from "@web/core/user";



registry.category("kanban_header_config_items").add(
    "open_automations",
    {
        label: _t("Automations"),
        method: "openAutomations",
        isVisible: ({ permissions }) => permissions.canEditAutomations,
        class: "o_column_automations",
    },
    { sequence: 25, force: true }
);
