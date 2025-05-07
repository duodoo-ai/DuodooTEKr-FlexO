import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";
import { makeContext } from "@web/core/context";
import { rpc } from "@web/core/network/rpc";

const serviceRegistry = registry.category("services");

export const themeColorSchemeService = {
    dependencies: ["ui"],
    start(env, { ui }) {
        let currentThemeColor = session.theme?.color?.default || 0;

        return {
            /**
             * 获取当前主题颜色
             * @returns {number} 主题颜色ID
             */
            getCurrentThemeColor() {
                return currentThemeColor;
            },

            /**
             * 设置主题颜色
             * @param {number} colorId - 主题颜色ID
             */
            async setThemeColor(colorId) {
                const theme = {
                    theme_color: colorId,
                };

                await rpc("/web/dataset/call_kw/res.users/set_user_theme", {
                    model: "res.users",
                    method: "set_user_theme",
                    args: [],
                    kwargs: {
                        context: makeContext([theme], {}),
                    },
                });

                currentThemeColor = colorId;
                // 触发主题更新事件
                env.bus.trigger("THEME_COLOR_CHANGED", { colorId });
            },

            /**
             * 获取可用的主题颜色列表
             * @returns {Array} 主题颜色列表
             */
            getAvailableThemeColors() {
                return session.theme?.color?.colors || [];
            },
        };
    },
};

serviceRegistry.add("theme_color_scheme_service", themeColorSchemeService);
