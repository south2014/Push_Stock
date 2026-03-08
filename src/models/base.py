"""数据库基类模块 - SQLAlchemy ORM基础配置.

提供所有数据模型的基类和数据库连接管理.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    Session,
    declarative_base,
    sessionmaker,
)
from sqlalchemy.pool import StaticPool

from src.config import get_config
from src.logger import get_logger

logger = get_logger(__name__)

# 创建声明式基类
Base = declarative_base()


class BaseModel(Base):
    """所有数据模型的抽象基类.
    
    提供通用的字段和功能.
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="更新时间"
    )
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式.
        
        Returns:
            包含模型数据的字典
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """字符串表示."""
        attrs = [f"{k}={v}" for k, v in self.to_dict().items()]
        return f"<{self.__class__.__name__}({', '.join(attrs)})>"


class DatabaseManager:
    """数据库管理器 - 管理连接和会话.
    
    使用单例模式确保全局唯一的数据库连接.
    """
    
    _instance: "DatabaseManager" = None
    _engine = None
    _session_factory = None
    
    def __new__(cls) -> "DatabaseManager":
        """单例模式."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """初始化数据库管理器."""
        if self._engine is not None:
            return
            
        config = get_config()
        db_path = config.database.path
        
        # 确保数据库目录存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建数据库引擎
        self._engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=config.debug,  # 调试模式输出SQL
        )
        
        # 创建会话工厂
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )
        
        logger.info(f"数据库引擎初始化完成: {db_path}")
    
    def create_tables(self) -> None:
        """创建所有数据表."""
        Base.metadata.create_all(bind=self._engine)
        logger.info("数据库表创建完成")
    
    def get_session(self) -> Session:
        """获取数据库会话.
        
        Returns:
            SQLAlchemy会话对象
        """
        return self._session_factory()
    
    def close(self) -> None:
        """关闭数据库连接."""
        if self._engine:
            self._engine.dispose()
            logger.info("数据库连接已关闭")


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例.
    
    Returns:
        DatabaseManager单例实例
    """
    return DatabaseManager()


def get_db_session() -> Session:
    """获取数据库会话的便捷函数.
    
    Returns:
        SQLAlchemy会话对象
    """
    return get_db_manager().get_session()
