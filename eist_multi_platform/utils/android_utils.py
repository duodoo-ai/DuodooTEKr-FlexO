# -*- coding: utf-8 -*-

import os
import zipfile
import logging
import struct
import binascii

from odoo import _

_logger = logging.getLogger(__name__)


def get_string_from_xml(data, offset):
    """从二进制XML数据中提取字符串"""
    try:
        # 获取字符串长度
        length = data[offset] & 0xFF
        if length == 0:
            return None, offset + 2

        # 读取字符串数据
        string_data = data[offset + 2 : offset + 2 + length * 2]
        string = string_data.decode("utf-16le")
        return string, offset + 2 + length * 2
    except Exception:
        return None, offset + 2


def parse_binary_xml(data):
    """解析二进制格式的AndroidManifest.xml"""
    try:
        # 查找字符串池
        if len(data) < 8:
            return {}

        # 检查文件魔数
        magic = binascii.hexlify(data[0:4]).decode("ascii")
        if magic != "03000800":
            return {}

        # 获取字符串池偏移量
        string_pool_offset = struct.unpack("<I", data[4:8])[0]
        if string_pool_offset >= len(data):
            return {}

        # 在文件中搜索关键属性
        version_name = None
        version_code = None
        package_name = None

        # 搜索关键字
        keywords = {
            b"versionName": "version_name",
            b"versionCode": "version_code",
            b"package": "package_name",
        }

        for keyword, attr_name in keywords.items():
            pos = data.find(keyword)
            if pos != -1:
                # 找到属性后，尝试读取其值
                value_offset = pos + len(keyword)
                while value_offset < len(data) - 2:
                    if data[value_offset : value_offset + 2] == b"\x00\x00":
                        value_start = value_offset + 2
                        value, _ = get_string_from_xml(data, value_start)
                        if value:
                            if attr_name == "version_name":
                                version_name = value
                            elif attr_name == "version_code":
                                version_code = value
                            elif attr_name == "package_name":
                                package_name = value
                        break
                    value_offset += 1

        return {"version_name": version_name, "version_code": version_code, "package_name": package_name}
    except Exception as e:
        _logger.error(_("Failed to parse AndroidManifest.xml: %s") % str(e))
        return {}


def get_apk_info(file_path):
    """
    获取Android APK文件的版本信息
    Args:
        file_path: APK文件路径
    Returns:
        dict: 包含版本信息的字典
    """
    try:
        with zipfile.ZipFile(file_path, "r") as apk:
            # 读取AndroidManifest.xml
            manifest_data = apk.read("AndroidManifest.xml")

            # 解析二进制AndroidManifest.xml
            info = parse_binary_xml(manifest_data)

            if not info.get("version_name"):
                raise ValueError(_("Failed to read the version information from the APK file"))

            return info

    except Exception as e:
        _logger.error(_("Failed to read the version information from the APK file: %s") % str(e))
        raise ValueError(_("Failed to read the version information from the APK file: %s") % str(e))
