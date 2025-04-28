/** @odoo-module **/

import { startWebClient } from "@web/start";
import { WebClientEistErp } from "./webclient/webclient";

/**
 * 此文件启动企业Web客户端。在 __manifest__.py 中，它替换社区版的 main.js 以加载不同的Web客户端类（ WebClientEistErp 而不是 WebClient ）
 */
startWebClient(WebClientEistErp);
