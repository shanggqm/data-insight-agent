import json
import os
import hashlib
from datetime import datetime

import requests


# ===== 缓存功能 =====
# 缓存目录（相对于项目根目录）
CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache"
)


def _ensure_cache_dir():
    """确保缓存目录存在"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def _generate_cache_key(tool_name: str, params: dict) -> str:
    """生成缓存键的哈希值"""
    param_str = json.dumps(params, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(param_str.encode()).hexdigest()[:8]


def save_to_cache(tool_name: str, params: dict, result: str) -> str:
    """
    保存查询结果到缓存
    命名规范: {tool_name}_{timestamp}_{hash}.json
    返回缓存文件路径
    """
    _ensure_cache_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_key = _generate_cache_key(tool_name, params)
    filename = f"{tool_name}_{timestamp}_{cache_key}.json"
    filepath = os.path.join(CACHE_DIR, filename)

    cache_data = {
        "tool_name": tool_name,
        "params": params,
        "result": result,
        "cached_at": datetime.now().isoformat(),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)

    return filepath


#### LINDORM AI EMBEDDING ####
def _post_model_request(
    host: str, username: str, password: str, model: str, data: dict, **kwargs
):
    data = json.dumps(data)
    url = "http://{}:{}/v1/ai/models/{}/infer".format(host, 9002, model)
    headers = {
        "Content-Type": "application/json",
        "x-ld-ak": username,
        "x-ld-sk": password,
    }
    connect_timeout = kwargs.get("connect_timeout", 60)
    read_timeout = kwargs.get("read_timeout", 60)
    timeout = (connect_timeout, read_timeout)

    try:
        result = requests.post(
            url, data=data, headers=headers, verify=False, timeout=timeout
        )
        result.raise_for_status()
        return 0, result.json()["data"]
    except requests.exceptions.Timeout as time_out_err:
        return -1, f"request out of time: f{time_out_err}"
    except requests.exceptions.HTTPError as http_err:
        return -1, f"HTTP error: {http_err}"
    except requests.exceptions.RequestException as err:
        return -1, f"request error happened: {err}"


def text_embedding(host: str, username: str, password: str, model: str, text: str):
    data = {"input": [text]}
    return _post_model_request(host, username, password, model, data)


def get_lindorm_search_host(instance_id: str, using_vpc: bool = False):
    """
    Get search host by instance id
    :param instance_id: Lindorm instance ID
    :param using_vpc: Boolean flag indicating whether to use VPC endpoint
    :return: Formatted search host URL
    """
    base_url = "lindorm.aliyuncs.com"
    if using_vpc:
        endpoint = "proxy-search-vpc"
    else:
        endpoint = "proxy-search-pub"
    return f"{instance_id}-{endpoint}.{base_url}"


def get_lindorm_ai_host(instance_id: str, using_vpc: bool = False):
    base_url = "lindorm.aliyuncs.com"
    if using_vpc:
        endpoint = "proxy-ai-vpc"
    else:
        endpoint = "proxy-ai-pub"
    return f"{instance_id}-{endpoint}.{base_url}"


def get_lindorm_table_host(instance_id: str, using_vpc: bool = False):
    base_url = "lindorm.aliyuncs.com"
    if using_vpc:
        endpoint = "proxy-lindorm-vpc"
    else:
        endpoint = "proxy-lindorm-pub"
    return f"{instance_id}-{endpoint}.{base_url}"


def str_to_bool(value):
    return value.lower() in ("true", "1", "yes", "on", "t")


def simplify_mappings(mappings, index_name):
    if not mappings or index_name not in mappings:
        return None

    properties = mappings[index_name]["mappings"].get("properties", {})
    simplified = {}

    for field, details in properties.items():
        if "type" in details:
            simplified[field] = details["type"]
        elif "properties" in details:
            simplified[field] = "object"
        else:
            simplified[field] = "unknown"

    return simplified
