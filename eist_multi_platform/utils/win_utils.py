# -*- coding: utf-8 -*-

import os
import re
import logging
import pefile
from odoo import _

_logger = logging.getLogger(__name__)


def normalize_version(version_str):
    """标准化版本号格式
    Args:
        version_str: 原始版本号字符串
    Returns:
        str: 标准化后的版本号
    """
    if not version_str:
        return None

    try:
        # 移除所有非数字和点的字符
        version = re.sub(r"[^\d.]", "", version_str)

        # 分割版本号
        parts = version.split(".")

        # 过滤掉空字符串
        parts = [p for p in parts if p]

        # 确保至少有一个数字
        if not parts:
            return None

        # 确保每个部分都是有效的数字
        parts = [str(int(p)) for p in parts]

        # 确保至少有三个部分 (x.y.z)
        while len(parts) < 3:
            parts.append("0")

        # 只保留前四个部分 (x.y.z.w)
        parts = parts[:4]

        return ".".join(parts)
    except:
        return None


def extract_version_from_filename(filename):
    """从文件名中提取版本号"""
    # 常见的版本号模式
    patterns = [
        r"[\-_](\d+\.\d+\.\d+(\.\d+)?)",  # 匹配 -1.2.3 或 _1.2.3.4
        r"[vV](\d+\.\d+\.\d+(\.\d+)?)",  # 匹配 v1.2.3 或 V1.2.3.4
        r"(\d+\.\d+\.\d+(\.\d+)?)",  # 匹配 1.2.3 或 1.2.3.4
        r"[\-_](\d+\.\d+)",  # 匹配 -1.2 或 _1.2
        r"[vV](\d+\.\d+)",  # 匹配 v1.2 或 V1.2
        r"(\d+\.\d+)",  # 匹配 1.2
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            version = normalize_version(match.group(1))
            if version:
                return version
    return None


def extract_build_number(version_str):
    """从版本字符串中提取构建号"""
    if not version_str:
        return None

    # 尝试从四段式版本号中提取最后一段作为构建号
    parts = version_str.split(".")
    if len(parts) >= 4:
        return parts[3]

    # 尝试从文件版本字符串中提取构建号
    build_match = re.search(r"[bB]uild[:\s]*(\d+)", version_str)
    if build_match:
        return build_match.group(1)

    return None


def get_version_from_pe_resource(pe):
    """从PE资源中获取版本信息"""
    try:
        version_info = {}

        # 获取VS_FIXEDFILEINFO信息
        if hasattr(pe, "VS_FIXEDFILEINFO"):
            version_info["file_version"] = "%d.%d.%d.%d" % (
                pe.VS_FIXEDFILEINFO[0].FileVersionMS >> 16,
                pe.VS_FIXEDFILEINFO[0].FileVersionMS & 0xFFFF,
                pe.VS_FIXEDFILEINFO[0].FileVersionLS >> 16,
                pe.VS_FIXEDFILEINFO[0].FileVersionLS & 0xFFFF,
            )
            version_info["product_version"] = "%d.%d.%d.%d" % (
                pe.VS_FIXEDFILEINFO[0].ProductVersionMS >> 16,
                pe.VS_FIXEDFILEINFO[0].ProductVersionMS & 0xFFFF,
                pe.VS_FIXEDFILEINFO[0].ProductVersionLS >> 16,
                pe.VS_FIXEDFILEINFO[0].ProductVersionLS & 0xFFFF,
            )

        # 获取字符串表信息
        if hasattr(pe, "FileInfo"):
            for file_info in pe.FileInfo:
                if hasattr(file_info, "StringTable"):
                    for string_table in file_info.StringTable:
                        for entry in string_table.entries.items():
                            key = entry[0].decode("utf-8", errors="ignore").lower()
                            value = entry[1].decode("utf-8", errors="ignore")
                            version_info[key] = value

        return version_info
    except Exception as e:
        _logger.warning(_("Failed to read version info from PE resource: %s") % str(e))
        return {}


def wait_for_file_ready(file_path, timeout=30, min_size=1024 * 1024):
    """
    等待文件上传完成并可访问
    Args:
        file_path: 文件路径
        timeout: 超时时间（秒）
        min_size: 最小文件大小（字节）
    Returns:
        bool: 文件是否准备就绪
    """
    import time

    start_time = time.time()
    last_size = 0
    stable_count = 0

    while time.time() - start_time < timeout:
        try:
            if not os.path.exists(file_path):
                time.sleep(1)
                continue

            current_size = os.path.getsize(file_path)

            # 如果文件大小大于最小值且连续3次大小相同，认为文件已完成
            if current_size >= min_size:
                if current_size == last_size:
                    stable_count += 1
                    if stable_count >= 3:
                        return True
                else:
                    stable_count = 0

            last_size = current_size
            time.sleep(1)

        except Exception as e:
            _logger.warning(_("Error while checking file: %s - %s") % (file_path, str(e)))
            time.sleep(1)

    return False


def is_pe_file(file_path):
    """
    检查文件是否为有效的PE文件
    Args:
        file_path: 文件路径
    Returns:
        bool: 是否为PE文件
    """
    try:
        # 规范化文件路径
        file_path = os.path.normpath(file_path)

        # 等待文件就绪
        if not wait_for_file_ready(file_path):
            _logger.warning(_("File is not ready or too small: %s") % file_path)
            return False

        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size < 64:  # PE文件至少需要64字节
            _logger.warning(
                _("File is too small to be a PE file: %s (size: %d bytes)") % (file_path, file_size)
            )
            return False

        # 以二进制方式打开文件
        with open(file_path, "rb", buffering=0) as f:
            # 读取DOS头的魔数
            dos_header = f.read(2)
            if dos_header != b"MZ":
                _logger.warning(_("Invalid DOS header magic number in file: %s") % file_path)
                return False

            # 读取PE签名偏移量
            f.seek(0x3C)
            pe_offset_bytes = f.read(4)
            if len(pe_offset_bytes) != 4:
                _logger.warning(_("Failed to read PE offset in file: %s") % file_path)
                return False

            pe_offset = int.from_bytes(pe_offset_bytes, byteorder="little")
            if pe_offset < 0 or pe_offset >= file_size:
                _logger.warning(
                    _("Invalid PE offset in file: %s (offset: %d, size: %d)")
                    % (file_path, pe_offset, file_size)
                )
                return False

            # 检查PE签名
            f.seek(pe_offset)
            pe_signature = f.read(4)
            if pe_signature != b"PE\x00\x00":
                _logger.warning(_("Invalid PE signature in file: %s") % file_path)
                return False

            return True

    except IOError as e:
        _logger.warning(_("IO Error while checking PE file: %s - %s") % (file_path, str(e)))
        return False
    except Exception as e:
        _logger.warning(_("Failed to check PE file: %s - %s") % (file_path, str(e)))
        return False


def get_exe_info(file_path):
    """
    获取Windows EXE文件的版本信息
    Args:
        file_path: EXE文件路径
    Returns:
        dict: 包含版本信息的字典
    """
    # 规范化文件路径
    file_path = os.path.normpath(file_path)

    if not os.path.exists(file_path):
        raise Exception(_("File does not exist: %s") % file_path)

    if not os.path.isfile(file_path):
        raise Exception(_("Path is not a file: %s") % file_path)

    info = {
        "version": None,
        "product_version": None,
        "build_number": None,
        "original_filename": os.path.basename(file_path),
    }

    try:
        # 直接使用pefile读取版本信息
        _logger.info(_("Attempting to read version info from PE file: %s") % file_path)
        pe = pefile.PE(file_path, fast_load=True)
        try:
            # 解析资源目录
            pe.parse_data_directories([pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
            version_info = get_version_from_pe_resource(pe)

            # 从PE资源中提取版本号
            if version_info:
                # 优先使用FileVersion
                if "file_version" in version_info:
                    version = normalize_version(version_info["file_version"])
                    if version:
                        info["version"] = version
                        _logger.info(_("Successfully read version from PE FileVersion: %s") % version)

                # 如果没有FileVersion，尝试其他字段
                if not info["version"] and "fileversion" in version_info:
                    version = normalize_version(version_info["fileversion"])
                    if version:
                        info["version"] = version
                        _logger.info(
                            _("Successfully read version from PE StringTable FileVersion: %s") % version
                        )

                # 获取ProductVersion
                if "product_version" in version_info:
                    product_version = normalize_version(version_info["product_version"])
                    if product_version:
                        info["product_version"] = product_version

                # 获取其他信息
                if "originalfilename" in version_info:
                    info["original_filename"] = version_info["originalfilename"]
                if "productname" in version_info:
                    info["product_name"] = version_info["productname"]
                if "internalname" in version_info:
                    info["internal_name"] = version_info["internalname"]

        finally:
            pe.close()

        # 如果从PE资源中无法获取版本号，尝试从文件名中提取
        if not info.get("version"):
            _logger.info(_("Attempting to extract version from filename"))
            version = extract_version_from_filename(os.path.basename(file_path))
            if version:
                info["version"] = version
                _logger.info(_("Successfully extracted version from filename: %s") % version)
            else:
                raise Exception(
                    _("Unable to extract valid version information from both PE resources and filename")
                )

        # 提取构建号
        if not info.get("build_number"):
            version_str = info.get("version")
            if version_str:
                build_number = extract_build_number(version_str)
                if build_number:
                    info["build_number"] = build_number

        return info

    except pefile.PEFormatError as e:
        _logger.warning(_("Invalid PE format: %s, trying to extract version from filename") % str(e))
        # 当PE文件解析失败时，尝试从文件名获取版本号
        version = extract_version_from_filename(os.path.basename(file_path))
        if version:
            info["version"] = version
            _logger.info(
                _("Successfully extracted version from filename after PE parse failure: %s") % version
            )
            return info
        else:
            raise Exception(_("Failed to read version information from both PE file and filename"))
    except Exception as e:
        error_msg = str(e)
        _logger.error(_("Failed to read EXE file version information: %s") % error_msg)
        raise Exception(_("Failed to read version information: %s") % error_msg)
