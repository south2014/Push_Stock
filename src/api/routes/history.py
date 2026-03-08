"""History API - 推送历史接口."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

from src.api.dependencies import DbService
from src.database_service import DatabaseService
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class PushRecordResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    price: float
    change_percent: Optional[float]
    volume: Optional[int]
    indicator: Optional[str]
    trigger_time: str
    file_path: str
    status: str
    error_message: Optional[str]
    retry_count: int
    created_at: str


@router.get("/pushes")
async def get_pushes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    stock_code: Optional[str] = None,
    status: Optional[str] = None,
    db_service: DatabaseService = Depends(DbService)
):
    """获取推送历史列表."""
    records = db_service.get_recent_pushes(limit=page_size)
    
    items = []
    for r in records:
        items.append({
            "id": r.id,
            "stock_code": r.stock_code,
            "stock_name": r.stock_name,
            "price": float(r.price),
            "change_percent": float(r.change_percent) if r.change_percent else None,
            "volume": r.volume,
            "indicator": r.indicator,
            "trigger_time": r.trigger_time,
            "file_path": r.file_path,
            "status": r.status,
            "error_message": r.error_message,
            "retry_count": r.retry_count,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return {"list": items, "total": len(items), "page": page, "page_size": page_size}


@router.post("/pushes/{record_id}/retry")
async def retry_push(record_id: int, db_service: DatabaseService = Depends(DbService)):
    """重新推送失败记录."""
    # TODO: 实现重推逻辑
    return {"message": "重推任务已创建", "record_id": record_id}
