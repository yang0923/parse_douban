# log_configurator.py

import os
import sys
from loguru import logger


def setup(log_file_path: str = "logs/app.log", logging_enabled: bool = True,save_logs: bool = True):

    # 移除默认的处理器
    logger.remove()
    if save_logs:
        # 创建日志目录
        log_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        # 添加文件处理器
        logger.add(
            log_file_path, # 日志文件路径
            rotation="10 MB",  # 文件大小达到 10 MB 后轮换
            retention="5 days",  # 保留 5 天的日志文件
            compression="zip",  # 使用 zip 压缩日志文件
            level="INFO",  # 文件记录 INFO 级别及以上的日志
            enqueue=True  # 支持多进程
        )

    if logging_enabled:
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            level="DEBUG"  # 控制台显示 DEBUG 级别及以上的日志
        )

