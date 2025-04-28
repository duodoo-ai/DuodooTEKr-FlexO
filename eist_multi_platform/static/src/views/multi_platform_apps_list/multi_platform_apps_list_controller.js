/** @odoo-module **/

import { ListController } from '@web/views/list/list_controller';
import { useBus, useService } from '@web/core/utils/hooks';
import { onMounted, useRef } from '@odoo/owl';
import { _t } from '@web/core/l10n/translation';
import { sprintf } from '@web/core/utils/strings';
import { checkFileSize, DEFAULT_MAX_FILE_SIZE } from '@web/core/utils/files';
import { rpc } from '@web/core/network/rpc';
import { AppFileUploader } from '@eist_multi_platform/components/app_file_uploader/app_file_uploader';

export class MultiPlatformAppsListController extends ListController {
    static components = {
        ...ListController.components,
        AppFileUploader,
    };
    static props = {
        ...ListController.props,
        record: { type: Object, optional: true },
    };
    setup() {
        super.setup(...arguments);
        // this.resModel = this.props.resModel;
    }

}
