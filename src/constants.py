"""常量定义模块 - 存放项目中使用的所有常量.

避免魔法数字和硬编码字符串，提高代码可维护性.
"""

from enum import Enum, auto


class StatusCode(Enum):
    """状态码枚举."""
    
    SUCCESS = 0
    ERROR = -1
    PARAM_ERROR = -2
    NOT_FOUND = -3
    PERMISSION_DENIED = -4
    DB_ERROR = -5
    EXTERNAL_ERROR = -6
    DUPLICATE = -7
    CONFIG_ERROR = -8


class PushStatus(Enum):
    """推送状态枚举."""
    
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class LogLevel(Enum):
    """日志级别枚举."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MonitorStatus(Enum):
    """监控状态枚举."""
    
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    ERROR = "error"


# 项目信息
PROJECT_NAME: str = "Push_Stock"
PROJECT_VERSION: str = "1.0.0"
PROJECT_DESCRIPTION: str = "股票信号推送监控系统"

# 文件监控配置
DEFAULT_MONITOR_BASE_PATH: str = "C:/Users/ckyto/Desktop"
DEFAULT_MONITOR_FILES: list[str] = ["回调买.txt"]
FILE_ENCODING: str = "utf-8"
FILE_CHECK_INTERVAL: float = 10.0  # 秒，兜底轮询间隔

# 推送配置
DEFAULT_RETRY_COUNT: int = 3
DEFAULT_RETRY_INTERVALS: list[int] = [5, 30, 120]  # 秒
DEFAULT_DUPLICATE_WINDOW: int = 3600  # 秒，1小时
DEFAULT_BATCH_INTERVAL: int = 30  # 秒
DEFAULT_DAILY_PUSH_LIMIT: int = 1000

# 日志配置
DEFAULT_LOG_LEVEL: str = "INFO"
DEFAULT_LOG_MAX_SIZE: str = "500 MB"
DEFAULT_LOG_RETENTION_DAYS: int = 10
DEFAULT_LOG_BACKUP_COUNT: int = 5

# API配置
DEFAULT_API_HOST: str = "127.0.0.1"
DEFAULT_API_PORT: int = 8000

# 数据库配置
DEFAULT_DB_PATH: str = "./data/push_stock.db"

# 企业微信配置
DEFAULT_BOT_NAME: str = "StockBot"
WECHAT_WEBHOOK_PREFIX: str = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send"

# 性能配置
MAX_MEMORY_MB: int = 500  # 最大内存占用
MAX_CPU_PERCENT: float = 80.0  # 最大CPU使用率
MONITOR_CHECK_INTERVAL: int = 60  # 进程监控检查间隔(秒)

# 正则表达式模式
STOCK_CODE_PATTERN: str = r"^\d{6}$"  # 6位数字股票代码
PRICE_PATTERN: str = r"^\d+\.?\d{0,2}$"  # 价格格式
DATE_TIME_PATTERN: str = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
CHANGE_PERCENT_PATTERN: str = r"^[+-]?\d+\.?\d{0,2}%$"  # 涨跌幅格式

# 文件解析配置
FILE_FIELD_SEPARATOR: str = "\t"  # 制表符分隔
FILE_EXPECTED_FIELDS: int = 7  # 期望字段数
FILE_FIELD_NAMES: list[str] = [
    "stock_code",
    "stock_name",
    "trigger_time",
    "price",
    "change_percent",
    "volume",
    "indicator"
]

# 时区配置
DEFAULT_TIMEZONE: str = "Asia/Shanghai"

# 分页配置
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

# 图表配置
CHART_COLORS: list[str] = [
    "#0066cc",  # 主蓝色
    "#00c851",  # 成功绿
    "#ff9800",  # 警告橙
    "#ff4444",  # 错误红
    "#9c27b0",  # 紫色
    "#00bcd4",  # 青色
    "#ff5722",  # 深橙
    "#795548",  # 棕色
]

# HTTP状态码
HTTP_OK: int = 200
HTTP_BAD_REQUEST: int = 400
HTTP_UNAUTHORIZED: int = 401
HTTP_FORBIDDEN: int = 403
HTTP_NOT_FOUND: int = 404
HTTP_INTERNAL_ERROR: int = 500
HTTP_SERVICE_UNAVAILABLE: int = 503

# 企业微信API错误码
WECHAT_SUCCESS: int = 0
WECHAT_INVALID_KEY: int = 40001
WECHAT_INVALID_TOKEN: int = 40014
WECHAT_RATE_LIMIT: int = 45009
WECHAT_MSG_SIZE_LIMIT: int = 40004
