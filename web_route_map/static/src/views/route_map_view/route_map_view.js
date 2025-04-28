/* @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { RouteMapArchParser } from "./route_map_arch_parser";
import { RouteMapModel } from "./route_map_model";
import { RouteMapController } from "./route_map_controller";
import { RouteMapRenderer } from "./route_map_renderer";

export const routeMapView = {
    type: "route_map",
    Controller: RouteMapController,
    Renderer: RouteMapRenderer,
    Model: RouteMapModel,
    ArchParser: RouteMapArchParser,
    buttonTemplate: "web_route_map.RouteMapView.Buttons",

    props: (genericProps, view, config) => {
        let modelParams = genericProps.state;
        if (!modelParams) {
            const { arch, resModel, fields, context } = genericProps;
            const parser = new view.ArchParser();
            const archInfo = parser.parse(arch);
            const views = config.views || [];
            modelParams = {
                allowResequence: archInfo.allowResequence || false,
                context: context,
                defaultOrder: archInfo.defaultOrder,
                fieldNames: archInfo.fieldNames,
                fieldNamesMarkerPopup: archInfo.fieldNamesMarkerPopup,
                fields: fields,
                hasFormView: views.some((view) => view[1] === "form"),
                hideAddress: archInfo.hideAddress || false,
                hideName: archInfo.hideName || false,
                hideTitle: archInfo.hideTitle || false,
                limit: archInfo.limit || 80,
                numbering: archInfo.routing || false,
                offset: 0,
                panelTitle: archInfo.panelTitle || config.getDisplayName() || _t("Items"),
                resModel: resModel,
                resPartnerField: archInfo.resPartnerField,
                routing: archInfo.routing || false,
            };
        }

        return {
            ...genericProps,
            Model: view.Model,
            modelParams,
            Renderer: view.Renderer,
            buttonTemplate: view.buttonTemplate,
        };
    },
}

registry.category("views").add("route_map", routeMapView);
