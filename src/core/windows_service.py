"""Windows服务封装 - 使用pywin32将应用作为Windows服务运行.

支持:
- 安装/卸载Windows服务
- 开机自启动
- 服务状态管理
- 优雅停止
"""

import os
import sys
import time
from pathlib import Path

# pywin32导入
import win32event
import win32service
import win32serviceutil
import servicemanager

from src.config import get_config
from src.core.file_monitor import FileMonitor
from src.core.parser import StockSignalParser
from src.core.wechat_bot import WeChatBot
from src.database_service import get_database_service
from src.logger import get_logger, setup_logger

logger = get_logger(__name__)


class PushStockService(win32serviceutil.ServiceFramework):
    """Push Stock Windows服务.
    
    将股票监控推送系统封装为Windows服务.
    """
    
    _svc_name_ = "PushStockService"
    _svc_display_name_ = "Push Stock Monitor Service"
    _svc_description_ = "监控通达信股票信号并推送到企业微信"
    
    def __init__(self, args):
        """初始化服务."""
        super().__init__(args)
        
        # 创建停止事件
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        
        # 服务状态
        self.is_running = False
        self.file_monitor = None
        self.parser = None
        self.wechat_bot = None
        self.db_service = None
    
    def SvcDoRun(self):
        """服务主运行逻辑."""
        try:
            # 报告服务正在启动
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            # 初始化
            self._initialize()
            
            # 主循环
            self.is_running = True
            while self.is_running:
                # 检查停止信号 (超时1秒)
                result = win32event.WaitForSingleObject(self.stop_event, 1000)
                if result == win32event.WAIT_OBJECT_0:
                    break
            
            # 报告服务已停止
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, '')
            )
            
        except Exception as e:
            logger.error(f"服务运行异常: {e}", exc_info=True)
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                0,
                (self._svc_name_, f"服务异常: {str(e)}")
            )
            raise
    
    def SvcStop(self):
        """停止服务."""
        try:
            # 报告服务正在停止
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            
            # 设置停止标志
            self.is_running = False
            
            # 停止文件监控
            if self.file_monitor:
                self.file_monitor.stop()
            
            # 触发停止事件
            win32event.SetEvent(self.stop_event)
            
            logger.info("服务停止请求已接收")
            
        except Exception as e:
            logger.error(f"停止服务异常: {e}", exc_info=True)
            raise
    
    def _initialize(self) -> None:
        """初始化服务组件."""
        logger.info("正在初始化服务组件...")
        
        # 设置日志
        setup_logger()
        
        # 初始化数据库
        self.db_service = get_database_service()
        
        # 初始化解析器
        self.parser = StockSignalParser()
        
        # 初始化微信机器人
        self.wechat_bot = WeChatBot()
        
        # 初始化文件监控
        self._setup_file_monitor()
        
        logger.info("服务组件初始化完成")
    
    def _setup_file_monitor(self) -> None:
        """设置文件监控."""
        # 获取监控文件配置
        monitor_files = self.db_service.get_all_monitor_files(enabled_only=True)
        
        if not monitor_files:
            logger.warning("没有启用的监控文件配置")
            return
        
        # 创建监控器
        self.file_monitor = FileMonitor(callback=self._on_file_changed)
        
        # 添加监控文件
        for mf in monitor_files:
            if Path(mf.file_path).exists():
                self.file_monitor.add_file(mf.file_path)
                logger.info(f"添加监控文件: {mf.file_path}")
            else:
                logger.warning(f"监控文件不存在: {mf.file_path}")
        
        # 启动监控
        if self.file_monitor._file_paths:
            self.file_monitor.start()
            logger.info(f"文件监控已启动，共{len(self.file_monitor._file_paths)}个文件")
    
    def _on_file_changed(self, file_path: str, new_content: str) -> None:
        """文件变化回调.
        
        Args:
            file_path: 变化的文件路径
            new_content: 新增内容
        """
        try:
            # 解析股票信号
            signals = self.parser.parse_lines(new_content)
            
            if not signals:
                return
            
            logger.info(f"从{file_path}解析到{len(signals)}条信号")
            
            # 处理每个信号
            for signal in signals:
                self._process_signal(signal, file_path)
                
        except Exception as e:
            logger.error(f"处理文件变化失败 {file_path}: {e}", exc_info=True)
    
    def _process_signal(self, signal, file_path: str) -> None:
        """处理单个股票信号.
        
        Args:
            signal: 股票信号
            file_path: 来源文件路径
        """
        try:
            # 保存到数据库
            record = self.db_service.create_push_record(
                stock_code=signal.stock_code,
                stock_name=signal.stock_name,
                price=signal.price,
                trigger_time=signal.trigger_time,
                file_path=file_path,
                raw_content=signal.raw_line,
                change_percent=signal.change_percent,
                volume=signal.volume,
                indicator=signal.indicator
            )
            
            # 推送到微信
            import asyncio
            asyncio.run(self._send_push(record, signal))
            
        except Exception as e:
            logger.error(f"处理信号失败 {signal.stock_code}: {e}", exc_info=True)
    
    async def _send_push(self, record, signal) -> None:
        """发送微信推送.
        
        Args:
            record: 数据库记录
            signal: 股票信号
        """
        try:
            success = await self.wechat_bot.send_stock_signal(
                stock_code=signal.stock_code,
                stock_name=signal.stock_name,
                price=float(signal.price),
                change_percent=signal.change_percent,
                volume=signal.volume,
                indicator=signal.indicator,
                trigger_time=signal.trigger_time
            )
            
            # 更新状态
            status = "success" if success else "failed"
            self.db_service.update_push_status(record.id, status)
            
            logger.info(f"推送{signal.stock_code}: {status}")
            
        except Exception as e:
            logger.error(f"推送失败 {signal.stock_code}: {e}")
            self.db_service.update_push_status(
                record.id,
                "failed",
                error_message=str(e)
            )


def install_service():
    """安装Windows服务."""
    try:
        win32serviceutil.InstallService(
            PushStockService,
            PushStockService._svc_name_,
            displayName=PushStockService._svc_display_name_,
            description=PushStockService._svc_description_,
            startType=win32service.SERVICE_AUTO_START
        )
        print(f"服务'{PushStockService._svc_name_}'安装成功")
        print(f"启动服务: sc start {PushStockService._svc_name_}")
        print(f"停止服务: sc stop {PushStockService._svc_name_}")
    except Exception as e:
        print(f"安装服务失败: {e}")
        raise


def remove_service():
    """卸载Windows服务."""
    try:
        win32serviceutil.RemoveService(PushStockService._svc_name_)
        print(f"服务'{PushStockService._svc_name_}'卸载成功")
    except Exception as e:
        print(f"卸载服务失败: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            install_service()
        elif sys.argv[1] == "remove":
            remove_service()
        else:
            win32serviceutil.HandleCommandLine(PushStockService)
    else:
        # 默认以服务方式运行
        win32serviceutil.HandleCommandLine(PushStockService)
