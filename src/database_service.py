"""数据库服务层 - 封装所有数据库CRUD操作.

提供高层业务接口，隐藏底层SQLAlchemy细节.
"""

from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Generator, List, Optional, Tuple

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from src.logger import get_logger
from src.models import (
    MonitorFile,
    PushRecord,
    PushStrategy,
    WeChatConfig,
    get_db_manager,
    get_db_session,
)

logger = get_logger(__name__)


class DatabaseService:
    """数据库服务类 - 所有数据操作的统一入口.
    
    使用上下文管理器管理会话生命周期.
    """
    
    def __init__(self) -> None:
        """初始化数据库服务."""
        self.db_manager = get_db_manager()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """会话上下文管理器.
        
        Yields:
            Session: 数据库会话对象
        """
        session = self.db_manager.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    # ========== PushRecord CRUD ==========
    
    def create_push_record(
        self,
        stock_code: str,
        stock_name: str,
        price: Decimal,
        trigger_time: str,
        file_path: str,
        raw_content: str,
        **kwargs
    ) -> PushRecord:
        """创建推送记录.
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            price: 价格
            trigger_time: 触发时间
            file_path: 文件路径
            raw_content: 原始内容
            **kwargs: 其他字段
            
        Returns:
            创建的PushRecord对象
        """
        with self.session_scope() as session:
            record = PushRecord(
                stock_code=stock_code,
                stock_name=stock_name,
                price=price,
                trigger_time=trigger_time,
                file_path=file_path,
                raw_content=raw_content,
                **kwargs
            )
            session.add(record)
            session.flush()
            session.refresh(record)
            logger.info(f"创建推送记录: {record.stock_code} {record.stock_name}")
            return record
    
    def get_push_record(self, record_id: int) -> Optional[PushRecord]:
        """获取单条推送记录.
        
        Args:
            record_id: 记录ID
            
        Returns:
            PushRecord对象或None
        """
        with self.session_scope() as session:
            return session.query(PushRecord).filter_by(id=record_id).first()
    
    def get_recent_pushes(
        self,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[PushRecord]:
        """获取最近推送记录.
        
        Args:
            limit: 返回数量限制
            status: 状态筛选
            
        Returns:
            PushRecord列表
        """
        with self.session_scope() as session:
            query = session.query(PushRecord).order_by(
                desc(PushRecord.created_at)
            )
            
            if status:
                query = query.filter_by(status=status)
            
            return query.limit(limit).all()
    
    def is_duplicate_signal(
        self,
        stock_code: str,
        price: Decimal,
        indicator: str,
        window_seconds: int = 3600
    ) -> bool:
        """检查是否为重复信号.
        
        Args:
            stock_code: 股票代码
            price: 价格
            indicator: 策略标识
            window_seconds: 去重窗口(秒)
            
        Returns:
            True如果是重复信号
        """
        with self.session_scope() as session:
            cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
            
            count = session.query(PushRecord).filter(
                and_(
                    PushRecord.stock_code == stock_code,
                    PushRecord.price == price,
                    PushRecord.indicator == indicator,
                    PushRecord.trigger_time >= cutoff_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            ).count()
            
            return count > 0
    
    def update_push_status(
        self,
        record_id: int,
        status: str,
        error_message: Optional[str] = None,
        webhook_response: Optional[str] = None
    ) -> bool:
        """更新推送状态.
        
        Args:
            record_id: 记录ID
            status: 新状态
            error_message: 错误信息
            webhook_response: Webhook响应
            
        Returns:
            是否更新成功
        """
        with self.session_scope() as session:
            record = session.query(PushRecord).filter_by(id=record_id).first()
            if not record:
                return False
            
            record.status = status
            if error_message:
                record.error_message = error_message
            if webhook_response:
                record.webhook_response = webhook_response
            
            if status == "failed":
                record.retry_count += 1
            
            logger.info(f"更新推送状态: {record_id} -> {status}")
            return True
    
    def get_daily_stats(self, date: Optional[datetime] = None) -> dict:
        """获取日统计信息.
        
        Args:
            date: 统计日期，默认为今天
            
        Returns:
            统计信息字典
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        
        with self.session_scope() as session:
            result = session.query(
                func.count(PushRecord.id).label("total"),
                func.sum(
                    func.case([(PushRecord.status == "success", 1)], else_=0)
                ).label("success"),
                func.sum(
                    func.case([(PushRecord.status == "failed", 1)], else_=0)
                ).label("failed")
            ).filter(
                func.date(PushRecord.created_at) == date_str
            ).first()
            
            total = result.total or 0
            success = result.success or 0
            failed = result.failed or 0
            
            success_rate = (success / total * 100) if total > 0 else 0
            
            return {
                "date": date_str,
                "total": total,
                "success": success,
                "failed": failed,
                "success_rate": round(success_rate, 2)
            }
    
    # ========== MonitorFile CRUD ==========
    
    def create_monitor_file(
        self,
        file_path: str,
        enabled: bool = True,
        description: Optional[str] = None
    ) -> MonitorFile:
        """创建监控文件配置.
        
        Args:
            file_path: 文件路径
            enabled: 是否启用
            description: 描述
            
        Returns:
            MonitorFile对象
        """
        with self.session_scope() as session:
            monitor_file = MonitorFile(
                file_path=file_path,
                enabled=enabled,
                description=description
            )
            session.add(monitor_file)
            session.flush()
            session.refresh(monitor_file)
            logger.info(f"创建监控文件: {file_path}")
            return monitor_file
    
    def get_all_monitor_files(self, enabled_only: bool = False) -> List[MonitorFile]:
        """获取所有监控文件配置.
        
        Args:
            enabled_only: 仅返回启用的
            
        Returns:
            MonitorFile列表
        """
        with self.session_scope() as session:
            query = session.query(MonitorFile)
            if enabled_only:
                query = query.filter_by(enabled=True)
            return query.all()
    
    def update_file_position(
        self,
        file_id: int,
        position: int
    ) -> bool:
        """更新文件读取位置.
        
        Args:
            file_id: 文件配置ID
            position: 新位置
            
        Returns:
            是否更新成功
        """
        with self.session_scope() as session:
            monitor_file = session.query(MonitorFile).filter_by(
                id=file_id
            ).first()
            
            if not monitor_file:
                return False
            
            monitor_file.update_position(position)
            logger.debug(f"更新文件位置: {file_id} -> {position}")
            return True
    
    # ========== Config CRUD ==========
    
    def get_wechat_config(self) -> Optional[WeChatConfig]:
        """获取企业微信配置.
        
        Returns:
            WeChatConfig对象或None
        """
        with self.session_scope() as session:
            return session.query(WeChatConfig).filter_by(id=1).first()
    
    def save_wechat_config(
        self,
        webhook_url: str,
        owner_user_id: Optional[str] = None,
        bot_name: str = "StockBot",
        enabled: bool = True
    ) -> WeChatConfig:
        """保存企业微信配置.
        
        Args:
            webhook_url: Webhook URL
            owner_user_id: 群主ID
            bot_name: 机器人名称
            enabled: 是否启用
            
        Returns:
            WeChatConfig对象
        """
        with self.session_scope() as session:
            config = session.query(WeChatConfig).filter_by(id=1).first()
            
            if config:
                config.webhook_url = webhook_url
                config.owner_user_id = owner_user_id
                config.bot_name = bot_name
                config.enabled = enabled
            else:
                config = WeChatConfig(
                    webhook_url=webhook_url,
                    owner_user_id=owner_user_id,
                    bot_name=bot_name,
                    enabled=enabled
                )
                session.add(config)
            
            session.flush()
            session.refresh(config)
            logger.info("更新企业微信配置")
            return config
    
    def get_push_strategy(self) -> PushStrategy:
        """获取推送策略配置.
        
        Returns:
            PushStrategy对象
        """
        with self.session_scope() as session:
            strategy = session.query(PushStrategy).filter_by(id=1).first()
            
            if not strategy:
                strategy = PushStrategy()  # 使用默认值
                session.add(strategy)
                session.commit()
                session.refresh(strategy)
            
            return strategy


# 便捷函数
def get_database_service() -> DatabaseService:
    """获取数据库服务实例.
    
    Returns:
        DatabaseService实例
    """
    return DatabaseService()
