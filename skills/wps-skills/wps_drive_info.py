#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取 WPS 盘详细信息

参考文档: docs/云盘/获取盘信息.md
"""
import logging
import requests
import json
import sys
from pathlib import Path

# 导入配置和工具函数
from wps_login import WPS_CONFIG, load_token, is_token_expired
from wps_api import build_kso1_headers

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API 基础 URL
API_BASE_URL = "https://openapi.wps.cn"


def get_drive_info(access_token, drive_id, with_ext_attrs=False):
    """
    获取盘信息

    Args:
        access_token: 访问令牌
        drive_id: 盘ID
        with_ext_attrs: 是否获取盘扩展属性

    Returns:
        dict: 包含盘信息的响应数据
    """
    method = "GET"
    uri = f"/v7/drives/{drive_id}/meta"

    # 构建查询参数
    params = {}
    if with_ext_attrs:
        params["with_ext_attrs"] = "true"

    # 使用统一的 API 工具构建请求头
    headers = build_kso1_headers(
        client_secret=WPS_CONFIG["client_secret"],
        client_id=WPS_CONFIG["client_id"],
        access_token=access_token,
        method=method,
        uri=uri,
        params=params
    )

    # 构建完整 URL
    url = API_BASE_URL + uri

    logging.info(f"Request URL: {url}")
    logging.info(f"Query params: {params}")

    response = requests.get(url, headers=headers, params=params)

    logging.info(f"Response status: {response.status_code}")

    result = response.json()

    if response.status_code != 200:
        raise Exception(f"Failed (HTTP {response.status_code}): {result}")
    if "code" in result and result["code"] != 0:
        raise Exception(f"Failed: {result.get('msg', 'Unknown error')}")
    if "error" in result:
        raise Exception(f"Failed: {result.get('error_description', result['error'])}")

    return result


def get_drive_by_source(drives, source="special"):
    """
    根据来源获取盘ID

    Args:
        drives: 盘列表
        source: 盘来源，默认为 "special"

    Returns:
        str: 匹配的盘ID，如果没有找到返回 None
    """
    for drive in drives:
        if drive.get("source") == source:
            return drive.get("id")
    return None


def format_drive_info_detail(data):
    """格式化盘详细信息"""
    quota = data.get("quota", {})
    used_mb = quota.get("used", 0) / (1024 * 1024)
    total_mb = quota.get("total", 0) / (1024 * 1024)
    remaining_mb = quota.get("remaining", 0) / (1024 * 1024)
    deleted_mb = quota.get("deleted", 0) / (1024 * 1024)

    created_by = data.get("created_by", {})
    created_by_info = f"{created_by.get('name', 'N/A')} ({created_by.get('id', 'N/A')})"

    info = f"""
盘基本信息:
  盘名称: {data.get('name', 'N/A')}
  盘ID: {data.get('id', 'N/A')}
  类型: {data.get('allotee_type', 'N/A')}
  归属ID: {data.get('allotee_id', 'N/A')}
  公司ID: {data.get('company_id', 'N/A')}
  来源: {data.get('source', 'N/A')}
  状态: {data.get('status', 'N/A')}
  描述: {data.get('description', 'N/A')}
  创建者: {created_by_info}
  创建时间: {data.get('ctime', 'N/A')}
  修改时间: {data.get('mtime', 'N/A')}

配额信息:
  已用: {used_mb:.2f} MB
  总容量: {total_mb:.2f} MB
  剩余: {remaining_mb:.2f} MB
  已删除: {deleted_mb:.2f} MB"""

    # 扩展属性
    ext_attrs = data.get("ext_attrs", [])
    if ext_attrs:
        info += "\n\n扩展属性:"
        for attr in ext_attrs:
            info += f"\n  {attr.get('name', 'N/A')}: {attr.get('value', 'N/A')}"

    return info


def save_drive_info_to_file(data, filename="drive_info.json"):
    """保存盘信息到文件"""
    output_path = Path(__file__).parent / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"盘信息已保存到: {output_path}")


def main():
    """主函数"""
    # 加载 token
    token_data = load_token()
    if not token_data:
        print("错误: 未找到有效的 token 文件，请先运行 wps_login.py 进行授权")
        return 1

    # 检查 token 是否过期
    if is_token_expired(token_data, "access"):
        print("错误: Access token 已过期，请运行 wps_login.py 刷新 token")
        return 1

    access_token = token_data["token"]["access_token"]
    print(f"使用 access_token: {access_token[:20]}...")

    # 解析命令行参数
    drive_id = None
    source = "special"
    with_ext_attrs = False
    output_file = None

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--help" or arg == "-h":
            print("获取 WPS 盘详细信息")
            print("")
            print("用法: python wps_drive_info.py [选项]")
            print("")
            print("选项:")
            print("  --drive-id ID       指定盘ID")
            print("  --source SOURCE     根据来源查找盘ID，默认: special")
            print("  --ext-attrs         获取盘扩展属性")
            print("  --output FILE       保存结果到文件")
            print("  --help, -h          显示帮助信息")
            print("")
            print("示例:")
            print("  python wps_drive_info.py --drive-id W88Mvvq")
            print("  python wps_drive_info.py --source special")
            return 0
        elif arg == "--drive-id" and i + 1 < len(sys.argv):
            drive_id = sys.argv[i + 1]
            i += 1
        elif arg == "--source" and i + 1 < len(sys.argv):
            source = sys.argv[i + 1]
            i += 1
        elif arg == "--ext-attrs":
            with_ext_attrs = True
        elif arg == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 1
        i += 1

    # 如果没有指定盘ID，尝试从drives_list.json读取
    if not drive_id:
        drives_file = Path(__file__).parent / "drives_list.json"
        if drives_file.exists():
            with open(drives_file, "r", encoding="utf-8") as f:
                drives = json.load(f)
            drive_id = get_drive_by_source(drives, source)
            if drive_id:
                print(f"从drives_list.json找到source='{source}'的盘ID: {drive_id}")
            else:
                print(f"错误: 在drives_list.json中未找到source='{source}'的盘")
                print(f"可用的盘来源: {set(d.get('source') for d in drives)}")
                return 1
        else:
            print(f"错误: 未找到drives_list.json文件，请先运行wps_drives.py获取盘列表")
            return 1

    print(f"\n获取盘信息...")
    print(f"  盘ID: {drive_id}")
    if with_ext_attrs:
        print(f"  获取扩展属性: 是")

    try:
        # 获取盘信息
        result = get_drive_info(
            access_token=access_token,
            drive_id=drive_id,
            with_ext_attrs=with_ext_attrs
        )

        drive_data = result.get("data", {})

        # 打印详细信息
        print("\n" + "="*60)
        print("盘详细信息")
        print("="*60)
        print(format_drive_info_detail(drive_data))

        # 保存到文件
        if output_file:
            save_drive_info_to_file(drive_data, output_file)
        else:
            save_drive_info_to_file(drive_data)

        return 0

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
