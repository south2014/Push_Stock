"""系统配置模型 - 存储企业微信和推送策略配置.

对应数据库表: wechat_config, push_strategy
"""

from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Integer,
    String,
    Text,
)

from src.models.base import BaseModel


class WeChatConfig(BaseModel):
    """企业微信配置模型.
    
    全局单条记录，id固定为1.
    
    Attributes:
        id: 固定为1
        webhook_url: Webhook完整URL
        owner_user_id: 群主企业微信ID
        bot_name: 机器人名称
        enabled: 是否启用
    """
    
    __tablename__ = "wechat_config"
    
    # 固定ID=1，确保只有一条记录
    id = Column(
        Integer,
        primary_key=True,
        default=1
    )
    
    webhook_url = Column(
        Text,
        nullable=False,
        comment="Webhook完整URL"
    )
    owner_user_id = Column(
        String(50),
        nullable=True,
        comment="群主企业微信ID"
    )
    bot_name = Column(
        String(50),
        nullable=False,
        default="StockBot",
        comment="机器人名称"
    )
    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否启用"
    )
    
    # 约束: id必须为1
    __table_args__ = (
        CheckConstraint("id = 1", name="check_single_config"),
    )
    
    def __init__(
        self,
        webhook_url: str,
        owner_user_id: Optional[str] = None,
        bot_name: str = "StockBot",
        enabled: bool = True,
    ) -> None:
        """初始化企业微信配置.
        
        Args:
            webhook_url: Webhook URL
            owner_user_id: 群主ID
            bot_name: 机器人名称
            enabled: 是否启用
        """
        self.id = 1
        self.webhook_url = webhook_url
        self.owner_user_id = owner_user_id
        self.bot_name = bot_name
        self.enabled = enabled
    
    def is_configured(self) -> bool:
        """检查是否已配置.
        
        Returns:
            True如果webhook_url不为空
        """
        return bool(self.webhook_url and self.webhook_url.strip())


class PushStrategy(BaseModel):
    """推送策略配置模型.
    
    全局单条记录，id固定为1.
    
    Attributes:
        id: 固定为1
        retry_count: 失败重试次数
        retry_intervals: 重试间隔(秒)JSON数组
        duplicate_window_seconds: 去重时间窗口(秒)
        batch_enabled: 是否启用批量推送
        batch_interval_seconds: 批量推送间隔(秒)
        daily_push_limit: 每日推送上限
    """
    
    __tablename__ = "push_strategy"
    
    # 固定ID=1
    id = Column(
        Integer,
        primary_key=True,
        default=1
    )
    
    retry_count = Column(
        Integer,
        nullable=False,
        default=3,
        comment="失败重试次数"
    )
    retry_intervals = Column(
        Text,
        nullable=False,
        default="[5,30,120]",
        comment="重试间隔(秒)JSON数组"
    )
    duplicate_window_seconds = Column(
        Integer,
        nullable=False,
        default=3600,
        comment="去重时间窗口(秒)"
    )
    batch_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否启用批量推送"
    )
    batch_interval_seconds = Column(
        Integer,
        nullable=False,
        default=30,
        comment="批量推送间隔(秒)"
    )
    daily_push_limit = Column(
        Integer,
        nullable=False,
        default=1000,
        comment="每日推送上限"
    )
    
    # 约束: id必须为1
    __table_args__ = (
        CheckConstraint("id = 1", name="check_single_strategy"),
    )
    
    def __init__(
        self,
        retry_count: int = 3,
        retry_intervals: str = "[5,30,120]",
        duplicate_window_seconds: int = 3600,
        batch_enabled: bool = False,
        batch_interval_seconds: int = 30,
        daily_push_limit: int = 1000,
    ) -> None:
        """初始化推送策略.
        
        Args:
            retry_count: 重试次数
            retry_intervals: 重试间隔JSON
            duplicate_window_seconds: 去重窗口
            batch_enabled: 批量推送
            batch_interval_seconds: 批量间隔
            daily_push_limit: 日推送上限
        """
        self.id = 1
        self.retry_count = retry_count
        self.retry_intervals = retry_intervals
        self.duplicate_window_seconds = duplicate_window_seconds
        self.batch_enabled = batch_enabled
        self.batch_interval_seconds = batch_interval_seconds
        self.daily_push_limit = daily_push_limit
    
    def get_retry_intervals_list(self) -> list[int]:
        """获取重试间隔列表.
        
        Returns:
            重试间隔列表
        """
        import json
        try:
            return json.loads(self.retry_intervals)
        except json.JSONDecodeError:
            return [5, 30, 120]
