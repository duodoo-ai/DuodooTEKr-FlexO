/** @odoo-module **/

import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { MultiPlatformAppsListController } from '@eist_multi_platform/views/multi_platform_apps_list/multi_platform_apps_list_controller';

const multiPlatformAppsListView = {
    ...listView,
    Controller: MultiPlatformAppsListController,
    buttonTemplate: 'eist_multi_platform.MultiPlatformAppsListController.Buttons',
};

registry.category('views').add('multi_platform_apps_list_view', multiPlatformAppsListView);
