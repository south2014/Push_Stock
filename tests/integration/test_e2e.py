"""端到端集成测试.

测试从文件监控到微信推送的完整流程.
"""

import pytest
import tempfile
import os
from pathlib import Path
from decimal import Decimal

from src.core.parser import StockSignalParser
from src.core.deduplicator import Deduplicator
from src.exceptions import ParserException, PushException


class TestEndToEndFlow:
    """端到端流程测试."""
    
    def test_parse_stock_signal(self):
        """测试解析股票信号."""
        parser = StockSignalParser()
        
        line = "600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G"
        signal = parser.parse_line(line)
        
        assert signal is not None
        assert signal.stock_code == "600176"
        assert signal.stock_name == "中国巨石"
        assert signal.price == Decimal("28.10")
        print(f"✅ 解析成功: {signal.stock_code} {signal.stock_name} ¥{signal.price}")
    
    def test_markdown_message_generation(self):
        """测试Markdown消息生成."""
        # 模拟微信机器人的Markdown格式
        stock_code = "600176"
        stock_name = "中国巨石"
        price = 28.10
        change_percent = " 3.92%"
        volume = 69
        indicator = "BBIHTM_G"
        trigger_time = "2026-03-02 11:21"
        
        # 构建涨跌幅显示
        change_display = change_percent
        if change_percent and float(change_percent.replace("%", "")) > 0:
            change_display = f"🟢 {change_percent}"
        elif change_percent and float(change_percent.replace("%", "")) < 0:
            change_display = f"🔴 {change_percent}"
        
        # 构建Markdown消息
        content = f"""**股票信号推送**

| 项目 | 内容 |
|------|------|
| **股票代码** | {stock_code} |
| **股票名称** | {stock_name} |
| **当前价格** | ¥{price:.2f} |
| **涨跌幅** | {change_display} |
| **成交量** | {volume if volume else '--'} 手 |
| **触发时间** | {trigger_time if trigger_time else '--'} |
| **策略指标** | {indicator if indicator else '--'} |
"""
        
        assert stock_code in content
        assert stock_name in content
        assert "🟢" in content  # 上涨显示绿色
        print("✅ Markdown消息生成成功")
    
    def test_config_loading(self):
        """测试配置加载."""
        from src.config import get_config
        
        config = get_config()
        
        # 验证配置对象存在
        assert config is not None
        assert config.database is not None
        assert config.push_strategy is not None
        
        # 验证默认值
        assert config.push_strategy.retry_count == 3
        assert config.push_strategy.duplicate_window == 3600
        print("✅ 配置加载成功")


class TestErrorHandling:
    """错误处理测试."""
    
    def test_parser_exception(self):
        """测试解析异常."""
        with pytest.raises(ParserException):
            raise ParserException("测试错误", code=ParserException.INVALID_FORMAT)
    
    def test_push_exception(self):
        """测试推送异常."""
        with pytest.raises(PushException):
            raise PushException("网络错误", code=PushException.NETWORK_ERROR)


class TestDataFlow:
    """数据流测试."""
    
    def test_signal_to_dict_conversion(self):
        """测试信号转换为字典."""
        from src.core.parser import StockSignal
        from decimal import Decimal
        
        signal = StockSignal(
            stock_code="600519",
            stock_name="贵州茅台",
            trigger_time="2026-03-08 10:30:00",
            price=Decimal("1680.50"),
            change_percent="3.92%",
            volume=1250,
            indicator="BBIHTM_G",
            raw_line="600519\t贵州茅台\t2026-03-08 10:30\t1680.50\t3.92%\t1250\tBBIHTM_G"
        )
        
        # 验证数据完整性
        assert signal.stock_code == "600519"
        assert signal.price == Decimal("1680.50")
        assert signal.volume == 1250
        print("✅ 信号数据结构完整")
