"""微信推送测试脚本 - 手动测试企业微信机器人.

使用方法:
    venv\Scripts\python.exe test_wechat_push.py

功能:
    - 测试文本消息推送
    - 测试Markdown消息推送
    - 测试股票信号格式推送
"""

import asyncio
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core.wechat_bot import WeChatBot
from src.config import get_config


async def test_text_message():
    """测试文本消息推送."""
    print("\n" + "="*60)
    print("测试1: 发送文本消息")
    print("="*60)
    
    try:
        bot = WeChatBot()
        success = await bot.send_text(
            "Push_Stock系统测试\n"
            "这是一条测试消息\n"
            "时间: 2026-03-08 18:10:00\n"
            "状态: 测试正常"
        )
        
        if success:
            print("[PASS] 文本消息发送成功！")
            return True
        else:
            print("[FAIL] 文本消息发送失败")
            return False
            
    except Exception as e:
        print(f"[FAIL] 发送失败: {e}")
        return False


async def test_markdown_message():
    """测试Markdown消息推送."""
    print("\n" + "="*60)
    print("测试2: 发送Markdown消息")
    print("="*60)
    
    try:
        bot = WeChatBot()
        
        # 构建Markdown消息
        content = """**Push_Stock系统测试**

| 项目 | 内容 |
|------|------|
| **测试类型** | Markdown格式 |
| **发送时间** | 2026-03-08 18:10:00 |
| **测试结果** | 🟢 正常 |

> 这是一条测试消息，用于验证Markdown格式是否正常显示。
"""
        
        success = await bot.send_markdown(content)
        
        if success:
            print("[PASS] Markdown消息发送成功！")
            return True
        else:
            print("[FAIL] Markdown消息发送失败")
            return False
            
    except Exception as e:
        print(f"[FAIL] 发送失败: {e}")
        return False


async def test_stock_signal_message():
    """测试股票信号格式推送."""
    print("\n" + "="*60)
    print("测试3: 发送股票信号消息")
    print("="*60)
    
    try:
        bot = WeChatBot()
        success = await bot.send_stock_signal(
            stock_code="600519",
            stock_name="贵州茅台",
            price=1680.50,
            change_percent="3.92%",
            volume=1250,
            indicator="BBIHTM_G",
            trigger_time="2026-03-08 18:10:00"
        )
        
        if success:
            print("[PASS] 股票信号消息发送成功！")
            return True
        else:
            print("[FAIL] 股票信号消息发送失败")
            return False
            
    except Exception as e:
        print(f"[FAIL] 发送失败: {e}")
        return False


async def test_connection():
    """测试Webhook连接."""
    print("\n" + "="*60)
    print("预检查: Webhook配置")
    print("="*60)
    
    config = get_config()
    webhook_url = config.wechat.webhook_url
    
    if not webhook_url:
        print("[FAIL] Webhook URL未配置！")
        print("请设置环境变量: WECHAT_WEBHOOK_URL")
        return False
    
    print(f"[INFO] Webhook URL: {webhook_url[:50]}...")
    
    if "__PLACEHOLDER__" in webhook_url:
        print("[WARNING] 使用的是占位符URL，需要配置真实Webhook")
        return False
    
    print("[PASS] Webhook已配置")
    return True


async def main():
    """主函数."""
    print("="*60)
    print("Push_Stock 微信推送测试")
    print("="*60)
    
    # 先检查配置
    if not await test_connection():
        print("\n[ERROR] 配置检查失败，请检查Webhook URL")
        return 1
    
    results = []
    
    # 测试1: 文本消息
    results.append(("文本消息", await test_text_message()))
    
    # 等待2秒避免频率限制
    await asyncio.sleep(2)
    
    # 测试2: Markdown消息
    results.append(("Markdown消息", await test_markdown_message()))
    
    # 等待2秒
    await asyncio.sleep(2)
    
    # 测试3: 股票信号
    results.append(("股票信号", await test_stock_signal_message()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有推送测试通过！微信机器人工作正常。")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} 项测试失败。")
        print("\n可能的错误原因:")
        print("1. Webhook URL无效或已过期")
        print("2. 企业微信群机器人已被删除")
        print("3. 网络连接问题")
        print("4. 触发企业微信频率限制")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
