"""Config API - 配置管理接口."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from src.api.dependencies import DbService
from src.database_service import DatabaseService
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class FileMonitorConfig(BaseModel):
    id: Optional[int] = None
    file_path: str
    enabled: bool = True
    description: Optional[str] = None


class WeChatConfig(BaseModel):
    webhook_url: str
    owner_user_id: Optional[str] = None
    bot_name: str = "StockBot"
    enabled: bool = True


@router.get("/file-monitors", response_model=List[FileMonitorConfig])
async def get_file_monitors(db_service: DatabaseService = Depends(DbService)):
    """获取监控文件列表."""
    files = db_service.get_all_monitor_files()
    return [{"id": f.id, "file_path": f.file_path, "enabled": f.enabled, "description": f.description} for f in files]


@router.post("/file-monitors")
async def create_file_monitor(config: FileMonitorConfig, db_service: DatabaseService = Depends(DbService)):
    """添加监控文件."""
    file_config = db_service.create_monitor_file(config.file_path, config.enabled, config.description)
    return {"id": file_config.id, "file_path": file_config.file_path, "enabled": file_config.enabled}


@router.get("/wechat")
async def get_wechat_config(db_service: DatabaseService = Depends(DbService)):
    """获取企业微信配置."""
    config = db_service.get_wechat_config()
    if not config:
        return {"webhook_url": "", "bot_name": "StockBot", "enabled": False}
    return {"webhook_url": config.webhook_url, "owner_user_id": config.owner_user_id, "bot_name": config.bot_name, "enabled": config.enabled}


@router.put("/wechat")
async def update_wechat_config(config: WeChatConfig, db_service: DatabaseService = Depends(DbService)):
    """更新企业微信配置."""
    updated = db_service.save_wechat_config(config.webhook_url, config.owner_user_id, config.bot_name, config.enabled)
    return {"message": "更新成功", "webhook_url": updated.webhook_url}
