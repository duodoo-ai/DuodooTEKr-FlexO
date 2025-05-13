/** @odoo-module **/


import { formatDuration } from "@web/core/l10n/dates";
import { sprintf } from "@web/core/utils/strings";
import { useBus, useService } from "@web/core/utils/hooks";
import { AssetsLoadingError, loadCSS, loadJS } from '@web/core/assets';
import { Component, useState, onWillStart, onMounted, onWillRender, onWillUnmount, useRef } from "@odoo/owl";
import { session } from "@web/session";

export class Overview extends Component {
    static template = "odoo_project.ProjectLargeScreen.Overview";
    static props = {

        projects: { type: Array },
    };
    setup() {
        this.tableRef = useRef("table");

        this.state = useState({
            shouldLoadJQ: false,
            shouldLoadTable: false,
            projects: this.props.projects,
            currentLang: session["bundle_params"]["lang"]
        })

        this.busService = this.env.services.bus_service;
        this.busService.subscribe("online_sync_pipeline", (notification) => {
            this.updatePipelineDataById(notification.id, notification.sync_data);
        });


        onWillStart(async () => {
            try {
                await Promise.all([
                    loadJS('/web/static/lib/jquery/jquery.js'),
                ])
                this.state.shouldLoadJQ = true;
                if (this.state.shouldLoadJQ) {
                    await Promise.all([
                        loadJS('/odoo_project/static/libs/datatables/js/dataTables.min.js'),
                        loadCSS('/odoo_project/static/libs/datatables/css/dataTables.dataTables.min.css'),
                    ])
                    this.state.shouldLoadTable = true;
                }
            } catch (error) {
                if (!(error instanceof AssetsLoadingError)) {
                    throw error;
                }
            }
        });

        onWillRender(() => {
            // console.log("onWillRender", this.state.shouldLoadJQ)
            // if (this.state.shouldLoadJQ) {
            //     this.state.shouldLoadTable = Promise.all([loadJS('/odoo_project/static/libs/datatables/js/dataTables.min.js') && loadCSS('/odoo_project/static/libs/datatables/css/dataTables.dataTables.min.css')]).then(() => new Promise(resolve => window.grecaptcha.ready(() => resolve())));
            // }
        });

        onMounted(() => {
            const self = this;
            // console.log("shouldLoadTable", this.state.shouldLoadTable)
            if (this.state.shouldLoadTable) {
                this.table = new DataTable(this.tableRef.el, {
                    deferRender: true, // 延迟渲染数据
                    paging: true, // 启用分页
                    lengthMenu: [5],
                    language: {
                        url: sprintf(
                            "/odoo_project/static/libs/datatables/i18n/%s.json",
                            self.state.currentLang
                        ),
                    },
                });
            }

        });
    }

    updatePipelineDataById(id, data) {
        // 使用 find 方法遍历 projects 数组，找到第一个满足条件的项目
        const project = this.state.projects.find((project) => project.id === id);

        // 使用 Object.entries 方法将 data 转换为键值对数组，然后遍历每个键值对
        Object.entries(data).forEach(([key, value]) => {
            // 打印当前正在更新的项目 id、键和值，方便调试
            // console.log("更新管道表格数据",project.id, key, value);
            // 将 data 中的键值对更新到找到的项目对象中
            project[key] = value;
        });
    }

    getPipelinepRunningTime(project) {
        const durationTracking = project.duration_tracking || {};
        const running_stage_id = project.running_stage_id;
        let duration = 0;

        if (Object.keys(durationTracking).length) {
            duration = durationTracking[running_stage_id] ?? 0
        }

        const shortTimeInStage = formatDuration(duration, false);
        const fullTimeInStage = formatDuration(duration, true);

        return fullTimeInStage
    }

}
