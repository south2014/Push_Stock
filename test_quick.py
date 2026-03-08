"""快速验证脚本 - 不依赖pytest，直接验证核心功能.

运行: python test_quick.py
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_parser():
    """测试解析器."""
    print("\n=== 测试股票解析器 ===")
    
    try:
        from src.core.parser import StockSignalParser
        
        parser = StockSignalParser()
        
        # 测试1: 正常解析
        line = "600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G"
        signal = parser.parse_line(line)
        
        if signal is None:
            print("❌ 解析失败: 返回None")
            return False
        
        if signal.stock_code != "600176":
            print(f"❌ 股票代码错误: {signal.stock_code}")
            return False
        
        if signal.stock_name != "中国巨石":
            print(f"❌ 股票名称错误: {signal.stock_name}")
            return False
        
        print(f"✅ 解析成功: {signal.stock_code} {signal.stock_name} ¥{signal.price}")
        
        # 测试2: 多行解析
        content = """600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G
300861\t美畅股份\t2026-03-02 13:19\t18.78\t-1.26%\t15\tBBIHTM_G"""
        
        signals = parser.parse_lines(content)
        
        if len(signals) != 2:
            print(f"❌ 多行解析错误: 期望2条，实际{len(signals)}条")
            return False
        
        print(f"✅ 多行解析成功: {len(signals)}条信号")
        return True
        
    except Exception as e:
        print(f"❌ 解析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exceptions():
    """测试异常体系."""
    print("\n=== 测试异常体系 ===")
    
    try:
        from src.exceptions import ParserException, PushException
        
        # 测试ParserException
        try:
            raise ParserException("测试错误", code=ParserException.INVALID_FORMAT)
        except ParserException as e:
            print(f"✅ ParserException工作正常: {e.code}")
        
        # 测试PushException
        try:
            raise PushException("网络错误", code=PushException.NETWORK_ERROR)
        except PushException as e:
            print(f"✅ PushException工作正常: {e.code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 异常测试失败: {e}")
        return False


def test_constants():
    """测试常量."""
    print("\n=== 测试常量定义 ===")
    
    try:
        from src.constants import PROJECT_NAME, DEFAULT_RETRY_COUNT, STOCK_CODE_PATTERN
        
        if PROJECT_NAME != "Push_Stock":
            print(f"❌ 项目名称错误: {PROJECT_NAME}")
            return False
        
        if DEFAULT_RETRY_COUNT != 3:
            print(f"❌ 重试次数错误: {DEFAULT_RETRY_COUNT}")
            return False
        
        print(f"✅ 常量定义正确: {PROJECT_NAME}, 重试{DEFAULT_RETRY_COUNT}次")
        return True
        
    except Exception as e:
        print(f"❌ 常量测试失败: {e}")
        return False


def main():
    """主函数."""
    print("=" * 50)
    print("Push_Stock 快速验证测试")
    print("=" * 50)
    
    results = []
    
    results.append(("解析器", test_parser()))
    results.append(("异常体系", test_exceptions()))
    results.append(("常量定义", test_constants()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！代码基本可用。")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 项测试失败，需要修复。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
