"""推送记录模型 - 存储所有股票信号推送记录.

对应数据库表: push_records
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)

from src.models.base import BaseModel


class PushRecord(BaseModel):
    """推送记录数据模型.
    
    Attributes:
        id: 主键ID
        stock_code: 股票代码 (6位数字)
        stock_name: 股票名称
        price: 触发价格
        change_percent: 涨跌幅 (%)
        volume: 成交量 (手)
        indicator: 指标标识
        trigger_time: 触发时间
        file_path: 监控文件路径
        raw_content: 原始文件行内容
        status: 推送状态
        error_message: 错误信息
        retry_count: 已重试次数
        webhook_response: Webhook响应
        wechat_message_id: 微信消息ID
    """
    
    __tablename__ = "push_records"
    
    # 股票信息
    stock_code = Column(
        String(6),
        nullable=False,
        index=True,
        comment="股票代码"
    )
    stock_name = Column(
        String(20),
        nullable=False,
        comment="股票名称"
    )
    
    # 价格信息
    price = Column(
        Numeric(10, 2),
        nullable=False,
        comment="触发价格"
    )
    change_percent = Column(
        Numeric(8, 2),
        nullable=True,
        comment="涨跌幅(%)"
    )
    volume = Column(
        Integer,
        nullable=True,
        comment="成交量(手)"
    )
    
    # 指标信息
    indicator = Column(
        String(20),
        nullable=True,
        comment="指标标识"
    )
    
    # 时间信息
    trigger_time = Column(
        String(19),  # YYYY-MM-DD HH:MM:SS
        nullable=False,
        index=True,
        comment="触发时间"
    )
    
    # 文件信息
    file_path = Column(
        Text,
        nullable=False,
        comment="监控文件路径"
    )
    raw_content = Column(
        Text,
        nullable=False,
        comment="原始文件行内容"
    )
    
    # 推送状态
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="推送状态"
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="错误信息"
    )
    retry_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="已重试次数"
    )
    
    # 响应信息
    webhook_response = Column(
        Text,
        nullable=True,
        comment="Webhook响应JSON"
    )
    wechat_message_id = Column(
        String(100),
        nullable=True,
        comment="微信消息ID"
    )
    
    # 唯一约束: 同股票同价格同时间不能重复
    __table_args__ = (
        UniqueConstraint(
            "stock_code",
            "price",
            "trigger_time",
            name="unique_signal"
        ),
        Index("idx_trigger_time", text("trigger_time DESC")),
        Index("idx_stock_code", "stock_code"),
        Index("idx_status", "status"),
        Index("idx_created_at", text("created_at DESC")),
    )
    
    def __init__(
        self,
        stock_code: str,
        stock_name: str,
        price: Decimal,
        trigger_time: str,
        file_path: str,
        raw_content: str,
        change_percent: Optional[Decimal] = None,
        volume: Optional[int] = None,
        indicator: Optional[str] = None,
        status: str = "pending",
        error_message: Optional[str] = None,
        retry_count: int = 0,
    ) -> None:
        """初始化推送记录.
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            price: 触发价格
            trigger_time: 触发时间 (YYYY-MM-DD HH:MM:SS)
            file_path: 监控文件路径
            raw_content: 原始文件行内容
            change_percent: 涨跌幅
            volume: 成交量
            indicator: 指标标识
            status: 推送状态
            error_message: 错误信息
            retry_count: 重试次数
        """
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.price = price
        self.trigger_time = trigger_time
        self.file_path = file_path
        self.raw_content = raw_content
        self.change_percent = change_percent
        self.volume = volume
        self.indicator = indicator
        self.status = status
        self.error_message = error_message
        self.retry_count = retry_count
