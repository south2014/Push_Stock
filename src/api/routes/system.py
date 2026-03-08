"""System API - 系统状态接口."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SystemStatus(BaseModel):
    service_status: str
    monitor_status: str
    uptime: str
    error_count: int


@router.get("/status")
async def get_system_status():
    """获取系统状态."""
    return {
        "service_status": "running",
        "monitor_status": "watching",
        "uptime": "1天",
        "error_count": 0
    }


@router.post("/start-monitor")
async def start_monitor():
    """启动监控服务."""
    return {"message": "监控服务已启动", "status": "running"}


@router.post("/stop-monitor")
async def stop_monitor():
    """停止监控服务."""
    return {"message": "监控服务已停止", "status": "stopped"}
