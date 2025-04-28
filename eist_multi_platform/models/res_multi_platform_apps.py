# -*- coding: utf-8 -*-

import os
import shutil
import logging
import base64
import subprocess
import re
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import file_open, file_path
from odoo.modules import get_resource_from_path, get_module_path


_logger = logging.getLogger(__name__)


class ResMultiPlatformApps(models.Model):
    """
    发布应用管理
    """

    _name = "res.multi_platform.apps"
    _description = "Multi-platform app publishing"

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    description = fields.Text(string="Description")
    platform = fields.Selection(
        [
            ("windows", "Windows"),
            ("macos", "MacOS"),
            ("linux", "Linux"),
            ("android", "Android"),
            ("ios", "iOS"),
            ("other", "Other"),
        ],
        string="Platform",
        required=True,
        readonly=True,
        store=True,
    )
    version = fields.Char(
        string="Version",
        required=True,
        readonly=True,
        store=True,
        help="The application version number, which is automatically read from the installation file",
    )
    build_number = fields.Char(
        "Build number",
        readonly=True,
        store=True,
        help="The build number, which is automatically read from the installation file",
    )
    package_name = fields.Char(
        "Package name",
        readonly=True,
        store=True,
        help="The package name, which is automatically read from the installation file",
    )
    app_file_path = fields.Char(string="App Path", readonly=True, store=True)
    app_filename = fields.Char(string="App Name", readonly=True, store=True)
    app_file_size = fields.Float("App file size(MB)", readonly=True, store=True)
    url = fields.Char(string="URL", store=True, compute="_compute_url")
    is_published = fields.Boolean(string="Published", default=False)

    # 版本号和平台唯一值
    _sql_constraints = [
        ("version_platform_unique", "unique (version, platform)", "The version and platform must be unique."),
    ]

    # --------------------------------------------------------
    # 计算字段
    # --------------------------------------------------------
    @api.depends("platform", "version")
    def _compute_name(self):
        for app in self:
            app.name = f"{app.platform}_{app.version}"

    @api.depends("app_file_path")
    def _compute_url(self):
        for app in self:
            app_file_path = app.app_file_path
            if "\\" in app_file_path:
                app_file_path = app_file_path.replace("\\", "/")
            app.url = f"{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}/{app_file_path}"

    # --------------------------------------------------------
    # ORM 方法
    # --------------------------------------------------------
    def unlink(self):
        """删除记录时同时删除文件"""
        for record in self:
            if record.app_file_path:
                try:
                    root_dir = self._get_upload_root_dir()
                    platform_dir = record.platform or "other"
                    version_dir = record.version or "1.0.0"
                    absolute_path = os.path.join(root_dir, platform_dir, version_dir, record.app_filename)

                    if os.path.exists(absolute_path):
                        os.unlink(absolute_path)
                except Exception as e:
                    _logger.error(_("Failed to delete the file:%s") % str(e))
        return super().unlink()

    # --------------------------------------------------------
    # 文件上传相关
    # --------------------------------------------------------
    # region 文件上传相关

    def _get_upload_root_dir(self):
        """获取上传根目录"""
        module_path = get_module_path("eist_multi_platform")
        root_dir = os.path.join(module_path, "static", "app_files")
        os.makedirs(root_dir, exist_ok=True)
        return root_dir

    def _get_temp_dir(self):
        """获取临时目录路径"""
        root_dir = self._get_upload_root_dir()
        temp_dir = os.path.join(root_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def _ensure_directory(self, file_path):
        """确保目录存在"""
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _detect_platform(self, filename):
        """根据文件名检测平台"""
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".exe":
            return "windows"
        elif ext == ".apk":
            return "android"
        elif ext == ".ipa":
            return "ios"
        elif ext == ".dmg":
            return "macos"
        elif ext == ".deb" or ext == ".rpm":
            return "linux"
        return "other"

    def _normalize_version(self, version):
        """标准化版本号格式"""
        if not version:
            return "1.0.0"

        try:
            # 移除所有非数字和点的字符
            version = re.sub(r"[^0-9.]", "", version)

            # 分割版本号
            parts = version.split(".")

            # 确保至少有三个部分 (x.y.z)
            while len(parts) < 3:
                parts.append("0")

            # 只保留前四个部分 (x.y.z.w)
            parts = parts[:4]

            # 确保每个部分都是有效的数字
            parts = [str(int(p)) for p in parts]

            return ".".join(parts)
        except:
            return "1.0.0"

    def _get_windows_exe_info(self, file_path):
        """获取Windows EXE文件信息"""
        # 临时禁用
        return None
        # try:
        #     from odoo.addons.eist_multi_platform.utils.win_utils import get_exe_info
        #
        #     # 等待文件完全写入
        #     file_size = 0
        #     last_size = -1
        #     retry_count = 0
        #     max_retries = 10
        #
        #     while retry_count < max_retries:
        #         try:
        #             if os.path.exists(file_path):
        #                 file_size = os.path.getsize(file_path)
        #                 if file_size > 0 and file_size == last_size:
        #                     break
        #                 last_size = file_size
        #             retry_count += 1
        #             if retry_count < max_retries:
        #                 import time
        #
        #                 time.sleep(1)  # 等待1秒再次检查
        #         except Exception as e:
        #             _logger.warning(_("Error checking file size: %s") % str(e))
        #             break
        #
        #     if file_size == 0:
        #         raise UserError(_("The file appears to be empty or not accessible"))
        #
        #     info = get_exe_info(file_path)
        #     if not info:
        #         raise UserError(_("Unable to read version information from the EXE file"))
        #
        #     # 提取详细版本信息
        #     version = None
        #     version_fields = [
        #         "FileVersion",
        #         "ProductVersion",
        #         "file_version",
        #         "product_version",
        #         "version",
        #     ]
        #
        #     # 尝试从所有可能的字段获取版本信息
        #     for field in version_fields:
        #         version = info.get(field)
        #         if version:
        #             # 检查是否是有效的版本号格式
        #             normalized_version = self._normalize_version(version)
        #             if normalized_version != "1.0.0":
        #                 break
        #
        #     if not version:
        #         raise UserError(_("No version information found in the EXE file"))
        #
        #     # 标准化版本号
        #     version = self._normalize_version(version)
        #     if version == "1.0.0":
        #         raise UserError(
        #             _(
        #                 "Invalid version format in the EXE file. Please ensure the file contains valid version information."
        #             )
        #         )
        #
        #     # 提取构建号
        #     build_number = info.get("build_number", "")
        #     if not build_number:
        #         # 尝试从版本号中提取构建号
        #         version_parts = version.split(".")
        #         if len(version_parts) >= 4:
        #             build_number = version_parts[3]
        #
        #     # 提取包名
        #     package_name = (
        #         info.get("original_filename", "")
        #         or info.get("internal_name", "")
        #         or info.get("product_name", "")
        #         or info.get("OriginalFilename", "")
        #         or info.get("InternalName", "")
        #         or info.get("ProductName", "")
        #         or os.path.splitext(os.path.basename(file_path))[0]  # 如果没有包名，使用文件名（不含扩展名）
        #     )
        #
        #     return {
        #         "version": version,
        #         "build_number": build_number,
        #         "package_name": package_name,
        #     }
        # except UserError:
        #     raise
        # except Exception as e:
        #     _logger.error(_("Failed to get Windows EXE information: %s") % str(e))
        #     raise UserError(_("Failed to read version information from the EXE file. Error: %s") % str(e))

    def _get_android_apk_info(self, file_path):
        """获取Android APK文件信息"""
        # 临时禁用
        return None
        # try:
        #     from odoo.addons.eist_multi_platform.utils.android_utils import get_apk_info
        #
        #     info = get_apk_info(file_path)
        #
        #     # 获取版本号
        #     version = info.get("version_name")
        #     if not version:
        #         raise UserError(_("Unable to read version information from APK file"))
        #
        #     # 标准化版本号
        #     version = self._normalize_version(version)
        #     if version == "1.0.0":
        #         raise UserError(_("Unable to read valid version information from APK file"))
        #
        #     return {
        #         "version": version,
        #         "build_number": str(info.get("version_code", "")),
        #         "package_name": info.get("package_name", ""),
        #     }
        # except Exception as e:
        #     _logger.error(_("Failed to get Android APK information:%s") % str(e))
        #     raise UserError(_("Failed to get Android APK information:%s") % str(e))

    def _get_macos_app_info(self, file_path):
        """获取MacOS应用信息"""
        # 临时禁用
        return None
        # try:
        #     # 尝试读取Info.plist文件
        #     if file_path.endswith(".app"):
        #         plist_path = os.path.join(file_path, "Contents", "Info.plist")
        #     elif file_path.endswith(".dmg"):
        #         # TODO: 处理DMG文件，需要先挂载
        #         raise UserError(_("Currently, the DMG file format is not supported"))
        #
        #     if not os.path.exists(plist_path):
        #         raise UserError(_("Unable to find version information file (Info.plist)"))
        #
        #     import plistlib
        #
        #     with open(plist_path, "rb") as fp:
        #         plist = plistlib.load(fp)
        #         version = plist.get("CFBundleShortVersionString")
        #         if not version:
        #             raise UserError(_("Unable to read version information from the application"))
        #
        #         # 标准化版本号
        #         version = self._normalize_version(version)
        #         if version == "1.0.0":
        #             raise UserError(_("Unable to read version information from the application"))
        #
        #         return {
        #             "version": version,
        #             "build_number": plist.get("CFBundleVersion", ""),
        #             "package_name": plist.get("CFBundleIdentifier", ""),
        #         }
        # except Exception as e:
        #     _logger.error(_("Failed to get MacOS application information:%s") % str(e))
        #     raise UserError(_("Failed to get MacOS application information:%s") % str(e))

    def _get_linux_package_info(self, file_path):
        """获取Linux包信息"""
        # 临时禁用
        return None
        # try:
        #     if file_path.endswith(".deb"):
        #         # 使用dpkg-deb获取信息
        #         result = subprocess.run(
        #             ["dpkg-deb", "-f", file_path, "Version", "Package"],
        #             capture_output=True,
        #             text=True,
        #         )
        #         if result.returncode != 0:
        #             raise UserError(_("Unable to read DEB package information"))
        #
        #         lines = result.stdout.strip().split("\n")
        #         version = lines[0] if len(lines) > 0 else None
        #         package = lines[1] if len(lines) > 1 else ""
        #
        #         if not version:
        #             raise UserError(_("Unable to read version information from DEB package"))
        #
        #         # 标准化版本号
        #         version = self._normalize_version(version)
        #         if version == "1.0.0":
        #             raise UserError(_("Unable to read valid version information from DEB package"))
        #
        #         return {
        #             "version": version,
        #             "build_number": "",
        #             "package_name": package,
        #         }
        #     elif file_path.endswith(".rpm"):
        #         # 使用rpm命令获取信息
        #         result = subprocess.run(
        #             ["rpm", "-qp", "--queryformat", "%{VERSION}\n%{RELEASE}\n%{NAME}", file_path],
        #             capture_output=True,
        #             text=True,
        #         )
        #         if result.returncode != 0:
        #             raise UserError(_("Unable to read RPM package information"))
        #
        #         lines = result.stdout.strip().split("\n")
        #         version = lines[0] if len(lines) > 0 else None
        #         build = lines[1] if len(lines) > 1 else ""
        #         package = lines[2] if len(lines) > 2 else ""
        #
        #         if not version:
        #             raise UserError(_("Unable to read version information from RPM package"))
        #
        #         # 标准化版本号
        #         version = self._normalize_version(version)
        #         if version == "1.0.0":
        #             raise UserError(_("Unable to read valid version information from RPM package"))
        #
        #         return {
        #             "version": version,
        #             "build_number": build,
        #             "package_name": package,
        #         }
        #     else:
        #         raise UserError(_("Unsupported Linux package format"))
        # except Exception as e:
        #     _logger.error(_("Failed to get Linux package information:%s") % str(e))
        #     raise UserError(_("Failed to get Linux package information:%s") % str(e))

    def _get_app_info(self, file_path, platform):
        """获取应用信息"""
        # 临时返回默认值，用于测试文件上传功能
        return {
            "version": "1.0.0",
            "build_number": "1",
            "package_name": os.path.splitext(os.path.basename(file_path))[0],
        }

        # if platform == "windows":
        #     return self._get_windows_exe_info(file_path)
        # elif platform == "android":
        #     return self._get_android_apk_info(file_path)
        # elif platform == "macos":
        #     return self._get_macos_app_info(file_path)
        # elif platform == "linux":
        #     return self._get_linux_package_info(file_path)
        # else:
        #     raise UserError(_("Unsupported platform types"))

    def _is_valid_version(self, version):
        """检查版本号格式是否有效"""
        try:
            # 检查基本的版本号格式（x.y.z 或 x.y.z.w）
            pattern = r"^\d+(\.\d+){1,3}$"
            if not re.match(pattern, version):
                return False

            # 检查每个数字部分是否在合理范围内
            parts = [int(p) for p in version.split(".")]
            return all(p >= 0 and p < 65536 for p in parts)
        except:
            return False

    @api.model
    def upload_small_file(self, session_id, file_content, filename, force_update=False):
        """
        上传小文件（小于  DEFAULT_MAX_FILE_SIZE 的文件）
        Args:
            session_id: 上传会话ID
            file_content: 文件内容（base64编码）
            filename: 文件名
            force_update: 是否强制更新
        Returns:
            dict: 包含创建的记录信息的动作
        """
        temp_file_path = None
        try:
            # 获取临时目录
            temp_dir = self._get_temp_dir()
            temp_file_path = os.path.join(temp_dir, filename)

            # 保存文件
            with open(temp_file_path, "wb") as f:
                f.write(base64.b64decode(file_content))

            # 检测平台
            platform = self._detect_platform(filename)

            # 获取相对路径和最终路径
            relative_path = os.path.join(
                "eist_multi_platform", "static", "app_files", platform, "temp", filename
            )
            root_dir = self._get_upload_root_dir()
            temp_final_path = os.path.join(root_dir, platform, "temp", filename)

            # 确保临时目录存在
            os.makedirs(os.path.dirname(temp_final_path), exist_ok=True)

            # 移动文件到临时最终位置
            shutil.move(temp_file_path, temp_final_path)
            temp_file_path = temp_final_path  # 更新临时文件路径

            # 确保文件移动完成
            import time

            time.sleep(1)  # 等待文件系统同步

            # 获取应用信息
            app_info = self._get_app_info(temp_final_path, platform)
            if not app_info:
                raise UserError(_("Unable to read application version information"))

            # 确保版本号有效
            version = app_info.get("version")
            build_number = app_info.get("build_number")
            if not self._is_valid_version(version):
                raise UserError(_("Invalid version number format: %s") % version)

            # 检查版本是否存在
            existing_record = self._check_version_exists(platform, version, build_number)
            if existing_record:
                if not force_update:
                    raise UserError(
                        _(
                            "Version %(version)s (build number: %(build)s) already exists. \n"
                            'If you want to overwrite an existing version, tick the "Force Update" option. '
                        )
                        % {"version": version, "build": build_number or None}
                    )
                else:
                    # 如果是强制更新，删除旧记录和文件
                    old_file_path = existing_record.app_file_path
                    if old_file_path and os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                            _logger.info(_("Deleted old version file: %s") % old_file_path)
                        except Exception as e:
                            _logger.error(_("Failed to delete old version file: %s") % str(e))
                    existing_record.unlink()
                    _logger.info(
                        _("The old version record has been deleted, version: %s, build number: %s")
                        % (version, build_number or None)
                    )

            # 移动文件到最终位置
            final_relative_path = os.path.join(
                "eist_multi_platform", "static", "app_files", platform, version, filename
            )
            final_path = os.path.join(root_dir, platform, version, filename)

            # 确保目录存在
            os.makedirs(os.path.dirname(final_path), exist_ok=True)

            # 移动文件到最终位置
            # shutil.copy(temp_final_path, final_path)
            shutil.move(temp_final_path, final_path)

            # 创建记录
            vals = {
                "platform": platform,
                "version": version,
                "build_number": build_number,
                "package_name": app_info.get("package_name"),
                "app_filename": filename,
                "app_file_path": final_relative_path,
            }

            record = self.create(vals)
            record._update_file_size()

            return {
                "type": "ir.actions.act_window",
                "res_model": "res.multi_platform.apps",
                "res_id": record.id,
                "view_mode": "form",
                "view_type": "form",
                "views": [(False, "form")],
                "target": "current",
            }

        except Exception as e:
            _logger.error(_("Failed to upload file: %s") % str(e))
            raise UserError(_("Failed to upload file: %s") % str(e))
        finally:
            # 清理临时文件
            try:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                _logger.error(_("Failed to clean up temporary file: %s") % str(e))

    @api.model
    def upload_chunk(
        self, session_id, chunk_index, total_chunks, chunk_content, filename, force_update=False
    ):
        """
        上传文件分片
        Args:
            session_id: 上传会话ID
            chunk_index: 分片索引
            total_chunks: 总分片数
            chunk_content: 分片内容（base64编码）
            filename: 文件名
            force_update: 是否强制更新
        """
        print("upload_chunk", session_id, chunk_index, total_chunks, filename, force_update)
        try:
            # 获取临时目录
            temp_dir = self._get_temp_dir()
            session_dir = os.path.join(temp_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)

            # 保存分片
            chunk_file = os.path.join(session_dir, f"chunk_{chunk_index}")
            with open(chunk_file, "wb") as f:
                f.write(base64.b64decode(chunk_content))

            return True
        except Exception as e:
            _logger.error(_("Failed to upload chunk: %s") % str(e))
            raise UserError(_("Failed to upload chunk: %s") % str(e))

    @api.model
    def complete_upload(self, session_id, filename, force_update=False):
        """
        完成文件上传
        Args:
            session_id: 上传会话ID
            filename: 文件名
            force_update: 是否强制更新
        Returns:
            dict: 包含创建的记录信息的动作
        """
        print("complete_upload", session_id, filename, force_update)
        temp_file_path = None
        session_dir = None
        try:
            # 获取会话目录
            temp_dir = self._get_temp_dir()
            session_dir = os.path.join(temp_dir, session_id)
            if not os.path.exists(session_dir):
                raise UserError(_("Upload session not found"))

            # 获取所有分片文件
            chunk_files = sorted(
                [f for f in os.listdir(session_dir) if f.startswith("chunk_")],
                key=lambda x: int(x.split("_")[1]),
            )

            # 合并分片
            temp_file_path = os.path.join(temp_dir, filename)
            with open(temp_file_path, "wb") as outfile:
                for chunk_file in chunk_files:
                    chunk_path = os.path.join(session_dir, chunk_file)
                    with open(chunk_path, "rb") as infile:
                        outfile.write(infile.read())

            # 检测平台
            platform = self._detect_platform(filename)

            # 获取相对路径和最终路径
            relative_path = os.path.join(
                "eist_multi_platform", "static", "app_files", platform, "temp", filename
            )
            root_dir = self._get_upload_root_dir()
            temp_final_path = os.path.join(root_dir, platform, "temp", filename)

            # 确保临时目录存在
            os.makedirs(os.path.dirname(temp_final_path), exist_ok=True)

            # 移动文件到临时最终位置
            shutil.move(temp_file_path, temp_final_path)
            temp_file_path = temp_final_path  # 更新临时文件路径

            # 确保文件移动完成
            import time

            time.sleep(1)  # 等待文件系统同步

            # 获取应用信息
            app_info = self._get_app_info(temp_final_path, platform)
            if not app_info:
                raise UserError(_("Unable to read application version information"))

            # 确保版本号有效
            version = app_info.get("version")
            build_number = app_info.get("build_number")
            if not self._is_valid_version(version):
                raise UserError(_("Invalid version number format: %s") % version)

            # 检查版本是否存在
            existing_record = self._check_version_exists(platform, version, build_number)
            if existing_record:
                if not force_update:
                    raise UserError(
                        _(
                            "Version %(version)s (build number: %(build)s) already exists. \n"
                            'If you want to overwrite an existing version, tick the "Force Update" option. '
                        )
                        % {"version": version, "build": build_number or None}
                    )
                else:
                    # 如果是强制更新，删除旧记录和文件
                    old_file_path = existing_record.app_file_path
                    if old_file_path and os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                            _logger.info(_("Deleted old version file: %s") % old_file_path)
                        except Exception as e:
                            _logger.error(_("Failed to delete old version file: %s") % str(e))
                    existing_record.unlink()
                    _logger.info(
                        _("The old version record has been deleted, version: %s, build number: %s")
                        % (version, build_number or None)
                    )

            # 移动文件到最终位置
            final_relative_path = os.path.join(
                "eist_multi_platform", "static", "app_files", platform, version, filename
            )
            final_path = os.path.join(root_dir, platform, version, filename)

            # 确保目录存在
            os.makedirs(os.path.dirname(final_path), exist_ok=True)

            # 移动文件到最终位置
            shutil.move(temp_final_path, final_path)

            # 创建记录
            vals = {
                "platform": platform,
                "version": version,
                "build_number": build_number,
                "package_name": app_info.get("package_name"),
                "app_filename": filename,
                "app_file_path": final_relative_path,
            }

            record = self.create(vals)
            record._update_file_size()

            return {
                "type": "ir.actions.act_window",
                "res_model": "res.multi_platform.apps",
                "res_id": record.id,
                "view_mode": "form",
                "view_type": "form",
                "views": [(False, "form")],
                "target": "current",
            }

        except Exception as e:
            _logger.error(_("Failed to complete upload: %s") % str(e))
            raise UserError(_("Failed to complete upload: %s") % str(e))
                # finally:
                #     pass
                    # 清理临时文件
            try:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                if session_dir and os.path.exists(session_dir):
                    shutil.rmtree(session_dir)
            except Exception as e:
                _logger.error(_("Failed to clean up temporary files: %s") % str(e))

    def _update_file_size(self):
        """更新文件大小"""
        try:
            if self.app_file_path:
                root_dir = self._get_upload_root_dir()
                platform_dir = self.platform or "other"
                version_dir = self.version or "1.0.0"
                absolute_path = os.path.join(root_dir, platform_dir, version_dir, self.app_filename)

                if os.path.exists(absolute_path):
                    # 获取文件大小（字节）并转换为MB
                    size_in_mb = os.path.getsize(absolute_path) / (1024 * 1024)
                    self.app_file_size = round(size_in_mb, 2)
                else:
                    self.app_file_size = 0
        except Exception as e:
            _logger.error(_("Failed to update file size:%s") % str(e))
            self.app_file_size = 0

    def action_upload_app_file(self, record_id=None, app_id=None):
        """上传应用文件后的动作"""
        if app_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "res.multi_platform.apps",
                "res_id": app_id,
                "view_mode": "form",
                "view_type": "form",
                "views": [(False, "form")],
                "target": "current",
            }
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def _check_version_exists(self, platform, version, build_number=None):
        """检查指定版本是否已存在
        Args:
            platform: 平台
            version: 版本号
            build_number: 构建号
        Returns:
            存在返回记录，不存在返回False
        """
        domain = [
            ("platform", "=", platform),
            ("version", "=", version),
        ]
        if build_number:
            domain.append(("build_number", "=", build_number))

        existing_record = self.search(domain, limit=1)
        return existing_record if existing_record else False

    @api.model
    def create_from_upload(self, temp_file_path, force_update=False):
        """从上传文件创建应用记录
        Args:
            temp_file_path: 临时文件路径
            force_update: 是否强制更新
        Returns:
            创建的记录ID
        """
        try:
            # 获取文件信息
            platform, app_info = self._get_app_info(temp_file_path)
            if not platform or not app_info:
                raise UserError(_("Unable to recognize the application type or get version information"))

            version = app_info.get("version")
            build_number = app_info.get("build_number")

            # 检查版本是否存在
            existing_record = self._check_version_exists(platform, version, build_number)
            if existing_record:
                if not force_update:
                    # 如果版本已存在且不是强制更新，则提示用户
                    raise UserError(
                        _(
                            "Version %(version)s (build number: %(build)s) already exists. \n"
                            'If you want to overwrite an existing version, tick the "Force Update" option. '
                        )
                        % {"version": version, "build": build_number or None}
                    )
                else:
                    # 如果是强制更新，删除旧记录和文件
                    old_file_path = existing_record.app_file_path
                    if old_file_path and os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                            _logger.info(_("The old version of the file has been deleted:%s") % old_file_path)
                        except Exception as e:
                            _logger.error(_("Failed to delete an old version of the file:%s") % str(e))
                    existing_record.unlink()
                    _logger.info(
                        _("The old version record has been deleted, version: %s, build number: %s")
                        % (version, build_number or None)
                    )

            # 生成目标文件路径
            file_name = os.path.basename(temp_file_path)
            target_dir = self._get_platform_dir(platform, version)
            os.makedirs(target_dir, exist_ok=True)
            target_file_path = os.path.join(target_dir, file_name)

            # 移动文件到目标目录
            shutil.move(temp_file_path, target_file_path)
            _logger.info(_("The file has been moved to: %s") % target_file_path)

            # 创建记录
            vals = {
                "name": app_info.get("product_name") or file_name,
                "platform": platform,
                "version": version,
                "build_number": build_number,
                "app_file_path": target_file_path,
            }

            # 更新文件大小
            record = self.create(vals)
            record._update_file_size()

            _logger.info(_("An app record has been created:%s") % vals)
            return record.id

        except Exception as e:
            # 确保清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            raise

    @api.model
    def check_version_exists(self, filename):
        """检查文件版本是否存在
        Args:
            filename: 文件名
        Returns:
            dict: 包含版本信息的字典，如果不存在则返回 None
        """
        try:
            # 检测平台
            platform = self._detect_platform(filename)
            if not platform:
                return None

            # 保存到临时文件以读取版本信息
            temp_dir = self._get_temp_dir()
            temp_file_path = os.path.join(temp_dir, filename)

            # 由于此时文件还未上传，我们只检查数据库中是否存在相同平台的相同版本
            domain = [
                ("platform", "=", platform),
                ("app_filename", "=", filename),
            ]

            existing_record = self.search(domain, limit=1)
            if existing_record:
                    return {
                    "version": existing_record.version,
                    "platform_type": existing_record.platform,
                    "build_number": existing_record.build_number,
                }
            return None

        except Exception as e:
            _logger.error(_("Error checking if version exists: %s"), str(e))
            return None

    # endregion
