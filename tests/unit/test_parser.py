"""股票信号解析器单元测试.

测试StockSignalParser的各种解析场景.
"""

import pytest
from decimal import Decimal

from src.core.parser import StockSignalParser, StockSignal
from src.exceptions import ParserException


class TestStockSignalParser:
    """StockSignalParser测试类."""
    
    def setup_method(self):
        """每个测试方法前执行."""
        self.parser = StockSignalParser()
    
    def test_parse_valid_line(self):
        """测试解析有效的股票信号行."""
        line = "600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G"
        
        signal = self.parser.parse_line(line)
        
        assert signal is not None
        assert signal.stock_code == "600176"
        assert signal.stock_name == "中国巨石"
        assert signal.trigger_time == "2026-03-02 11:21:00"
        assert signal.price == Decimal("28.10")
        assert signal.change_percent == " 3.92%"
        assert signal.volume == 69
        assert signal.indicator == "BBIHTM_G"
    
    def test_parse_line_with_negative_change(self):
        """测试解析负涨跌幅."""
        line = "300861\t美畅股份\t2026-03-02 13:19\t18.78\t-1.26%\t15\tBBIHTM_G"
        
        signal = self.parser.parse_line(line)
        
        assert signal is not None
        assert signal.change_percent == "-1.26%"
    
    def test_parse_empty_line(self):
        """测试解析空行."""
        signal = self.parser.parse_line("")
        assert signal is None
        
        signal = self.parser.parse_line("   ")
        assert signal is None
    
    def test_parse_invalid_stock_code(self):
        """测试解析无效的股票代码."""
        line = "invalid\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G"
        
        with pytest.raises(ParserException) as exc_info:
            self.parser.parse_line(line)
        
        assert exc_info.value.code == ParserException.INVALID_STOCK_CODE
    
    def test_parse_short_stock_code(self):
        """测试解析位数不足的股票代码."""
        line = "60017\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G"
        
        with pytest.raises(ParserException) as exc_info:
            self.parser.parse_line(line)
        
        assert exc_info.value.code == ParserException.INVALID_STOCK_CODE
    
    def test_parse_invalid_price(self):
        """测试解析无效的价格."""
        line = "600176\t中国巨石\t2026-03-02 11:21\tabc\t 3.92%\t69\tBBIHTM_G"
        
        with pytest.raises(ParserException) as exc_info:
            self.parser.parse_line(line)
        
        assert exc_info.value.code == ParserException.INVALID_PRICE
    
    def test_parse_insufficient_fields(self):
        """测试解析字段不足的行."""
        line = "600176\t中国巨石\t2026-03-02 11:21"
        
        with pytest.raises(ParserException) as exc_info:
            self.parser.parse_line(line)
        
        assert exc_info.value.code == ParserException.INVALID_FORMAT
    
    def test_parse_lines_multiple(self):
        """测试解析多行内容."""
        content = """600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G
300861\t美畅股份\t2026-03-02 13:19\t18.78\t-1.26%\t15\tBBIHTM_G
002734\t利民股份\t2026-03-03 10:26\t21.03\t-2.55%\t261\tBBIHTM_G"""
        
        signals = self.parser.parse_lines(content)
        
        assert len(signals) == 3
        assert signals[0].stock_code == "600176"
        assert signals[1].stock_code == "300861"
        assert signals[2].stock_code == "002734"
    
    def test_parse_lines_with_invalid_line(self):
        """测试解析包含无效行的内容."""
        content = """600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G
invalid line
300861\t美畅股份\t2026-03-02 13:19\t18.78\t-1.26%\t15\tBBIHTM_G"""
        
        signals = self.parser.parse_lines(content)
        
        assert len(signals) == 2
        assert signals[0].stock_code == "600176"
        assert signals[1].stock_code == "300861"
    
    def test_parse_optional_fields_empty(self):
        """测试解析可选字段为空的情况."""
        line = "600176\t中国巨石\t2026-03-02 11:21\t28.10\t\t\t"
        
        signal = self.parser.parse_line(line)
        
        assert signal is not None
        assert signal.change_percent is None
        assert signal.volume is None
        assert signal.indicator is None
    
    def test_get_stats(self):
        """测试获取解析统计."""
        # 先解析一些数据
        self.parser.parse_line("600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G")
        
        stats = self.parser.get_stats()
        
        assert stats == (1, 0)  # 1成功, 0失败
    
    def test_reset_stats(self):
        """测试重置统计."""
        # 先解析一些数据
        self.parser.parse_line("600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G")
        
        # 重置
        self.parser.reset_stats()
        stats = self.parser.get_stats()
        
        assert stats == (0, 0)  # 重置后为0
