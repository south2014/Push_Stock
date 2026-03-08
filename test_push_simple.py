"""简化版端到端测试 - 使用回调买.txt测试推送.
"""

import sys
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).parent))

from src.core.parser import StockSignalParser
from src.core.wechat_bot import WeChatBot
from src.config import get_config


async def main():
    """主函数."""
    print("=" * 60)
    print("Push_Stock End-to-End Test")
    print("=" * 60)
    
    # 读取文件
    filepath = r"F:\OpenCode\Push_Stock\回调买.txt"
    
    # 尝试多种编码
    content = None
    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"[OK] File read with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if not content:
        print("[ERROR] Cannot read file")
        return 1
    
    # 解析信号
    parser = StockSignalParser()
    signals = parser.parse_lines(content)
    
    print(f"[OK] Parsed {len(signals)} stock signals")
    
    if not signals:
        print("[ERROR] No valid signals")
        return 1
    
    # 显示前3条
    print("\n[Info] First 3 signals:")
    for i, s in enumerate(signals[:3], 1):
        print(f"  {i}. {s.stock_code} - Price: {s.price}")
    
    # 推送测试
    config = get_config()
    if not config.wechat.webhook_url:
        print("[ERROR] Webhook not configured")
        return 1
    
    print(f"\n[OK] Webhook configured")
    print("[Info] Pushing first 3 signals to WeChat...")
    
    bot = WeChatBot()
    success = 0
    
    for i, signal in enumerate(signals[:3], 1):
        try:
            print(f"\n[{i}/3] Pushing: {signal.stock_code}")
            
            result = await bot.send_stock_signal(
                stock_code=signal.stock_code,
                stock_name=signal.stock_code,  # 用代码代替中文名避免编码问题
                price=float(signal.price),
                change_percent=signal.change_percent or "0%",
                volume=signal.volume or 0,
                indicator=signal.indicator or "TEST",
                trigger_time=signal.trigger_time
            )
            
            if result:
                print(f"  [OK] Push successful")
                success += 1
            else:
                print(f"  [FAIL] Push failed")
            
            if i < 3:
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    # 结果
    print("\n" + "=" * 60)
    print("Test Result")
    print("=" * 60)
    print(f"Total signals: {len(signals)}")
    print(f"Pushed: 3")
    print(f"Success: {success}")
    print(f"Failed: {3 - success}")
    
    if success > 0:
        print("\n[SUCCESS] Test passed!")
        return 0
    else:
        print("\n[FAIL] Test failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
