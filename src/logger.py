"""日志模块 - 使用Loguru实现结构化异步日志.

提供统一的日志接口，支持:
- 控制台输出 (开发环境)
- 文件存储 (生产环境)
- 自动轮转和压缩
- 异步写入不阻塞主线程
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from src.config import get_config


def setup_logger() -> None:
    """配置全局日志系统.
    
    根据配置初始化日志处理器，包括:
    - 控制台输出 (INFO级别以上)
    - 应用日志文件 (INFO级别，自动轮转)
    - 错误日志文件 (ERROR级别，长期保留)
    """
    config = get_config()
    log_config = config.log
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    _add_console_handler(log_config.level)
    
    # 添加文件处理器
    _add_file_handlers(log_config)
    
    logger.info("日志系统初始化完成")


def _add_console_handler(level: str) -> None:
    """添加控制台日志处理器.
    
    Args:
        level: 日志级别
    """
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level:8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
        enqueue=True
    )


def _add_file_handlers(log_config) -> None:
    """添加文件日志处理器.
    
    Args:
        log_config: 日志配置对象
    """
    log_dir = log_config.dir
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 应用日志 (INFO级别)
    logger.add(
        log_dir / "app.log",
        rotation=log_config.max_size,
        retention=f"{log_config.backup_count} days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:8} | {name}:{function}:{line} | {message}",
        encoding="utf-8",
        enqueue=True
    )
    
    # 错误日志 (ERROR级别)
    logger.add(
        log_dir / "error.log",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:8} | {name}:{function}:{line} | {message}\n{exception}",
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )


def get_logger(name: Optional[str] = None):
    """获取指定名称的日志记录器.
    
    Args:
        name: 模块名称，默认为调用模块名
        
    Returns:
        logger: 配置好的日志记录器
    """
    if name:
        return logger.bind(name=name)
    return logger


class LogContext:
    """日志上下文管理器 - 用于记录耗时操作."""
    
    def __init__(self, operation: str, level: str = "INFO"):
        """初始化上下文.
        
        Args:
            operation: 操作名称
            level: 日志级别
        """
        self.operation = operation
        self.level = level
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        """进入上下文."""
        import time
        self.start_time = time.time()
        logger.log(self.level, f"开始执行: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文."""
        import time
        duration = time.time() - self.start_time
        
        if exc_type is None:
            logger.log(
                self.level, 
                f"完成执行: {self.operation} (耗时: {duration:.3f}s)"
            )
        else:
            logger.error(
                f"执行失败: {self.operation} (耗时: {duration:.3f}s) - {exc_val}"
            )
        
        return False  # 不吞掉异常


# 便捷函数
def debug(msg: str, *args, **kwargs) -> None:
    """记录DEBUG级别日志."""
    logger.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """记录INFO级别日志."""
    logger.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """记录WARNING级别日志."""
    logger.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """记录ERROR级别日志."""
    logger.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """记录CRITICAL级别日志."""
    logger.critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs) -> None:
    """记录异常信息."""
    logger.exception(msg, *args, **kwargs)
