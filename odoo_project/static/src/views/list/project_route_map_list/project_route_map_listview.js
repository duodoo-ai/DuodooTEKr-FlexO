/** @odoo-module */

import { useService } from '@web/core/utils/hooks';
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { ListRenderer } from '@web/views/list/list_renderer';
import { TencentProjectRouteMap } from '@odoo_project/components/tencent_project_route_map/tencent_project_route_map';
import { AmapProjectRouteMap } from '@odoo_project/components/amap_project_route_map/amap_project_route_map';

import { onMounted, onRendered, onPatched, useState, onWillStart } from '@odoo/owl';

export class ProjectRouteMapListRenderer extends ListRenderer {
    static template = 'project.ProjectRouteMapListView';
    static components = Object.assign({}, ListRenderer.components, { TencentProjectRouteMap, AmapProjectRouteMap });

    setup() {
        super.setup(...arguments);
        this.orm = useService('orm');

        this.state = useState({
            ...this.state,
        });

        if (this.props.list.records.length > 0) {
            this.state.current_list_ids = this.getCurrentListIds(this.props.list.records);
        }

        const self = this;
        if (this.props.list.records.length > 0) {
            this.props.list.records.forEach((record) => {
                if (!self.state.current_list_ids.includes(record.resId)) {
                    self.state.current_list_ids.push(record.resId);
                }
            });
        }

        onWillStart(async () => {
            this.state.emap_provider = await this.getEmapProvider();
            console.log("emap_provider", this.state.emap_provider);
            this.state.projects = await this.getProjects();
        });

        onMounted(() => {
            // console.log("onMounted", this.props)
            this.rootRef.el.parentElement.classList.add('d-flex', 'justify-content-between');
        });
        onPatched(async () => {
            if (this.props.list.records.length > 0) {
                // this.props.list.records.forEach(record => {
                //     if (!self.state.current_list_ids.includes(record.resId)) {
                //         self.state.current_list_ids.push(record.resId)
                //     }
                // })
            }
        });
        onRendered(() => {});
    }

    getCurrentListIds(records) {
        let current_list_ids = [];
        records.forEach((record) => {
            if (!current_list_ids.includes(record.resId)) {
                current_list_ids.push(record.resId);
            }
        });
        return current_list_ids;
    }

    async getEmapProvider() {
        return await this.orm.call('res.config.settings', 'get_emap_provider_info');
    }

    async getProjects() {
        return await this.orm.call('project.project', 'get_locations_by_project_ids', [this.state.current_list_ids]);
    }
}

export const ProjectRouteMapListView = {
    ...listView,
    Renderer: ProjectRouteMapListRenderer,
};

registry.category('views').add('project_route_map_list', ProjectRouteMapListView);
