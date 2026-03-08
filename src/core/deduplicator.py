"""去重服务 - 防止重复推送相同的股票信号.

基于时间窗口的去重策略:
- 在指定时间窗口内（默认1小时）
- 相同的股票代码 + 相同的价格 + 相同的策略
- 视为重复信号，不进行推送

支持两种存储后端:
- SQLite (默认): 适合单实例，持久化存储
- Redis (可选): 高性能，适合分布式
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from src.database_service import get_database_service
from src.logger import get_logger

logger = get_logger(__name__)


class Deduplicator:
    """信号去重器.
    
    检测并过滤重复的股票信号.
    """
    
    def __init__(self, window_seconds: int = 3600) -> None:
        """初始化去重器.
        
        Args:
            window_seconds: 去重时间窗口（秒），默认1小时
        """
        self.window_seconds = window_seconds
        self.db_service = get_database_service()
        self.duplicate_count = 0
    
    def is_duplicate(
        self,
        stock_code: str,
        price: Decimal,
        indicator: str
    ) -> bool:
        """检查信号是否为重复.
        
        Args:
            stock_code: 股票代码
            price: 触发价格
            indicator: 策略标识
            
        Returns:
            True如果是重复信号
        """
        try:
            is_dup = self.db_service.is_duplicate_signal(
                stock_code=stock_code,
                price=price,
                indicator=indicator,
                window_seconds=self.window_seconds
            )
            
            if is_dup:
                self.duplicate_count += 1
                logger.debug(
                    f"检测到重复信号: {stock_code} 价格{price} "
                    f"策略{indicator}"
                )
            
            return is_dup
            
        except Exception as e:
            logger.error(f"去重检查失败: {e}")
            # 出错时允许通过（避免阻塞正常流程）
            return False
    
    def filter_signals(
        self,
        signals: list
    ) -> tuple[list, list]:
        """批量过滤信号.
        
        Args:
            signals: 信号列表 (StockSignal对象)
            
        Returns:
            (新信号列表, 重复信号列表)
        """
        new_signals = []
        duplicate_signals = []
        
        for signal in signals:
            if self.is_duplicate(
                signal.stock_code,
                signal.price,
                signal.indicator or "UNKNOWN"
            ):
                duplicate_signals.append(signal)
            else:
                new_signals.append(signal)
        
        if duplicate_signals:
            logger.info(
                f"去重过滤: {len(new_signals)}条新信号，"
                f"{len(duplicate_signals)}条重复"
            )
        
        return new_signals, duplicate_signals
    
    def get_stats(self) -> dict:
        """获取去重统计.
        
        Returns:
            统计信息字典
        """
        return {
            "duplicate_count": self.duplicate_count,
            "window_seconds": self.window_seconds
        }
    
    def reset_stats(self) -> None:
        """重置统计."""
        self.duplicate_count = 0


# 便捷函数
def get_deduplicator(window_seconds: Optional[int] = None) -> Deduplicator:
    """获取去重器实例.
    
    Args:
        window_seconds: 去重窗口（秒）
        
    Returns:
        Deduplicator实例
    """
    if window_seconds is None:
        # 从配置获取默认值
        from src.config import get_config
        window_seconds = get_config().push_strategy.duplicate_window
    
    return Deduplicator(window_seconds)
