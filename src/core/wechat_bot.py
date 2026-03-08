"""企业微信机器人 - 推送消息到企业微信群.

支持:
- 文本消息推送
- Markdown消息推送
- 异步发送
- 失败重试（指数退避）
- 频率限制保护
"""

import asyncio
import json
from typing import Optional

import requests

from src.config import get_config
from src.constants import WECHAT_WEBHOOK_PREFIX
from src.exceptions import PushException, WeChatAPIException
from src.logger import get_logger

logger = get_logger(__name__)


class WeChatBot:
    """企业微信机器人客户端.
    
    封装企业微信Webhook API调用.
    """
    
    # API基础URL
    BASE_URL = WECHAT_WEBHOOK_PREFIX
    
    # 请求超时（秒）
    TIMEOUT = 10.0
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        retry_count: int = 3,
        retry_intervals: Optional[list] = None
    ) -> None:
        """初始化微信机器人.
        
        Args:
            webhook_url: Webhook URL（默认从配置读取）
            retry_count: 失败重试次数
            retry_intervals: 重试间隔列表（秒）
        """
        if webhook_url:
            self.webhook_url = webhook_url
        else:
            config = get_config()
            self.webhook_url = config.wechat.webhook_url
        
        self.retry_count = retry_count
        self.retry_intervals = retry_intervals or [5, 30, 120]
        
        # 统计
        self.sent_count = 0
        self.failed_count = 0
    
    async def send_text(
        self,
        content: str,
        mentioned_list: Optional[list] = None,
        mentioned_mobile_list: Optional[list] = None
    ) -> bool:
        """发送文本消息.
        
        Args:
            content: 消息内容
            mentioned_list: @用户ID列表
            mentioned_mobile_list: @手机号列表
            
        Returns:
            发送是否成功
        """
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        if mentioned_list:
            data["text"]["mentioned_list"] = mentioned_list
        if mentioned_mobile_list:
            data["text"]["mentioned_mobile_list"] = mentioned_mobile_list
        
        return await self._send_with_retry(data)
    
    async def send_markdown(
        self,
        content: str
    ) -> bool:
        """发送Markdown消息.
        
        Args:
            content: Markdown格式内容
            
        Returns:
            发送是否成功
        """
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        return await self._send_with_retry(data)
    
    async def send_stock_signal(
        self,
        stock_code: str,
        stock_name: str,
        price: float,
        change_percent: Optional[str] = None,
        volume: Optional[int] = None,
        indicator: Optional[str] = None,
        trigger_time: Optional[str] = None
    ) -> bool:
        """发送股票信号消息（Markdown表格格式）.
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            price: 当前价格
            change_percent: 涨跌幅
            volume: 成交量
            indicator: 指标标识
            trigger_time: 触发时间
            
        Returns:
            发送是否成功
        """
        # 构建涨跌幅显示
        change_display = change_percent if change_percent else "--"
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

> 数据来源: 通达信监控系统
"""
        
        return await self.send_markdown(content)
    
    async def _send_with_retry(self, data: dict) -> bool:
        """带重试机制的发送.
        
        Args:
            data: 请求数据
            
        Returns:
            发送是否成功
        """
        if not self.webhook_url:
            logger.error("Webhook URL未配置")
            raise PushException(
                "Webhook URL未配置",
                code=PushException.WEBHOOK_INVALID
            )
        
        last_error = None
        
        for attempt in range(self.retry_count + 1):
            try:
                success = await self._send_once(data)
                if success:
                    self.sent_count += 1
                    return True
                    
            except WeChatAPIException as e:
                last_error = e
                
                # 如果是限流错误，等待更久
                if e.errcode == 45009:  # 频率限制
                    wait_time = 60
                    logger.warning(f"触发频率限制，等待{wait_time}秒")
                else:
                    wait_time = self.retry_intervals[min(attempt, len(self.retry_intervals) - 1)]
                
                if attempt < self.retry_count:
                    logger.warning(
                        f"发送失败，{wait_time}秒后重试 "
                        f"({attempt + 1}/{self.retry_count}): {e.message}"
                    )
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                last_error = e
                wait_time = self.retry_intervals[min(attempt, len(self.retry_intervals) - 1)]
                
                if attempt < self.retry_count:
                    logger.warning(
                        f"发送异常，{wait_time}秒后重试 "
                        f"({attempt + 1}/{self.retry_count}): {e}"
                    )
                    await asyncio.sleep(wait_time)
        
        # 所有重试都失败
        self.failed_count += 1
        logger.error(f"发送失败，已重试{self.retry_count}次: {last_error}")
        
        raise PushException(
            f"发送失败: {last_error}",
            webhook_url=self.webhook_url,
            retry_count=self.retry_count,
            code=PushException.MAX_RETRY_EXCEEDED
        )
    
    async def _send_once(self, data: dict) -> bool:
        """单次发送请求.
        
        Args:
            data: 请求数据
            
        Returns:
            是否成功
            
        Raises:
            WeChatAPIException: API返回错误
        """
        response = requests.post(
            self.webhook_url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=self.TIMEOUT
        )
        
        result = response.json()
        
        if result.get("errcode") == 0:
            logger.debug(f"发送成功: {data.get('msgtype')}")
            return True
        
        # API返回错误
        raise WeChatAPIException(
            message=f"微信API错误: {result.get('errmsg', '未知错误')}",
            errcode=result.get("errcode", -1),
            errmsg=result.get("errmsg", ""),
            webhook_url=self.webhook_url
        )
    
    def get_stats(self) -> dict:
        """获取发送统计.
        
        Returns:
            统计信息
        """
        return {
            "sent": self.sent_count,
            "failed": self.failed_count,
            "total": self.sent_count + self.failed_count
        }
    
    async def test_connection(self) -> bool:
        """测试Webhook连接.
        
        Returns:
            连接是否正常
        """
        try:
            await self.send_text("测试消息 - Push_Stock系统连接正常")
            return True
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False


# 便捷函数
async def send_stock_push(
    stock_code: str,
    stock_name: str,
    price: float,
    **kwargs
) -> bool:
    """便捷函数：发送股票推送.
    
    Args:
        stock_code: 股票代码
        stock_name: 股票名称
        price: 价格
        **kwargs: 其他参数
        
    Returns:
        发送是否成功
    """
    bot = WeChatBot()
    return await bot.send_stock_signal(
        stock_code, stock_name, price, **kwargs
    )
