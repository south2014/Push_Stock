"""核心服务包 - 业务逻辑核心模块.

包含:
- parser: 股票信号解析器
- deduplicator: 去重服务
- wechat_bot: 企业微信推送
- file_monitor: 文件监控器
"""

from src.core.deduplicator import Deduplicator, get_deduplicator
from src.core.file_monitor import FileMonitor, create_monitor
from src.core.parser import StockSignal, StockSignalParser
from src.core.wechat_bot import WeChatBot, send_stock_push

__all__ = [
    # 解析器
    "StockSignal",
    "StockSignalParser",
    # 去重器
    "Deduplicator",
    "get_deduplicator",
    # 微信机器人
    "WeChatBot",
    "send_stock_push",
    # 文件监控
    "FileMonitor",
    "create_monitor",
]
