"""文件监控器 - 使用Watchdog实时监控文件变化.

采用混合策略:
1. Watchdog实时监控 (毫秒级响应)
2. 定时轮询兜底 (10秒间隔)
3. 文件哈希校验避免重复处理
4. 增量读取提升性能
"""

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.config import get_config
from src.database_service import get_database_service
from src.exceptions import MonitorException
from src.logger import get_logger

logger = get_logger(__name__)


class FileChangeHandler(FileSystemEventHandler):
    """文件变化事件处理器."""
    
    def __init__(
        self,
        callback: Callable[[str, str], None],
        file_paths: Set[str]
    ):
        """初始化处理器.
        
        Args:
            callback: 变化回调函数 (file_path, new_content)
            file_paths: 监控的文件路径集合
        """
        self.callback = callback
        self.file_paths = file_paths
        self._last_positions: Dict[str, int] = {}
        self._last_hashes: Dict[str, str] = {}
    
    def on_modified(self, event):
        """文件修改事件回调."""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # 只处理监控列表中的文件
        if file_path not in self.file_paths:
            return
        
        try:
            self._handle_file_change(file_path)
        except Exception as e:
            logger.error(f"处理文件变化失败 {file_path}: {e}")
    
    def _handle_file_change(self, file_path: str) -> None:
        """处理文件变化.
        
        Args:
            file_path: 变化的文件路径
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return
        
        # 获取当前文件大小
        current_size = path.stat().st_size
        last_position = self._last_positions.get(file_path, 0)
        
        # 文件被清空或重置
        if current_size < last_position:
            logger.info(f"文件被重置: {file_path}")
            self._last_positions[file_path] = 0
            last_position = 0
        
        # 无新增内容
        if current_size == last_position:
            return
        
        # 读取新增内容
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                f.seek(last_position)
                new_content = f.read()
                current_position = f.tell()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return
        
        if not new_content.strip():
            return
        
        # 计算内容哈希
        content_hash = hashlib.sha256(new_content.encode()).hexdigest()
        last_hash = self._last_hashes.get(file_path, "")
        
        # 检查是否重复内容
        if content_hash == last_hash:
            logger.debug(f"内容未变化: {file_path}")
            self._last_positions[file_path] = current_position
            return
        
        # 更新状态
        self._last_hashes[file_path] = content_hash
        self._last_positions[file_path] = current_position
        
        logger.info(f"检测到文件变化: {file_path} (+{len(new_content)} 字节)")
        
        # 触发回调
        try:
            self.callback(file_path, new_content)
        except Exception as e:
            logger.error(f"回调执行失败: {e}")
    
    def update_position(self, file_path: str, position: int) -> None:
        """更新文件读取位置.
        
        Args:
            file_path: 文件路径
            position: 新位置
        """
        self._last_positions[file_path] = position


class FileMonitor:
    """文件监控器.
    
    使用Watchdog实现实时文件监控.
    """
    
    def __init__(
        self,
        callback: Optional[Callable[[str, str], None]] = None,
        fallback_interval: float = 10.0
    ):
        """初始化监控器.
        
        Args:
            callback: 文件变化回调函数
            fallback_interval: 兜底轮询间隔（秒）
        """
        self.callback = callback
        self.fallback_interval = fallback_interval
        
        self._observer: Optional[Observer] = None
        self._handler: Optional[FileChangeHandler] = None
        self._monitoring = False
        self._file_paths: Set[str] = set()
        self._db_service = get_database_service()
        
        # 统计
        self.change_count = 0
        self.error_count = 0
    
    def add_file(self, file_path: str) -> None:
        """添加监控文件.
        
        Args:
            file_path: 文件完整路径
        """
        self._file_paths.add(file_path)
        logger.info(f"添加监控文件: {file_path}")
    
    def remove_file(self, file_path: str) -> None:
        """移除监控文件.
        
        Args:
            file_path: 文件完整路径
        """
        self._file_paths.discard(file_path)
        logger.info(f"移除监控文件: {file_path}")
    
    def start(self) -> None:
        """启动监控."""
        if not self._file_paths:
            logger.warning("没有配置监控文件")
            return
        
        if self._monitoring:
            logger.warning("监控已在运行")
            return
        
        # 创建事件处理器
        self._handler = FileChangeHandler(
            callback=self._on_file_changed,
            file_paths=self._file_paths
        )
        
        # 创建Observer
        self._observer = Observer()
        
        # 为每个文件所在目录添加监控
        watched_dirs: Set[str] = set()
        for file_path in self._file_paths:
            dir_path = str(Path(file_path).parent)
            if dir_path not in watched_dirs:
                self._observer.schedule(
                    self._handler,
                    dir_path,
                    recursive=False
                )
                watched_dirs.add(dir_path)
                logger.info(f"监控目录: {dir_path}")
        
        # 启动Observer
        self._observer.start()
        self._monitoring = True
        
        logger.info(f"文件监控已启动，共{len(self._file_paths)}个文件")
        
        # 启动兜底轮询
        asyncio.create_task(self._fallback_polling())
    
    def stop(self) -> None:
        """停止监控."""
        if not self._monitoring:
            return
        
        self._monitoring = False
        
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        
        logger.info("文件监控已停止")
    
    def _on_file_changed(self, file_path: str, new_content: str) -> None:
        """文件变化回调.
        
        Args:
            file_path: 文件路径
            new_content: 新增内容
        """
        self.change_count += 1
        
        # 更新数据库中的文件位置
        try:
            self._update_file_position_in_db(file_path)
        except Exception as e:
            logger.error(f"更新文件位置失败: {e}")
        
        # 调用用户回调
        if self.callback:
            try:
                self.callback(file_path, new_content)
            except Exception as e:
                self.error_count += 1
                logger.error(f"用户回调执行失败: {e}")
    
    def _update_file_position_in_db(self, file_path: str) -> None:
        """更新数据库中的文件位置.
        
        Args:
            file_path: 文件路径
        """
        # 获取当前文件大小
        try:
            current_size = Path(file_path).stat().st_size
        except:
            return
        
        # 查找对应的monitor_files记录
        monitor_files = self._db_service.get_all_monitor_files()
        for mf in monitor_files:
            if mf.file_path == file_path:
                self._db_service.update_file_position(mf.id, current_size)
                break
    
    async def _fallback_polling(self) -> None:
        """兜底轮询 - 防止Watchdog漏检."""
        while self._monitoring:
            try:
                await asyncio.sleep(self.fallback_interval)
                
                if not self._monitoring:
                    break
                
                # 检查所有文件
                for file_path in self._file_paths:
                    try:
                        if self._handler:
                            self._handler._handle_file_change(file_path)
                    except Exception as e:
                        logger.error(f"兜底轮询检查失败 {file_path}: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"兜底轮询异常: {e}")
    
    def is_monitoring(self) -> bool:
        """是否正在监控.
        
        Returns:
            监控状态
        """
        return self._monitoring
    
    def get_stats(self) -> dict:
        """获取监控统计.
        
        Returns:
            统计信息
        """
        return {
            "monitoring": self._monitoring,
            "file_count": len(self._file_paths),
            "change_count": self.change_count,
            "error_count": self.error_count
        }


# 便捷函数
def create_monitor(
    file_paths: List[str],
    callback: Callable[[str, str], None]
) -> FileMonitor:
    """便捷函数：创建并启动监控器.
    
    Args:
        file_paths: 监控文件路径列表
        callback: 变化回调函数
        
    Returns:
        FileMonitor实例
    """
    monitor = FileMonitor(callback=callback)
    
    for path in file_paths:
        monitor.add_file(path)
    
    monitor.start()
    return monitor
