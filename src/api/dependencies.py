"""依赖注入模块 - FastAPI依赖管理.

提供可复用的依赖项，如数据库会话、配置等.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config import Config, get_config
from src.database_service import DatabaseService, get_database_service
from src.logger import get_logger
from src.models import get_db_session

logger = get_logger(__name__)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话依赖.
    
    Yields:
        SQLAlchemy会话对象
    """
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


def get_config_dependency() -> Config:
    """获取配置依赖.
    
    Returns:
        配置对象
    """
    return get_config()


def get_db_service() -> DatabaseService:
    """获取数据库服务依赖.
    
    Returns:
        数据库服务实例
    """
    return get_database_service()


class CommonQueryParams:
    """通用查询参数.
    
    分页和排序参数.
    """
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        """初始化查询参数.
        
        Args:
            page: 页码
            page_size: 每页数量
            sort_by: 排序字段
            sort_order: 排序方向 (asc/desc)
        """
        self.page = page
        self.page_size = min(page_size, 100)  # 最大100
        self.sort_by = sort_by
        self.sort_order = sort_order


def verify_webhook_configured() -> None:
    """验证Webhook是否已配置.
    
    Raises:
        HTTPException: Webhook未配置
    """
    config = get_config()
    if not config.wechat.webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="企业微信Webhook未配置"
        )


# 便捷函数
CommonParams = Depends(CommonQueryParams)
DbSession = Depends(get_db)
ConfigDep = Depends(get_config_dependency)
DbService = Depends(get_db_service)
VerifyWebhook = Depends(verify_webhook_configured)
