"""自定义异常模块 - 定义项目中使用的所有业务异常.

异常层级结构:
PushStockException (基类)
├── ConfigException (配置相关)
├── MonitorException (监控相关)
├── ParserException (解析相关)
├── PushException (推送相关)
└── DatabaseException (数据库相关)
"""

from typing import Any, Dict, Optional


class PushStockException(Exception):
    """项目基础异常类.
    
    所有自定义异常的基类，提供统一的错误处理接口.
    
    Attributes:
        code: 错误码
        message: 错误消息
        details: 详细错误信息
    """
    
    def __init__(
        self,
        message: str,
        code: int = -1,
        details: Optional[Dict[str, Any]] = None
    ):
        """初始化异常.
        
        Args:
            message: 错误描述
            code: 错误码，默认为-1
            details: 详细错误信息字典
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def __str__(self) -> str:
        """字符串表示."""
        if self.details:
            return f"[{self.code}] {self.message} - {self.details}"
        return f"[{self.code}] {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 (用于API响应).
        
        Returns:
            包含错误信息的字典
        """
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class ConfigException(PushStockException):
    """配置异常 - 配置加载、验证失败时抛出."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """初始化配置异常.
        
        Args:
            message: 错误描述
            config_key: 出错的配置项名称
            details: 详细信息
        """
        super().__init__(message, code=-100, details=details)
        self.config_key = config_key


class MonitorException(PushStockException):
    """监控异常 - 文件监控相关错误."""
    
    FILE_NOT_FOUND = -200
    FILE_ACCESS_DENIED = -201
    FILE_LOCKED = -202
    WATCHDOG_ERROR = -203
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        code: int = -200,
        details: Optional[Dict[str, Any]] = None
    ):
        """初始化监控异常.
        
        Args:
            message: 错误描述
            file_path: 出错的文件路径
            code: 错误码
            details: 详细信息
        """
        super().__init__(message, code=code, details=details)
        self.file_path = file_path


class ParserException(PushStockException):
    """解析异常 - 股票信号解析失败时抛出."""
    
    INVALID_FORMAT = -300
    INVALID_STOCK_CODE = -301
    INVALID_PRICE = -302
    INVALID_DATE = -303
    
    def __init__(
        self,
        message: str,
        raw_content: Optional[str] = None,
        code: int = -300,
        details: Optional[Dict[str, Any]] = None
    ):
        """初始化解析异常.
        
        Args:
            message: 错误描述
            raw_content: 原始解析内容
            code: 错误码
            details: 详细信息
        """
        super().__init__(message, code=code, details=details)
        self.raw_content = raw_content


class PushException(PushStockException):
    """推送异常 - 企业微信推送失败时抛出."""
    
    WEBHOOK_INVALID = -400
    WEBHOOK_RATE_LIMIT = -401
    NETWORK_ERROR = -402
    TIMEOUT_ERROR = -403
    MAX_RETRY_EXCEEDED = -404
    
    def __init__(
        self,
        message: str,
        webhook_url: Optional[str] = None,
        retry_count: int = 0,
        code: int = -400,
        details: Optional[Dict[str, Any]] = None
    ):
        """初始化推送异常.
        
        Args:
            message: 错误描述
            webhook_url: Webhook URL
            retry_count: 已重试次数
            code: 错误码
            details: 详细信息
        """
        super().__init__(message, code=code, details=details)
        self.webhook_url = webhook_url
        self.retry_count = retry_count


class DatabaseException(PushStockException):
    """数据库异常 - 数据库操作失败时抛出."""
    
    CONNECTION_ERROR = -500
    QUERY_ERROR = -501
    INSERT_ERROR = -502
    UPDATE_ERROR = -503
    DELETE_ERROR = -504
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        sql: Optional[str] = None,
        code: int = -500,
        details: Optional[Dict[str, Any]] = None
    ):
        """初始化数据库异常.
        
        Args:
            message: 错误描述
            operation: 数据库操作类型
            sql: SQL语句
            code: 错误码
            details: 详细信息
        """
        super().__init__(message, code=code, details=details)
        self.operation = operation
        self.sql = sql


class WeChatAPIException(PushException):
    """企业微信API异常 - 微信API返回错误."""
    
    def __init__(
        self,
        message: str,
        errcode: int = 0,
        errmsg: str = "",
        webhook_url: Optional[str] = None
    ):
        """初始化微信API异常.
        
        Args:
            message: 错误描述
            errcode: 微信错误码
            errmsg: 微信错误信息
            webhook_url: Webhook URL
        """
        super().__init__(message, webhook_url=webhook_url, code=-410)
        self.errcode = errcode
        self.errmsg = errmsg


class DuplicateSignalException(PushStockException):
    """重复信号异常 - 检测到重复股票信号时抛出."""
    
    def __init__(
        self,
        stock_code: str,
        price: float,
        trigger_time: str,
        window_seconds: int = 3600
    ):
        """初始化重复信号异常.
        
        Args:
            stock_code: 股票代码
            price: 价格
            trigger_time: 触发时间
            window_seconds: 去重窗口(秒)
        """
        message = (
            f"重复信号: {stock_code} 价格 {price} 在 {window_seconds}秒 "
            f"窗口内已推送"
        )
        super().__init__(message, code=-600)
        self.stock_code = stock_code
        self.price = price
        self.trigger_time = trigger_time
        self.window_seconds = window_seconds


# 便捷函数
def raise_config_error(message: str, key: Optional[str] = None) -> None:
    """抛出配置异常."""
    raise ConfigException(message, config_key=key)


def raise_monitor_error(
    message: str,
    file_path: Optional[str] = None,
    code: int = MonitorException.FILE_NOT_FOUND
) -> None:
    """抛出监控异常."""
    raise MonitorException(message, file_path=file_path, code=code)


def raise_push_error(
    message: str,
    webhook_url: Optional[str] = None,
    code: int = PushException.NETWORK_ERROR
) -> None:
    """抛出推送异常."""
    raise PushException(message, webhook_url=webhook_url, code=code)
