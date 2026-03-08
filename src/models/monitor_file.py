"""监控文件模型 - 配置需要监控的文件路径.

对应数据库表: monitor_files
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Index,
    Integer,
    Text,
)

from src.models.base import BaseModel


class MonitorFile(BaseModel):
    """监控文件配置模型.
    
    Attributes:
        id: 主键ID
        file_path: 监控文件完整路径
        enabled: 是否启用
        description: 配置描述
        last_position: 上次读取位置(字节)
        last_processed_time: 最后处理时间
    """
    
    __tablename__ = "monitor_files"
    
    # 文件路径 (唯一)
    file_path = Column(
        Text,
        nullable=False,
        unique=True,
        comment="监控文件完整路径"
    )
    
    # 启用状态
    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否启用"
    )
    
    # 描述信息
    description = Column(
        Text,
        nullable=True,
        comment="配置描述"
    )
    
    # 读取位置追踪
    last_position = Column(
        Integer,
        nullable=False,
        default=0,
        comment="上次读取位置(字节)"
    )
    last_processed_time = Column(
        Text,  # YYYY-MM-DD HH:MM:SS
        nullable=True,
        comment="最后处理时间"
    )
    
    # 索引和约束
    __table_args__ = (
        Index("idx_file_path", "file_path"),
        Index("idx_enabled", "enabled"),
    )
    
    def __init__(
        self,
        file_path: str,
        enabled: bool = True,
        description: Optional[str] = None,
        last_position: int = 0,
        last_processed_time: Optional[str] = None,
    ) -> None:
        """初始化监控文件配置.
        
        Args:
            file_path: 监控文件完整路径
            enabled: 是否启用
            description: 配置描述
            last_position: 上次读取位置
            last_processed_time: 最后处理时间
        """
        self.file_path = file_path
        self.enabled = enabled
        self.description = description
        self.last_position = last_position
        self.last_processed_time = last_processed_time
    
    def update_position(self, position: int) -> None:
        """更新文件读取位置.
        
        Args:
            position: 新的读取位置
        """
        from datetime import datetime
        self.last_position = position
        self.last_processed_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
