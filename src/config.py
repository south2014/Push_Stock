"""配置管理模块 - 使用Pydantic进行类型安全的配置管理.

提供三层配置加载策略:
1. 环境变量 (优先级最高)
2. SQLite数据库配置 (Web界面可修改)
3. 默认值 (首次启动引导)
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """数据库配置."""
    
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        extra="ignore"
    )
    
    path: Path = Field(
        default=Path("./data/push_stock.db"),
        description="SQLite数据库文件路径"
    )
    
    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        """确保数据库目录存在."""
        v.parent.mkdir(parents=True, exist_ok=True)
        return v


class WeChatConfig(BaseSettings):
    """企业微信配置."""
    
    model_config = SettingsConfigDict(
        env_prefix="WECHAT_",
        extra="ignore"
    )
    
    webhook_url: str = Field(
        default="",
        description="企业微信Webhook URL"
    )
    owner_user_id: Optional[str] = Field(
        default=None,
        description="群主企业微信ID"
    )
    bot_name: str = Field(
        default="StockBot",
        description="机器人名称"
    )


class MonitorConfig(BaseSettings):
    """文件监控配置."""
    
    model_config = SettingsConfigDict(
        env_prefix="MONITOR_",
        extra="ignore"
    )
    
    base_path: Path = Field(
        default=Path("C:/Users/ckyto/Desktop"),
        description="监控文件基础路径"
    )
    files: str = Field(
        default="回调买.txt",
        description="监控文件名列表(逗号分隔)"
    )
    
    def get_file_list(self) -> List[str]:
        """获取监控文件列表."""
        return [f.strip() for f in self.files.split(",") if f.strip()]


class PushStrategyConfig(BaseSettings):
    """推送策略配置."""
    
    model_config = SettingsConfigDict(
        env_prefix="PUSH_",
        extra="ignore"
    )
    
    retry_count: int = Field(
        default=3,
        ge=0,
        le=10,
        description="失败重试次数"
    )
    retry_intervals: str = Field(
        default="5,30,120",
        description="重试间隔(秒,逗号分隔)"
    )
    duplicate_window: int = Field(
        default=3600,
        ge=0,
        description="去重时间窗口(秒)"
    )
    batch_enabled: bool = Field(
        default=False,
        description="是否启用批量推送"
    )
    batch_interval: int = Field(
        default=30,
        ge=1,
        description="批量推送间隔(秒)"
    )
    
    def get_retry_intervals(self) -> List[int]:
        """获取重试间隔列表."""
        try:
            return [int(x.strip()) for x in self.retry_intervals.split(",")]
        except ValueError:
            return [5, 30, 120]


class LogConfig(BaseSettings):
    """日志配置."""
    
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        extra="ignore"
    )
    
    level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="日志级别"
    )
    dir: Path = Field(
        default=Path("./logs"),
        description="日志目录"
    )
    max_size: str = Field(
        default="10MB",
        description="单个日志文件最大大小"
    )
    backup_count: int = Field(
        default=5,
        ge=1,
        le=30,
        description="保留日志文件数量"
    )
    
    @field_validator("dir")
    @classmethod
    def validate_dir(cls, v: Path) -> Path:
        """确保日志目录存在."""
        v.mkdir(parents=True, exist_ok=True)
        return v


class APIConfig(BaseSettings):
    """API服务配置."""
    
    model_config = SettingsConfigDict(
        env_prefix="API_",
        extra="ignore"
    )
    
    host: str = Field(
        default="127.0.0.1",
        description="API服务主机"
    )
    port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="API服务端口"
    )
    reload: bool = Field(
        default=False,
        description="开发模式热重载"
    )


class Config(BaseSettings):
    """全局配置 - 整合所有子配置."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # 子配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    wechat: WeChatConfig = Field(default_factory=WeChatConfig)
    monitor: MonitorConfig = Field(default_factory=MonitorConfig)
    push_strategy: PushStrategyConfig = Field(default_factory=PushStrategyConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    
    # 全局设置
    debug: bool = Field(
        default=False,
        description="调试模式"
    )
    
    @field_validator("debug", mode="before")
    @classmethod
    def validate_debug(cls, v):
        """从环境变量读取DEBUG设置."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例 (单例模式).
    
    Returns:
        Config: 全局配置对象
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """重新加载配置.
    
    Returns:
        Config: 新的配置对象
    """
    global _config
    _config = Config()
    return _config
