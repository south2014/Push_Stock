"""Webhook调试脚本 - 显示完整的HTTP响应信息.

用于调试企业微信API的具体错误.
"""

import requests
import json
import sys

# Webhook URL
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=19faf146-7331-414a-8ae9-583c42ed5a3a"

def test_simple_text():
    """测试简单文本消息."""
    print("=" * 60)
    print("测试1: 发送简单文本消息")
    print("=" * 60)
    
    payload = {
        "msgtype": "text",
        "text": {
            "content": "触发监控：600519，当前价格：1500"
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"返回详情: {response.text}")
        print(f"响应头: {dict(response.headers)}")
        
        # 解析JSON响应
        try:
            result = response.json()
            print(f"错误码: {result.get('errcode')}")
            print(f"错误信息: {result.get('errmsg')}")
            
            if result.get('errcode') == 0:
                print("[SUCCESS] 发送成功！")
                return True
            else:
                print(f"[FAIL] 发送失败，错误码: {result.get('errcode')}")
                return False
                
        except json.JSONDecodeError:
            print("[FAIL] 响应不是有效的JSON")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] 请求异常: {e}")
        return False


def test_markdown():
    """测试Markdown消息."""
    print("\n" + "=" * 60)
    print("测试2: 发送Markdown消息")
    print("=" * 60)
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": "**股票信号**\n\n| 代码 | 名称 | 价格 |\n|------|------|------|\n| 600519 | 贵州茅台 | 1500 |"
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"返回详情: {response.text}")
        
        result = response.json()
        print(f"错误码: {result.get('errcode')}")
        print(f"错误信息: {result.get('errmsg')}")
        
        if result.get('errcode') == 0:
            print("[SUCCESS] 发送成功！")
            return True
        else:
            print(f"[FAIL] 发送失败")
            return False
            
    except Exception as e:
        print(f"[FAIL] 异常: {e}")
        return False


def check_error_code(errcode: int):
    """检查错误码含义."""
    error_codes = {
        0: "成功",
        93000: "无效的Webhook URL",
        93001: "无效的请求格式",
        93002: "无效的请求参数",
        93003: "无效的请求方法",
        93004: "消息体过大",
        93005: "发送消息过于频繁",
        93006: "企业微信内部错误",
    }
    
    return error_codes.get(errcode, f"未知错误码: {errcode}")


def main():
    """主函数."""
    print("=" * 60)
    print("Webhook 调试工具")
    print("=" * 60)
    print(f"URL: {WEBHOOK_URL[:60]}...")
    print()
    
    # 测试1
    result1 = test_simple_text()
    
    # 测试2
    if result1:
        print("\n等待2秒...")
        import time
        time.sleep(2)
        result2 = test_markdown()
    else:
        result2 = False
    
    # 汇总
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"文本测试: {'通过' if result1 else '失败'}")
    print(f"Markdown测试: {'通过' if result2 else '失败'}")
    
    if result1 and result2:
        print("\n[SUCCESS] 所有测试通过！Webhook工作正常。")
        return 0
    else:
        print("\n[FAIL] 测试失败，请检查错误码：")
        print("- 93000: URL无效，需要重新生成")
        print("- 93005: 触发频率限制，请等待1分钟")
        print("- 其他错误: 请参考企业微信文档")
        return 1


if __name__ == "__main__":
    sys.exit(main())
