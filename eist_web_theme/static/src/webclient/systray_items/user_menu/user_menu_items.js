/** @odoo-module **/


import { registry } from "@web/core/registry";
import { Component, markup } from "@odoo/owl";
import { isMacOS } from "@web/core/browser/feature_detection";
import { _t } from "@web/core/l10n/translation";
import { escape } from "@web/core/utils/strings";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";
import { sprintf } from "@web/core/utils/strings";
const LockScreenInfoKey = "lockScreenInfo";

/*******************************************************************************
 * 关爱模式
 ******************************************************************************/
function careMode() {
    return {
        type: "switch",
        id: "care_mode",
        description: _t("Care Model"),
        callback: () => {
            alert("关爱模式正在开发中，敬请期待！");
        },
        // href: "/web/login?redirect=/care_model",
        sequence: 35,
        isChecked: false,
        icon: "fa fa-heart",
        // <i class="bi bi-suit-heart-fill"></i>
    };
}


/*******************************************************************************
 * 开发者模式
 ******************************************************************************/
function developerToolsItemSeparator() {
    let hide = false;
    if (show_debug) {
        hide = true;
    }else {
        hide = true;
    }
    return {
        type: "separator",
        sequence: 70,
        hide: hide,
    };
}

const isDebug = Boolean(odoo.debug);
const isAssets = odoo.debug.includes("assets");
const isTests = odoo.debug.includes("tests");

const show_debug = session["user_menu_items"].enable_developer_tool;

function toggleDevMode(mode) {
    // const url = window.location.href;
    // 获取当前 URL 的参数
    let searchParams = new URLSearchParams(window.location.search);

    // 修改参数值
    searchParams.set("debug", mode)

    // 创建一个新的 URL，但不替换当前的 URL，也不刷新页面
    const debug_url = `${window.location.origin}${window.location.pathname}?${searchParams.toString()}${window.location.hash}`;
    browser.open(debug_url, "_self");
}

function getQueryString(url_string, name) {
    const url = new URL(url_string);
    return url.searchParams.get(name);
}


function developerModeItem(env) {
    const url = "?debug=1";
    let hide = false;
    if (show_debug) {
        if (isDebug && !isAssets) {
            hide = true;
        }
    } else {
        hide = true;
    }

    return {
        type: "item",
        id: "developer_mode",
        description: _t("Activate the developer mode"),
        href: url,
        callback: () => {
            toggleDevMode("1");
        },
        sequence: 80,
        hide: hide,
        icon: "fa fa-bug",
    };
}

function developerAssetsModeItem(env) {
    const url = "?debug=assets";
    let hide = false;
    if (show_debug && isAssets) {
        hide = true;
    }else {
        hide = true;
    }

    return {
        type: "item",
        id: "developer_assets_mode",
        description: _t("Activate the developer mode (with assets)"),
        href: url,
        callback: () => {
            toggleDevMode("assets");
            // browser.open(url);
        },
        sequence: 90,
        hide: hide,
        icon: "fa fa-bug",
    };
}

function deactivateDeveloperModeItem(env) {
    const url = "?debug=";
    let hide = false;

    if (show_debug) {
        if (isDebug) {
            hide = false;
        } else {
            hide = true;
        }
    }else {
        hide = true;
    }
    return {
        type: "item",
        id: "deactivate_developer_mode",
        description: _t("Deactivate the developer mode"),
        href: url,
        callback: () => {
            // browser.open(url);
            toggleDevMode("0");
        },
        sequence: 100,
        hide: hide,
        icon: "fa fa-bug",
    };
}

/*******************************************************************************
 * 锁屏
 ******************************************************************************/

function lockScreenItemSeparator(env) {
    return {
        type: "separator",
        sequence: 100,
        hide: getLockScreenStatus(env),
    };
}

function getLockScreenStatus(env) {
    if (env.isSmall) {
        return true;
    } else {
        return !session["user_menu_items"].enable_lock_screen;
    }
}

function lockScreenItem(env) {
    const storage_mode = session.lock_screen_state_storage_mode;
    const lock_screen_info = {
        href: window.location.href, //完整URL
        host: window.location.host, //主机名
        pathname: window.location.pathname, //路径名
        search: window.location.search, //查询字符串
        hash: window.location.hash, //锚点（“#”后面的分段）
    };
    const route = "/web/lock";
    return {
        type: "item",
        id: "lock",
        description: _t("Lock Screen"),
        href: `${browser.location.origin}${route}`,
        callback: async () => {
            alert("客官，此功能正在开发中，敬请期待！");
            // const result = await env.services.rpc("/web/lockscreen", {
            //     uid: env.services.user.userId,
            //     lock_screen_info: lock_screen_info,
            // });

            // if (result["state"]) {
            //     if (result["storage_mode"] === 1) {
            //         // 1: 本地存储
            //         localStorage.setItem(
            //             LockScreenInfoKey,
            //             JSON.stringify(lock_screen_info)
            //         );
            //     }
            //     browser.location.href = route;
            // } else {
            //     const title = env._t("Operation failed!");
            //     const message = _.str.sprintf(
            //         "%s,%s",
            //         env._t("Failed to lock the screen!"),
            //         result["msg"]
            //     );
            //     env.services.notification.add(message, {
            //         title: title,
            //         type: "warning",
            //         sticky: false,
            //     });
            // }
        },
        sequence: 120,
        hide: getLockScreenStatus(env),
        icon: "fa fa-lock",
    };
}

function logOutItemSeparator() {
    return {
        type: "separator",
        sequence: 130,
    };
}


registry
    .category("user_menuitems")
    .add("care_mode", careMode)
    .add("dev_tool_separator", developerToolsItemSeparator)
    .add("dev_mode", developerModeItem)
    .add("dev_assets_mode", developerAssetsModeItem)
    .add("deactivate_dev_mode", deactivateDeveloperModeItem)
    .add("lock_screen_separator", lockScreenItemSeparator)
    .add("lock_screen", lockScreenItem)
    .add("logout_separator", logOutItemSeparator)

