import { aceField } from "@web/views/fields/ace/ace_field";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

aceField.supportedTypes = ["text", "html", "jsonb"];

registry.category("fields").add("json", aceField);