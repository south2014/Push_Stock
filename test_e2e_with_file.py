"""端到端测试 - 使用真实的回调买.txt文件测试完整流程.

测试流程:
1. 读取 回调买.txt 文件
2. 解析股票信号
3. 推送到企业微信
4. 记录到数据库（可选）
"""

import sys
from pathlib import Path
import asyncio

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core.parser import StockSignalParser
from src.core.wechat_bot import WeChatBot
from src.config import get_config


def read_stock_file(filepath: str) -> str:
    """读取股票信号文件.
    
    Args:
        filepath: 文件路径
        
    Returns:
        文件内容
    """
    # 尝试多种编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"[INFO] 成功读取文件: {filepath}")
            print(f"[INFO] 编码: {encoding}")
            print(f"[INFO] 文件大小: {len(content)} 字符")
            return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"[ERROR] 读取文件失败: {e}")
            return ""
    
    print("[ERROR] 无法识别文件编码")
    return ""


def parse_signals(content: str) -> list:
    """解析股票信号.
    
    Args:
        content: 文件内容
        
    Returns:
        信号列表
    """
    parser = StockSignalParser()
    signals = parser.parse_lines(content)
    print(f"[INFO] 解析到 {len(signals)} 条股票信号")
    return signals


async def push_signals(signals: list, max_count: int = 3) -> int:
    """推送股票信号到微信.
    
    Args:
        signals: 信号列表
        max_count: 最多推送条数（避免刷屏）
        
    Returns:
        成功推送数量
    """
    if not signals:
        print("[WARNING] 没有信号需要推送")
        return 0
    
    # 检查Webhook配置
    config = get_config()
    if not config.wechat.webhook_url:
        print("[ERROR] Webhook URL未配置")
        return 0
    
    print(f"[INFO] Webhook: {config.wechat.webhook_url[:50]}...")
    
    # 创建微信机器人
    bot = WeChatBot()
    
    success_count = 0
    
    # 只推送前max_count条（避免刷屏）
    signals_to_push = signals[:max_count]
    
    print(f"\n[INFO] 开始推送 {len(signals_to_push)} 条信号（共{len(signals)}条）...")
    print("=" * 60)
    
    for i, signal in enumerate(signals_to_push, 1):
        try:
            print(f"\n[{i}/{len(signals_to_push)}] 推送: {signal.stock_code} {signal.stock_name}")
            
            success = await bot.send_stock_signal(
                stock_code=signal.stock_code,
                stock_name=signal.stock_name,
                price=float(signal.price),
                change_percent=signal.change_percent,
                volume=signal.volume,
                indicator=signal.indicator,
                trigger_time=signal.trigger_time
            )
            
            if success:
                print(f"[SUCCESS] 推送成功: {signal.stock_code}")
                success_count += 1
            else:
                print(f"[FAIL] 推送失败: {signal.stock_code}")
            
            # 间隔2秒，避免频率限制
            if i < len(signals_to_push):
                print("[INFO] 等待2秒...")
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"[ERROR] 推送异常 {signal.stock_code}: {e}")
    
    return success_count


def show_signals(signals: list):
    """显示股票信号列表.
    
    Args:
        signals: 信号列表
    """
    print("\n" + "=" * 60)
    print("股票信号列表（前5条）")
    print("=" * 60)
    
    for i, signal in enumerate(signals[:5], 1):
        change = signal.change_percent or "N/A"
        print(f"{i}. {signal.stock_code} {signal.stock_name} "
              f"¥{signal.price} {change} "
              f"Vol:{signal.volume or 'N/A'}")
    
    if len(signals) > 5:
        print(f"... 还有 {len(signals) - 5} 条信号")
    
    print("=" * 60)


async def main():
    """主函数."""
    print("=" * 60)
    print("Push_Stock 端到端测试")
    print("使用真实文件: 回调买.txt")
    print("=" * 60)
    
    # 1. 读取文件
    filepath = r"F:\OpenCode\Push_Stock\回调买.txt"
    content = read_stock_file(filepath)
    
    if not content:
        print("[ERROR] 文件为空或读取失败")
        return 1
    
    # 2. 解析信号
    signals = parse_signals(content)
    
    if not signals:
        print("[ERROR] 未解析到有效信号")
        return 1
    
    # 3. 显示信号
    show_signals(signals)
    
    # 4. 询问是否推送
    print("\n[INFO] 准备推送股票信号到企业微信")
    print("[INFO] 为避免刷屏，只推送前3条信号")
    
    # 自动确认（非交互式）
    print("[INFO] 自动开始推送...")
    
    # 5. 推送信号
    success_count = await push_signals(signals, max_count=3)
    
    # 6. 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"文件: {filepath}")
    print(f"总信号数: {len(signals)}")
    print(f"推送成功: {success_count}")
    print(f"推送失败: {3 - success_count}")
    
    if success_count > 0:
        print(f"\n[SUCCESS] 推送测试通过！成功发送 {success_count} 条消息到微信。")
        return 0
    else:
        print("\n[FAIL] 推送测试失败，请检查：")
        print("1. Webhook URL是否配置正确")
        print("2. 网络连接是否正常")
        print("3. 企业微信群机器人是否正常工作")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
