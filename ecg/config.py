import os
import yaml


def load_config(path: str = "../config.yml"):
    """读取YAML格式的配置文件。"""
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}
