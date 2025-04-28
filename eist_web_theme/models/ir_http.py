# -*- coding: utf-8 -*-

import ast
import json
from odoo import models, _
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _post_logout(cls):
        request.future_response.set_cookie("color_scheme", max_age=0)

    def webclient_rendering_context(self):
        """
        覆盖社区版以防止不必要的load_menus请求
        """
        return {
            "session_info": self.session_info(),
        }

    def session_info(self):
        ICP = self.env["ir.config_parameter"].sudo()
        current_user = self.env.user
        current_user_company = current_user.company_id

        session_info = super(Http, self).session_info()

        # -------------------------------------------------------
        # 品牌
        # -------------------------------------------------------
        system_name = ICP.get_param("eist_erp.system_name", default="EIST ERP")
        display_company_name = ICP.get_param("eist_erp.display_company_name", default=False)

        if type(display_company_name) == str:
            display_company_name = bool(ast.literal_eval(display_company_name))

        session_info["brand"] = {
            "system_name": system_name,
            "display_company_name": display_company_name,
        }

        # -------------------------------------------------------
        # 语言
        # -------------------------------------------------------
        session_info["user_langs"] = {}
        langs = self.env["res.lang"].search_read([], ["name", "code", "flag_image_url"])
        for lang in langs:
            if lang["code"] == request.env.lang:  # type: ignore
                session_info["user_langs"].update({"current_lang": lang})
                break
        session_info["user_langs"].update({"langs": langs})

        # -------------------------------------------------------
        # 注册授权信息
        # -------------------------------------------------------
        if current_user.has_group("base.group_system"):
            warn_eist_erp = "admin"
        elif current_user.has_group("base.group_user"):
            warn_eist_erp = "user"
        else:
            warn_eist_erp = False

        session_info["support_url"] = "https://www.odoo.com/help"
        if warn_eist_erp:
            session_info["warning"] = warn_eist_erp
            session_info["expiration_date"] = ICP.get_param("database.expiration_date")
            session_info["expiration_reason"] = ICP.get_param("database.expiration_reason")

        # -------------------------------------------------------
        # 用户菜单项
        # -------------------------------------------------------
        session_info["user_menu_items"] = {}
        enable_odoo_account = current_user_company.enable_odoo_account
        enable_lock_screen = current_user_company.enable_lock_screen
        enable_developer_tool = current_user_company.enable_developer_tool
        enable_documentation = current_user_company.enable_documentation
        documentation_url = current_user_company.doc_url
        enable_support = current_user_company.enable_support
        support_url = current_user_company.support_url


        session_info["user_menu_items"].update(
            {
                "enable_odoo_account": enable_odoo_account,
                "enable_lock_screen": enable_lock_screen,
                "enable_developer_tool": enable_developer_tool,
                "support": {
                    "support_url": support_url,
                    "show": enable_support,
                },
                "documentation": {
                    "documentation_url": documentation_url,
                    "show": enable_documentation,
                },
            }
        )

        # -------------------------------------------------------
        # 主题
        # -------------------------------------------------------
        disable_theme_customizer = current_user_company.theme_id.disable_theme_customizer

        # 主题 1. Main
        # -------------------------------------------------------
        loading_method = dict(
            self.env["res.theme"].fields_get("main_app_load_method")["main_app_load_method"]["selection"]
        )
        loading_method_list = []
        for key, value in loading_method.items():
            mode = {"id": int(key), "name": value}
            if key == "1":
                mode.update({"icon": "bi-window-sidebar"})
            if key == "2":
                mode.update({"icon": "bi-list-stars"})
            if key == "3":
                mode.update({"icon": "bi-window-dock"})
            loading_method_list.append(mode)

        main_submenu_position_dict = dict(
            self.env["res.theme"].fields_get("main_submenu_position")["main_submenu_position"]["selection"]
        )
        main_submenu_position_list = []
        for key, value in main_submenu_position_dict.items():
            mode = {"id": int(key), "name": value}
            if key == "1":
                mode.update({"icon": "/eist_web_theme/static/img/submenu/submenu-header.png"})
            if key == "2":
                mode.update({"icon": "/eist_web_theme/static/img/submenu/submenu-sidebar.png"})
            if key == "3":
                mode.update({"icon": "/eist_web_theme/static/img/submenu/submenu-both.png"})
            main_submenu_position_list.append(mode)

        # 主题 3. Theme color
        # -------------------------------------------------------
        theme_color_list = [
            {"id": 0, "name": _("Light")},
            {"id": 1, "name": _("Red")},
            {"id": 2, "name": _("Orange")},
            {"id": 3, "name": _("Yellow")},
            {"id": 4, "name": _("Green")},
            {"id": 5, "name": _("Blue")},
            {"id": 6, "name": _("Indigo")},
            {"id": 7, "name": _("Lavender")},
            {"id": 8, "name": _("Mauve")},
            {"id": 9, "name": _("Grey")},
        ]

        # 主题 6. Views
        # -------------------------------------------------------
        views_form_chatter_position_dict = dict(
            self.env["res.theme"].fields_get("form_chatter_position")["form_chatter_position"]["selection"]
        )
        views_form_chatter_position_list = []
        for key, value in views_form_chatter_position_dict.items():
            mode = {"id": int(key), "name": value}
            if key == "1":
                mode.update({"icon": "bi-layout-sidebar-inset-reverse"})
            if key == "2":
                mode.update({"icon": "bi-text-wrap"})
            views_form_chatter_position_list.append(mode)

        views_list_rows_limit_dict = dict(
            self.env["res.theme"].fields_get("list_rows_limit")["list_rows_limit"]["selection"]
        )
        views_list_rows_limit_list = []
        for key, value in views_list_rows_limit_dict.items():
            row = {"value": int(key), "name": value}
            views_list_rows_limit_list.append(row)



        theme = {}
        theme_id = current_user.theme_id
        if disable_theme_customizer:
            # 如果关闭用户定制主题功能，则使用公司绑定的主题
            theme_id = current_user_company.theme_id

        theme = {
            "disable_customization": disable_theme_customizer,
            # 1.main
            "main": {
                "app_load_method": {
                    "default": theme_id.main_app_load_method,
                    "methods": loading_method_list,
                },
                "display_drawer_menu_button": theme_id.main_display_drawer_menu_button,
                "open_action_in_tabs": theme_id.main_open_action_in_tabs,
                "submenu": {
                    "position": int(theme_id.main_submenu_position),
                    "positions": main_submenu_position_list,
                },
            },
            # 3.Theme color
            "color": {
                "default": theme_id.theme_color,
                "colors": theme_color_list,
            },
            # 4.SideNavbar
            "sidebar": {
                "display_number_of_submenus": theme_id.sidebar_display_number_of_submenus,
                "show_minimize_button": theme_id.sidebar_show_minimize_button,
                "default_minimized": theme_id.sidebar_default_minimized,
                "hover_maximize": theme_id.sidebar_hover_maximize,
                "main_menu": {
                    "display_icon": theme_id.sidebar_main_menu_display_icon,
                    "display_arrow": theme_id.sidebar_main_menu_display_arrow,
                },
                "submenu": {
                    "display_icon": theme_id.sidebar_submenu_display_icon,
                    "display_arrow": theme_id.sidebar_submenu_display_arrow,
                },
            },
            # 6.Views
            "views": {
                "display_scroll_top_button": theme_id.display_scroll_top_button,
                "list": {
                    # "herder_fixed": theme_id.list_herder_fixed,
                    "rows": {
                        "limit": int(theme_id.list_rows_limit),
                        "limits": views_list_rows_limit_list,
                    },
                },
                "form": {
                    "chatter": {
                        "position": int(theme_id.form_chatter_position),
                        "positions": views_form_chatter_position_list,
                    }
                },
            },
            # 9.Footer
            "footer": {
                "display": theme_id.display_footer,
                "display_support": theme_id.display_footer_support,
                "support_url": current_user_company.support_url,
                "display_copyright": theme_id.display_footer_copyright,
                "copyright": current_user_company.copyright,
                "display_doc": theme_id.display_footer_doc,
                "doc_url": current_user_company.doc_url,
                "display_version": theme_id.display_footer_version,
            },
        }
        session_info.update({"theme": json.loads(json.dumps(theme))})

        return session_info
