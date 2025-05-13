/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { rpc } from '@web/core/network/rpc';
import { registry } from '@web/core/registry';
import { Component, useState, onWillStart, onMounted, onWillUnmount } from '@odoo/owl';
import { useBus, useService } from '@web/core/utils/hooks';
import { standardActionServiceProps } from '@web/webclient/actions/action_service';
import { TencentProjectRouteMap } from '@odoo_project/components/tencent_project_route_map/tencent_project_route_map';
import { AmapProjectRouteMap } from '@odoo_project/components/amap_project_route_map/amap_project_route_map';
import { Header } from './components/header/header';
import { Dashboard } from './components/dashboard/dashboard';
import { Overview } from './components/overview/overview';

export class PipelineLargeScreen extends Component {
    static template = 'odoo_project.PipelineLargeScreen';
    static components = {
        TencentProjectRouteMap,
        AmapProjectRouteMap,
        Header,
        Dashboard,
        Overview,
    };
    static props = {
        ...standardActionServiceProps,
    };

    setup() {
        this.actionService = useService('action');
        this.state = useState({
            has_error: false,
            error_message: '',
            geo_provider: {},
            projects: {},
            pipeline_data: {},
            fullscreen: true,
        });
        this.pwaService = useService('pwa');
        this.dm = useService('drawer_menu');

        // 检查窗口大小的方法
        this.checkWindowSize = () => {
            if (window.innerWidth < 1024) {
                this.state.has_error = true;
                this.state.error_message = _t(
                    'The screen width is insufficient, please use a larger screen to view the large screen display. Minimum width requirement: 1024px'
                );
            } else {
                this.state.has_error = false;
                this.state.error_message = '';
            }
        };

        onWillStart(async () => {
            // 检查浏览器窗口宽度
            this.checkWindowSize();

            const data = await rpc('/pipeline/large_screen_data');

            this.state.geo_provider = data.provider_info;
            this.state.projects = data.projects;
            this.state.title = data.title;

            let total_traffic = 0; // 总流量
            let monthly_traffic = 0; // 当月流量
            let seasonal_traffic = 0; // 当季流量
            let year_traffic = 0; // 当年流量

            let running_pipeline_qty = 0; // 运营中管线数量
            let stopped_pipeline_qty = 0; // 停止运营管线数量

            data.projects.forEach((project) => {
                total_traffic += project.total_traffic;
                monthly_traffic += project.monthly_traffic;
                seasonal_traffic += project.seasonal_traffic;
                year_traffic += project.year_traffic;
                if (project.stage === 'running') {
                    running_pipeline_qty += 1;
                }
                if (project.stage === 'stopped') {
                    stopped_pipeline_qty += 1;
                }
            });
            this.state.pipeline_data = {
                total_pipeline_qty: data.projects.length, // 管线数量
                running_pipeline_qty: running_pipeline_qty, // 运营中管线数量
                stopped_pipeline_qty: stopped_pipeline_qty, // 停止运营管线数量
                total_traffic: total_traffic, // 总流量
                monthly_traffic: monthly_traffic, // 当月流量
                seasonal_traffic: seasonal_traffic, // 当季流量
                year_traffic: year_traffic, // 当季流量
            };
        });

        onMounted(() => {
            // 设置 body 的 data-fullscreen 属性
            document.body.setAttribute('data-fullscreen', 'true');
            // 添加resize事件监听器
            window.addEventListener('resize', this.checkWindowSize);
        });

        onWillUnmount(() => {
            // 移除resize事件监听器
            window.removeEventListener('resize', this.checkWindowSize);
        });
    }
}

registry.category('actions').add('pipeline_large_screen', PipelineLargeScreen);
// registry.category("public_components").add("project_large_screen", PipelineLargeScreen);
