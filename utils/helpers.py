# 各种通用工具函数
import os
import re

def contains_only_english(text):
        """
        检查字符串是否只包含英文字母、数字和符号，不包含其他语言字符
        Args:
            text (str): 待检查的字符串
        Returns:
            bool: 如果字符串仅包含英文字母、数字和符号，则返回 True，否则返回 False
        """
        return bool(re.fullmatch(r'[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~ ]+', text))



def save_json_to_file(data, file_path):
    """
    将数据保存到指定路径的 JSON 文件中。如果数据是字符串，尝试将其解析为字典。
    Args:
        data (str or dict): 要保存的数据，可以是字符串或字典
        file_path (str): 保存文件的路径
    """
    import json
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 如果数据是字符串，尝试将其解析为字典
    if isinstance(data, str):
        try:
            # 尝试将字符串解析为 JSON
            data = json.loads(data)
        except json.JSONDecodeError:
            # 如果解析失败，保留原始字符串
            pass

    # 确保数据是字典
    if isinstance(data, dict):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        raise ValueError("输入数据必须是字符串或字典")


