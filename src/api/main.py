"""FastAPI应用入口 - Push Stock API服务.

提供RESTful API接口用于:
- Dashboard数据查询
- 配置管理
- 推送历史
- 系统监控
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import config, dashboard, history, system
from src.config import get_config
from src.database_service import get_database_service
from src.logger import get_logger, setup_logger
from src.models import get_db_manager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理.
    
    启动时初始化数据库，关闭时清理资源.
    """
    # 启动
    logger.info("正在初始化Push Stock API服务...")
    
    # 设置日志
    setup_logger()
    
    # 初始化数据库
    try:
        db_manager = get_db_manager()
        db_manager.create_tables()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    
    logger.info("API服务启动完成")
    yield
    
    # 关闭
    logger.info("正在关闭API服务...")
    get_db_manager().close()
    logger.info("API服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例.
    
    Returns:
        FastAPI应用实例
    """
    config = get_config()
    
    app = FastAPI(
        title="Push Stock API",
        description="股票信号推送监控系统API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vue开发服务器
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(
        dashboard.router,
        prefix="/api/dashboard",
        tags=["Dashboard"]
    )
    app.include_router(
        config.router,
        prefix="/api/config",
        tags=["Config"]
    )
    app.include_router(
        history.router,
        prefix="/api/history",
        tags=["History"]
    )
    app.include_router(
        system.router,
        prefix="/api/system",
        tags=["System"]
    )
    
    # 根路由
    @app.get("/")
    async def root():
        """API根路径."""
        return {
            "message": "Push Stock API",
            "version": "1.0.0",
            "docs": "/docs"
        }
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查端点."""
        return {"status": "healthy"}
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    uvicorn.run(
        "src.api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload
    )
