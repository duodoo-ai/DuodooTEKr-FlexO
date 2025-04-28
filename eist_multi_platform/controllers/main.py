# -*- coding: utf-8 -*-

import os
import logging
from odoo import http, _
from odoo.http import request, Response
import werkzeug
import json
import base64
import tempfile
from odoo.exceptions import UserError


from odoo.addons.eist_multi_platform import utils as mp_utils  # type: ignore

_logger = logging.getLogger(__name__)


class MultiPlatformController(http.Controller):

    def _get_temp_dir(self):
        """获取临时目录路径"""
        base_dir = mp_utils.APP_FILE_TEMP_PATH
        temp_dir = os.path.join(base_dir, "temps")
        # temp_dir = os.path.join(tempfile.gettempdir(), "odoo_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def _get_upload_dir(self):
        """
        获取最终文件存储目录
        """
        base_dir = mp_utils.APP_FILE_TEMP_PATH
        upload_dir = os.path.join(base_dir, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    

    @http.route("/multi_platform/upload_chunk", type="json", auth="user")
    def upload_chunk(self, filename, chunk_data, chunk_index, total_chunks):
        try:
            # 确保临时目录存在
            temp_dir = os.path.join("eist_multi_platform", "static", "app_files", "temp")
            os.makedirs(temp_dir, exist_ok=True)

            # 生成临时文件路径
            temp_file_path = os.path.join(temp_dir, f"{filename}.part")

            # 解码并写入分片数据
            chunk_binary = base64.b64decode(chunk_data.split(",")[1] if "," in chunk_data else chunk_data)
            mode = "ab" if chunk_index > 0 else "wb"
            with open(temp_file_path, mode) as f:
                f.write(chunk_binary)

            return {"success": True, "message": f"分片 {chunk_index + 1}/{total_chunks} 上传成功"}

        except Exception as e:
            _logger.error(f"上传分片失败: {str(e)}")
            return {"success": False, "error": f"上传分片失败: {str(e)}"}

    @http.route("/multi_platform/complete_upload", type="json", auth="user")
    def complete_upload(self, filename, force_update=False):
        try:
            # 获取临时文件路径
            temp_dir = os.path.join("eist_multi_platform", "static", "app_files", "temp")
            temp_file_path = os.path.join(temp_dir, f"{filename}.part")

            if not os.path.exists(temp_file_path):
                return {"success": False, "error": "找不到上传的文件"}

            # 重命名临时文件，移除.part后缀
            final_temp_path = os.path.join(temp_dir, filename)
            os.rename(temp_file_path, final_temp_path)

            try:
                # 创建应用记录
                record_id = request.env["res.multi.platform.apps"].create_from_upload(
                    final_temp_path, force_update=force_update
                )

                return {"success": True, "message": "上传成功", "record_id": record_id}

            except UserError as e:
                if "已存在" in str(e):
                    # 如果是版本已存在的错误，返回特殊的错误类型
                    return {"success": False, "error_type": "version_exists", "error": str(e)}
                raise

        except Exception as e:
            _logger.error(f"完成上传失败: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                if os.path.exists(final_temp_path):
                    os.remove(final_temp_path)
            except:
                pass
