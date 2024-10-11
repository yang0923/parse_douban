from config import log_config  # 导入日志配置文件
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# 日志配置
SAVE_LOGS = False  # 控制是否保存日志 到文件 Fasle:不保存 True:保存
LOGGING_ENABLED = True  # 控制日志是否启用 , Fasle:不启用 True:启用
LOG_FILE_PATH = BASE_DIR / 'logs' / 'app.log'  # 设置日志文件路径
# 启动日志配置
log_config.setup(log_file_path=str(LOG_FILE_PATH), logging_enabled=LOGGING_ENABLED,save_logs=SAVE_LOGS)