"""Dashboard API - 数据大盘接口.

提供Dashboard页面所需的所有数据接口.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.dependencies import DbService
from src.database_service import DatabaseService
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class DashboardSummary(BaseModel):
    """大盘摘要响应模型."""
    today_total: int
    today_success: int
    today_failed: int
    success_rate: str
    monitor_status: str
    uptime: str
    last_push_time: Optional[str]


class SuccessRateTrendItem(BaseModel):
    """成功率趋势项."""
    date: str
    success_count: int
    failed_count: int
    success_rate: float


class StockDistributionItem(BaseModel):
    """股票分布项."""
    code: str
    name: str
    count: int
    percentage: float


class PushRecordItem(BaseModel):
    """推送记录项."""
    id: int
    stock_code: str
    stock_name: str
    price: float
    change_percent: Optional[float]
    trigger_time: str
    status: str


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    db_service: DatabaseService = Depends(DbService)
) -> DashboardSummary:
    """获取大盘摘要数据."""
    try:
        # 获取今日统计
        stats = db_service.get_daily_stats()
        
        # 计算成功率
        total = stats["total"]
        success = stats["success"]
        failed = stats["failed"]
        success_rate = f"{(success / total * 100):.2f}%" if total > 0 else "0.00%"
        
        # 获取最近推送
        recent = db_service.get_recent_pushes(limit=1)
        last_push_time = recent[0].trigger_time if recent else None
        
        return DashboardSummary(
            today_total=total,
            today_success=success,
            today_failed=failed,
            success_rate=success_rate,
            monitor_status="running",  # TODO: 从实际监控服务获取
            uptime="1天",  # TODO: 计算实际运行时间
            last_push_time=last_push_time
        )
    except Exception as e:
        logger.error(f"获取摘要失败: {e}")
        raise HTTPException(status_code=500, detail="获取数据失败")


@router.get("/success-rate-trend")
async def get_success_rate_trend(
    days: int = Query(default=7, ge=1, le=30),
    db_service: DatabaseService = Depends(DbService)
) -> dict:
    """获取成功率趋势."""
    try:
        trend = []
        for i in range(days - 1, -1, -1):
            date = datetime.now() - timedelta(days=i)
            stats = db_service.get_daily_stats(date)
            
            total = stats["total"]
            success = stats["success"]
            failed = stats["failed"]
            rate = (success / total) if total > 0 else 1.0
            
            trend.append({
                "date": stats["date"],
                "success_count": success,
                "failed_count": failed,
                "success_rate": round(rate, 4)
            })
        
        return {"list": trend, "total": len(trend)}
    except Exception as e:
        logger.error(f"获取趋势失败: {e}")
        raise HTTPException(status_code=500, detail="获取数据失败")


@router.get("/stock-distribution")
async def get_stock_distribution(
    days: int = Query(default=30, ge=1, le=90),
    limit: int = Query(default=20, ge=1, le=50),
    db_service: DatabaseService = Depends(DbService)
) -> dict:
    """获取股票触发分布."""
    try:
        # 获取最近推送记录
        cutoff_date = datetime.now() - timedelta(days=days)
        records = db_service.get_recent_pushes(limit=1000)
        
        # 统计每只股票触发次数
        stock_counts = {}
        for record in records:
            key = (record.stock_code, record.stock_name)
            stock_counts[key] = stock_counts.get(key, 0) + 1
        
        # 排序并取Top
        sorted_stocks = sorted(
            stock_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        total = sum(count for _, count in sorted_stocks)
        
        distribution = []
        for (code, name), count in sorted_stocks:
            percentage = (count / total * 100) if total > 0 else 0
            distribution.append({
                "code": code,
                "name": name,
                "count": count,
                "percentage": round(percentage, 2)
            })
        
        return {"list": distribution, "total": len(distribution)}
    except Exception as e:
        logger.error(f"获取分布失败: {e}")
        raise HTTPException(status_code=500, detail="获取数据失败")


@router.get("/recent-pushes")
async def get_recent_pushes(
    limit: int = Query(default=10, ge=1, le=100),
    db_service: DatabaseService = Depends(DbService)
) -> dict:
    """获取最近推送记录."""
    try:
        records = db_service.get_recent_pushes(limit=limit)
        
        items = []
        for record in records:
            items.append({
                "id": record.id,
                "stock_code": record.stock_code,
                "stock_name": record.stock_name,
                "price": float(record.price),
                "change_percent": float(record.change_percent) if record.change_percent else None,
                "trigger_time": record.trigger_time,
                "status": record.status
            })
        
        return {"list": items, "total": len(items)}
    except Exception as e:
        logger.error(f"获取记录失败: {e}")
        raise HTTPException(status_code=500, detail="获取数据失败")
