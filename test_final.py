"""终极测试 - 直接使用硬编码URL测试推送.
"""

import requests
import json

# 硬编码URL（从用户提供）
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=19faf146-7331-414a-8ae9-583c42ed5a3a"

def send_text(content: str) -> bool:
    """发送文本消息."""
    payload = {
        "msgtype": "text",
        "text": {"content": content}
    }
    
    try:
        resp = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        result = resp.json()
        print(f"Status: {resp.status_code}")
        print(f"Response: {result}")
        
        return result.get("errcode") == 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def send_markdown(content: str) -> bool:
    """发送Markdown消息."""
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": content}
    }
    
    try:
        resp = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        result = resp.json()
        print(f"Status: {resp.status_code}")
        print(f"Response: {result}")
        
        return result.get("errcode") == 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def send_stock_signal(stock_code: str, stock_name: str, price: float, 
                      change_percent: str = None, volume: int = None) -> bool:
    """发送股票信号."""
    # 构建Markdown
    change_display = change_percent if change_percent else "N/A"
    vol_display = str(volume) if volume else "N/A"
    
    content = f"""**股票信号推送**

| 项目 | 内容 |
|------|------|
| **股票代码** | {stock_code} |
| **股票名称** | {stock_name} |
| **当前价格** | ¥{price:.2f} |
| **涨跌幅** | {change_display} |
| **成交量** | {vol_display} 手 |

> 时间: 2026-03-08 18:30:00
"""
    
    return send_markdown(content)


def main():
    """主函数."""
    print("=" * 60)
    print("终极推送测试")
    print("=" * 60)
    print(f"URL: {WEBHOOK_URL[:50]}...")
    print()
    
    # 测试1: 文本消息
    print("Test 1: Text message")
    if send_text("Push_Stock测试消息\n这是一条测试\nFrom: 回调买.txt"):
        print("[OK] Text sent successfully")
    else:
        print("[FAIL] Text failed")
    
    print()
    
    # 测试2: 股票信号
    print("Test 2: Stock signal")
    if send_stock_signal(
        stock_code="600519",
        stock_name="贵州茅台",
        price=1680.50,
        change_percent="+3.92%",
        volume=1250
    ):
        print("[OK] Stock signal sent successfully")
    else:
        print("[FAIL] Stock signal failed")


if __name__ == "__main__":
    main()
