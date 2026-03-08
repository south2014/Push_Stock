# Push_Stock 数据库设计文档

**版本**: v1.0  
**制定日期**: 2026-03-08  
**数据库**: SQLite 3.40+  
**状态**: 已确认

---

## 一、数据库设计总览

### 1.1 数据库选型

**选择 SQLite 的理由:**

1. **零配置**: 无需安装数据库服务器，文件即数据库
2. **轻量级**: 适合桌面应用，资源占用低
3. **可移植**: 数据库文件可复制、备份、迁移
4. **性能**: 对小到中型数据量(百万级)性能优秀
5. **ACID**: 支持事务，保证数据一致性
6. **Python生态**: SQLAlchemy原生支持

**适用场景:**
- 个人桌面应用
- 数据量 < 100万条
- 并发连接数 < 100
- 单用户/少用户访问

**未来迁移路径:**
- SQLite → PostgreSQL/MySQL (云部署时)
- SQLAlchemy ORM保证迁移平滑

---

### 1.2 数据库文件结构

```
Push_Stock/
└── data/
    ├── push_stock.db           # 主数据库文件
    ├── push_stock.db-shm       # SQLite共享内存文件
    ├── push_stock.db-wal       # SQLite预写日志文件
    └── backup_20260308.sql     # 备份文件(脚本自动生成)
```

---

## 二、数据表设计

### 2.1 push_records (推送记录表)

**表说明**: 存储所有股票信号推送记录，核心数据表

#### 表结构

```sql
CREATE TABLE push_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code VARCHAR(6) NOT NULL,
    stock_name VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    change_percent DECIMAL(8,2),
    volume INTEGER,
    indicator VARCHAR(20),
    trigger_time DATETIME NOT NULL,
    file_path TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    webhook_response TEXT,
    wechat_message_id VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, price, trigger_time)
);
```

#### 字段详解

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键，自增ID | 1001 |
| stock_code | VARCHAR(6) | NOT NULL | 股票代码(6位数字) | 600519 |
| stock_name | VARCHAR(20) | NOT NULL | 股票名称 | 贵州茅台 |
| price | DECIMAL(10,2) | NOT NULL | 触发价格(保留2位小数) | 1680.50 |
| change_percent | DECIMAL(8,2) | - | 涨跌幅(%) | 3.92 |
| volume | INTEGER | - | 成交量(手) | 1250 |
| indicator | VARCHAR(20) | - | 指标标识 | BBIHTM_G |
| trigger_time | DATETIME | NOT NULL | 触发时间 | 2026-03-08 10:30:25 |
| file_path | TEXT | NOT NULL | 监控文件完整路径 | C:\\...\\回调买.txt |
| raw_content | TEXT | NOT NULL | 原始文件行内容 | 600519\\t贵州茅台\\t... |
| status | VARCHAR(20) | DEFAULT 'pending' | 推送状态 | success/failed/pending |
| error_message | TEXT | - | 错误信息 | 网络超时 |
| retry_count | INTEGER | DEFAULT 0 | 已重试次数 | 0 |
| webhook_response | TEXT | - | 企业微信响应JSON | {"errcode":0,...} |
| wechat_message_id | VARCHAR(100) | - | 微信消息ID | - |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | 2026-03-08 10:30:30 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 | 2026-03-08 10:30:30 |

#### 约束说明

- `UNIQUE(stock_code, price, trigger_time)`: 防止重复推送同股票同价格同时间点的信号
- `VARCHAR(6)`: 股票代码固定6位数字(A股)
- `DECIMAL(10,2)`: 价格最大支持99999999.99，足够覆盖所有股票
- `TEXT`: 原始行内容可能包含备注信息，长度不固定

#### 索引设计

```sql
-- 推送时间查询 (最常用)
CREATE INDEX idx_push_records_trigger_time ON push_records(trigger_time DESC);

-- 股票代码查询
CREATE INDEX idx_push_records_stock_code ON push_records(stock_code);

-- 状态查询 (筛选成功/失败)
CREATE INDEX idx_push_records_status ON push_records(status);

-- 创建时间查询 (分页列表)
CREATE INDEX idx_push_records_created_at ON push_records(created_at DESC);

-- 复合索引 (多条件筛选)
CREATE INDEX idx_push_records_multi_query ON push_records(stock_code, status, trigger_time DESC);
```

#### 性能预估

- **数据量**: 每天约100-500条信号
- **年数据量**: 3.6万 - 18万条
- **查询性能**: 索引优化后 < 100ms
- **写入性能**: < 50ms (含索引更新)

---

### 2.2 monitor_files (监控文件配置表)

**表说明**: 配置需要监控的文件路径及相关参数

#### 表结构

```sql
CREATE TABLE monitor_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    description TEXT,
    last_position INTEGER DEFAULT 0,
    last_processed_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 字段详解

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 配置ID | 1 |
| file_path | TEXT | UNIQUE NOT NULL | 监控文件完整路径 | C:\\...\\回调买.txt |
| enabled | BOOLEAN | DEFAULT 1 | 是否启用 | true/false |
| description | TEXT | - | 配置描述 | "回调买入策略" |
| last_position | INTEGER | DEFAULT 0 | 上次读取位置(字节) | 15200 |
| last_processed_time | DATETIME | - | 最后处理时间 | 2026-03-08 10:30:25 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | 2026-03-08 09:00:00 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 | 2026-03-08 10:00:00 |

#### 索引设计

```sql
-- 路径唯一索引
CREATE UNIQUE INDEX idx_monitor_files_path ON monitor_files(file_path);

-- 启用状态查询
CREATE INDEX idx_monitor_files_enabled ON monitor_files(enabled);
```

#### 使用场景

```python
# 查询所有启用的监控文件
SELECT * FROM monitor_files WHERE enabled = 1;

# 更新文件最后读取位置
UPDATE monitor_files 
SET last_position = ?, last_processed_time = ? 
WHERE id = ?;
```

---

### 2.3 wechat_config (企业微信配置表)

**表说明**: 存储企业微信Webhook配置，全局单条记录

#### 表结构

```sql
CREATE TABLE wechat_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    webhook_url TEXT NOT NULL,
    owner_user_id TEXT,
    bot_name VARCHAR(50) DEFAULT 'StockBot',
    enabled BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 字段详解

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY CHECK (id = 1) | 固定为1 | 1 |
| webhook_url | TEXT | NOT NULL | Webhook完整URL | https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx |
| owner_user_id | TEXT | - | 群主企业微信ID | ZhangSan |
| bot_name | VARCHAR(50) | DEFAULT 'StockBot' | 机器人名称 | StockPushBot |
| enabled | BOOLEAN | DEFAULT 1 | 是否启用 | true |
| created_at | DATETIME | - | 创建时间 | 2026-03-08 09:00:00 |
| updated_at | DATETIME | - | 更新时间 | 2026-03-08 10:00:00 |

#### 约束说明

- `CHECK (id = 1)`: 确保只有一条配置记录
- `TEXT`: Webhook URL可能很长

#### 使用场景

```python
# 获取当前配置
SELECT * FROM wechat_config WHERE id = 1;

# 更新配置 (REPLACE 或 UPDATE)
REPLACE INTO wechat_config (id, webhook_url, owner_user_id, bot_name) 
VALUES (1, ?, ?, ?);
```

---

### 2.4 push_strategy (推送策略配置表)

**表说明**: 推送策略参数配置，全局单条记录

#### 表结构

```sql
CREATE TABLE push_strategy (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    retry_count INTEGER DEFAULT 3,
    retry_intervals TEXT DEFAULT '[5,30,120]',
    duplicate_window_seconds INTEGER DEFAULT 3600,
    batch_enabled BOOLEAN DEFAULT 0,
    batch_interval_seconds INTEGER DEFAULT 30,
    daily_push_limit INTEGER DEFAULT 1000,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 字段详解

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY CHECK (id = 1) | 固定为1 | 1 |
| retry_count | INTEGER | DEFAULT 3 | 失败重试次数 | 3 |
| retry_intervals | TEXT | DEFAULT '[5,30,120]' | 重试间隔(秒)JSON数组 | [5,30,120] |
| duplicate_window_seconds | INTEGER | DEFAULT 3600 | 去重时间窗口(秒) | 3600 (1小时) |
| batch_enabled | BOOLEAN | DEFAULT 0 | 是否启用批量推送 | false |
| batch_interval_seconds | INTEGER | DEFAULT 30 | 批量推送间隔(秒) | 30 |
| daily_push_limit | INTEGER | DEFAULT 1000 | 每日推送上限 | 1000 |
| created_at | DATETIME | - | 创建时间 | 2026-03-08 09:00:00 |
| updated_at | DATETIME | - | 更新时间 | 2026-03-08 10:00:00 |

#### 字段说明

- `retry_intervals`: JSON格式数组，单位秒，指数退避策略
- `duplicate_window_seconds`: 同股票同价格不去重的时间窗口
- `batch_enabled`: 是否启用批量推送(多条信号攒一起推送)
- `daily_push_limit`: 防止推送泛滥，达到上限后停止推送

#### 使用场景

```python
# 获取推送策略配置
SELECT * FROM push_strategy WHERE id = 1;

# 解析重试间隔数组
import json
retry_intervals = json.loads(strategy['retry_intervals'])  # [5, 30, 120]

# 更新策略
UPDATE push_strategy 
SET retry_count = 5, duplicate_window_seconds = 1800 
WHERE id = 1;
```

---

### 2.5 system_logs (系统日志表)

**表说明**: 结构化存储系统运行日志，便于查询和分析

#### 表结构

```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level VARCHAR(10) NOT NULL,
    module VARCHAR(50),
    message TEXT NOT NULL,
    exception TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 字段详解

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 日志ID | 1 |
| level | VARCHAR(10) | NOT NULL | 日志级别 | INFO/WARNING/ERROR/CRITICAL |
| module | VARCHAR(50) | - | 模块名 | file_monitor |
| message | TEXT | NOT NULL | 日志消息 | 检测到文件变化 |
| exception | TEXT | - | 异常堆栈 | Traceback... |
| created_at | DATETIME | - | 创建时间 | 2026-03-08 10:30:30 |

#### 日志级别定义

| 级别 | 使用场景 | 示例 |
|------|---------|------|
| DEBUG | 详细调试信息 | 文件读取位置: 15200 |
| INFO | 正常业务流程 | 推送成功: 600519 |
| WARNING | 可恢复的异常 | 文件被占用，重试中 |
| ERROR | 需要关注的错误 | 推送失败: 网络超时 |
| CRITICAL | 严重错误，需立即处理 | 数据库连接失败 |

#### 索引设计

```sql
-- 按级别查询
CREATE INDEX idx_system_logs_level ON system_logs(level);

-- 按时间范围查询
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at DESC);

-- 按模块查询
CREATE INDEX idx_system_logs_module ON system_logs(module);

-- 复合索引 (级别+时间)
CREATE INDEX idx_system_logs_level_time ON system_logs(level, created_at DESC);
```

#### 日志轮转策略

```python
# 保留策略 (由应用层控制)

# 1. DEBUG/INFO日志保留7天
# 2. WARNING日志保留30天
# 3. ERROR/CRITICAL日志保留90天

# 清理SQL
delete_query = """
    DELETE FROM system_logs 
    WHERE level IN ('DEBUG', 'INFO') 
    AND created_at < datetime('now', '-7 days')
"""
```

---

## 三、数据库操作示例

### 3.1 SQLAlchemy 模型定义

```python
# models/push_record.py

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PushRecord(Base):
    __tablename__ = 'push_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(6), nullable=False)
    stock_name = Column(String(20), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    change_percent = Column(Numeric(8, 2))
    volume = Column(Integer)
    indicator = Column(String(20))
    trigger_time = Column(DateTime, nullable=False)
    file_path = Column(Text, nullable=False)
    raw_content = Column(Text, nullable=False)
    status = Column(String(20), default='pending')
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    webhook_response = Column(Text)
    wechat_message_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        # 唯一约束
        UniqueConstraint('stock_code', 'price', 'trigger_time'),
        
        # 索引
        Index('idx_push_records_trigger_time', 'trigger_time', descending=True),
        Index('idx_push_records_stock_code', 'stock_code'),
        Index('idx_push_records_status', 'status'),
        Index('idx_push_records_created_at', 'created_at', descending=True),
    )
```

### 3.2 CRUD 操作示例

```python
# database_service.py

from sqlalchemy.orm import Session
from models.push_record import PushRecord
from datetime import datetime

class DatabaseService:
    def __init__(self, session: Session):
        self.session = session
    
    def create_push_record(self, record_data: dict) -> PushRecord:
        """创建推送记录"""
        record = PushRecord(**record_data)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
    
    def get_push_record(self, record_id: int) -> Optional[PushRecord]:
        """获取单条记录"""
        return self.session.query(PushRecord).filter(PushRecord.id == record_id).first()
    
    def get_recent_pushes(self, limit: int = 10) -> List[PushRecord]:
        """获取最近推送"""
        return (self.session.query(PushRecord)
                .order_by(PushRecord.created_at.desc())
                .limit(limit)
                .all())
    
    def get_daily_stats(self, date: datetime.date) -> dict:
        """获取日统计"""
        result = (self.session.query(
            func.count(PushRecord.id).label('total'),
            func.sum(case((PushRecord.status == 'success', 1), else_=0)).label('success'),
            func.sum(case((PushRecord.status == 'failed', 1), else_=0)).label('failed')
        ).filter(
            func.date(PushRecord.created_at) == date
        ).first())
        
        return {
            'total': result.total or 0,
            'success': result.success or 0,
            'failed': result.failed or 0,
            'success_rate': (result.success or 0) / (result.total or 1)
        }
```

---

## 四、数据库迁移 (Alembic)

### 4.1 初始化迁移

```bash
# 安装Alembic
pip install alembic

# 初始化
alembic init alembic

# 配置alembic.ini
sqlalchemy.url = sqlite:///./data/push_stock.db
```

### 4.2 生成迁移脚本

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "Initial tables"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 五、备份与恢复

### 5.1 备份策略

```python
# backup_db.py

import sqlite3
import shutil
from datetime import datetime

def backup_database():
    db_path = './data/push_stock.db'
    backup_dir = './backup'
    
    # 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{backup_dir}/push_stock_{timestamp}.db'
    
    # 执行备份
    shutil.copy2(db_path, backup_path)
    
    # 压缩备份
    shutil.make_archive(backup_path.replace('.db', ''), 'zip', backup_dir, 
                       f'push_stock_{timestamp}.db')
    
    # 删除过期备份 (保留30天)
    cleanup_old_backups(backup_dir, days=30)
```

### 5.2 恢复数据

```bash
# 停止服务
sc stop PushStockService

# 恢复备份
sqlite3 push_stock.db < backup_20260308.sql

# 或复制备份文件
cp backup/push_stock_20260308.db data/push_stock.db

# 启动服务
sc start PushStockService
```

---

## 六、性能优化

### 6.1 查询优化技巧

```sql
-- 1. 使用索引覆盖查询
SELECT stock_code, stock_name, price 
FROM push_records 
WHERE trigger_time BETWEEN '2026-03-01' AND '2026-03-08'
ORDER BY trigger_time DESC;

-- 2. 避免SELECT *
-- 错误: SELECT * FROM push_records WHERE ...
-- 正确: SELECT id, stock_code, price FROM push_records WHERE ...

-- 3. 使用分页查询
SELECT * FROM push_records 
ORDER BY created_at DESC 
LIMIT 20 OFFSET 0;  -- 第1页

-- 4. 使用EXISTS代替IN
-- 错误: SELECT * FROM push_records WHERE stock_code IN (SELECT code FROM ...)
-- 正确: SELECT * FROM push_records p WHERE EXISTS (SELECT 1 FROM ... WHERE code = p.stock_code)
```

### 6.2 慢查询日志

```python
# 启用SQLite慢查询日志
import logging

# SQLAlchemy查询日志
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 输出格式
# INFO:sqlalchemy.engine.Engine:SELECT * FROM push_records WHERE ...
# INFO:sqlalchemy.engine.Engine:[generated in 0.00234s]
```

---

## 七、监控与维护

### 7.1 数据库健康检查

```python
# 检查数据库完整性
def check_database_integrity():
    conn = sqlite3.connect('data/push_stock.db')
    cursor = conn.cursor()
    
    # 检查数据库完整性
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()
    
    if result[0] == 'ok':
        print("✅ 数据库完整性检查通过")
    else:
        print("❌ 数据库损坏:", result[0])
    
    # 检查数据库大小
    cursor.execute("SELECT page_count * page_size / 1024 / 1024 FROM pragma_page_count(), pragma_page_size();")
    size_mb = cursor.fetchone()[0]
    print(f"数据库大小: {size_mb:.2f} MB")
    
    conn.close()
```

### 7.2 清理过期数据

```python
# 保留90天数据
def cleanup_old_data():
    cutoff_date = datetime.now() - timedelta(days=90)
    
    # 删除旧推送记录
    deleted = session.query(PushRecord).filter(
        PushRecord.created_at < cutoff_date
    ).delete()
    
    # 删除旧日志
    deleted_logs = session.query(SystemLog).filter(
        SystemLog.created_at < cutoff_date
    ).delete()
    
    session.commit()
    
    print(f"清理完成: {deleted} 条推送记录, {deleted_logs} 条日志")
```

---

## 八、版本历史

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-03-08 | 初始版本，完整数据库设计 | OpenCode AI |

---

**说明:**

- 所有时间字段使用 UTC 或本地时间 (需统一)
- 定期备份数据库 (建议每天)
- 监控数据库大小 (超过1GB需关注)
- 定期重建索引 (每月) 提升性能
