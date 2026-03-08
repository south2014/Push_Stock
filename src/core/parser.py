"""股票信号解析器 - 解析通达信生成的监控文件内容.

输入格式:
600176	中国巨石	2026-03-02 11:21	28.10	 3.92%	69	BBIHTM_G

字段顺序:
1. 股票代码 (6位数字)
2. 股票名称 (中文)
3. 触发时间 (YYYY-MM-DD HH:MM)
4. 当前价格 (Decimal)
5. 涨跌幅 (字符串，带%号)
6. 成交量 (整数，手)
7. 指标标识 (策略名称)
8. 备注 (可选)
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple

from src.constants import STOCK_CODE_PATTERN
from src.exceptions import ParserException
from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class StockSignal:
    """股票信号数据类.
    
    Attributes:
        stock_code: 股票代码
        stock_name: 股票名称
        trigger_time: 触发时间 (YYYY-MM-DD HH:MM)
        price: 当前价格
        change_percent: 涨跌幅 (%)
        volume: 成交量 (手)
        indicator: 指标标识
        raw_line: 原始行内容
    """
    stock_code: str
    stock_name: str
    trigger_time: str
    price: Decimal
    change_percent: Optional[str]
    volume: Optional[int]
    indicator: Optional[str]
    raw_line: str


class StockSignalParser:
    """股票信号解析器.
    
    解析通达信监控文件的每一行，提取股票信号信息.
    """
    
    # 字段分隔符 (制表符)
    FIELD_SEPARATOR = "\t"
    
    # 股票代码正则
    STOCK_CODE_REGEX = re.compile(STOCK_CODE_PATTERN)
    
    # 涨跌幅正则 (匹配 +3.92% 或 -1.26%)
    CHANGE_PERCENT_REGEX = re.compile(r"^[+-]?\d+\.?\d*%$")
    
    def __init__(self) -> None:
        """初始化解析器."""
        self.parsed_count = 0
        self.error_count = 0
    
    def parse_line(self, line: str) -> Optional[StockSignal]:
        """解析单行股票信号.
        
        Args:
            line: 原始文件行内容
            
        Returns:
            StockSignal对象，解析失败返回None
            
        Raises:
            ParserException: 解析格式错误
        """
        # 去除首尾空白
        line = line.strip()
        
        # 空行跳过
        if not line:
            return None
        
        # 按制表符分割
        fields = line.split(self.FIELD_SEPARATOR)
        
        # 检查字段数量 (最少7个，可能有备注)
        if len(fields) < 7:
            self.error_count += 1
            raise ParserException(
                f"字段数量不足: 期望至少7个，实际{len(fields)}个",
                raw_content=line,
                code=ParserException.INVALID_FORMAT
            )
        
        try:
            # 提取字段
            stock_code = self._parse_stock_code(fields[0])
            stock_name = self._parse_stock_name(fields[1])
            trigger_time = self._parse_trigger_time(fields[2])
            price = self._parse_price(fields[3])
            change_percent = self._parse_change_percent(fields[4])
            volume = self._parse_volume(fields[5])
            indicator = self._parse_indicator(fields[6])
            
            self.parsed_count += 1
            
            return StockSignal(
                stock_code=stock_code,
                stock_name=stock_name,
                trigger_time=trigger_time,
                price=price,
                change_percent=change_percent,
                volume=volume,
                indicator=indicator,
                raw_line=line
            )
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"解析行失败: {line[:50]}... - {e}")
            raise ParserException(
                f"解析失败: {str(e)}",
                raw_content=line,
                code=ParserException.INVALID_FORMAT
            )
    
    def parse_lines(self, content: str) -> List[StockSignal]:
        """解析多行内容.
        
        Args:
            content: 多行文本内容
            
        Returns:
            StockSignal列表
        """
        signals = []
        lines = content.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            try:
                signal = self.parse_line(line)
                if signal:
                    signals.append(signal)
            except ParserException as e:
                logger.warning(f"第{line_num}行解析失败: {e.message}")
                continue
            except Exception as e:
                logger.error(f"第{line_num}行未知错误: {e}")
                continue
        
        logger.info(f"解析完成: 成功{self.parsed_count}条，失败{self.error_count}条")
        return signals
    
    def _parse_stock_code(self, field: str) -> str:
        """解析股票代码.
        
        Args:
            field: 股票代码字段
            
        Returns:
            6位数字股票代码
            
        Raises:
            ParserException: 格式错误
        """
        code = field.strip()
        
        if not self.STOCK_CODE_REGEX.match(code):
            raise ParserException(
                f"股票代码格式错误: {code}",
                code=ParserException.INVALID_STOCK_CODE
            )
        
        return code
    
    def _parse_stock_name(self, field: str) -> str:
        """解析股票名称.
        
        Args:
            field: 股票名称字段
            
        Returns:
            股票名称
        """
        return field.strip()
    
    def _parse_trigger_time(self, field: str) -> str:
        """解析触发时间.
        
        Args:
            field: 时间字段 (YYYY-MM-DD HH:MM)
            
        Returns:
            格式化的时间字符串
        """
        time_str = field.strip()
        
        # 通达信格式是 YYYY-MM-DD HH:MM，补充秒为00
        if len(time_str) == 16:  # YYYY-MM-DD HH:MM
            time_str += ":00"
        
        return time_str
    
    def _parse_price(self, field: str) -> Decimal:
        """解析价格.
        
        Args:
            field: 价格字段
            
        Returns:
            Decimal价格
            
        Raises:
            ParserException: 格式错误
        """
        price_str = field.strip()
        
        try:
            return Decimal(price_str)
        except InvalidOperation:
            raise ParserException(
                f"价格格式错误: {price_str}",
                code=ParserException.INVALID_PRICE
            )
    
    def _parse_change_percent(self, field: str) -> Optional[str]:
        """解析涨跌幅.
        
        Args:
            field: 涨跌幅字段 (如: +3.92%)
            
        Returns:
            涨跌幅字符串或None
        """
        percent_str = field.strip()
        
        if not percent_str:
            return None
        
        # 去掉百分号验证
        if percent_str.endswith("%"):
            try:
                float(percent_str[:-1])
                return percent_str
            except ValueError:
                pass
        
        return None
    
    def _parse_volume(self, field: str) -> Optional[int]:
        """解析成交量.
        
        Args:
            field: 成交量字段
            
        Returns:
            成交量整数或None
        """
        volume_str = field.strip()
        
        if not volume_str:
            return None
        
        try:
            return int(volume_str)
        except ValueError:
            return None
    
    def _parse_indicator(self, field: str) -> Optional[str]:
        """解析指标标识.
        
        Args:
            field: 指标字段
            
        Returns:
            指标标识或None
        """
        indicator = field.strip()
        return indicator if indicator else None
    
    def get_stats(self) -> Tuple[int, int]:
        """获取解析统计.
        
        Returns:
            (成功数, 失败数)
        """
        return self.parsed_count, self.error_count
    
    def reset_stats(self) -> None:
        """重置统计计数器."""
        self.parsed_count = 0
        self.error_count = 0
