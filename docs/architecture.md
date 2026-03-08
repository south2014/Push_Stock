# Push_Stock 系统架构设计文档

**版本**: v1.0  
**制定日期**: 2026-03-08  
**状态**: 已确认

---

## 一、系统架构总览

### 1.1 技术栈选型

| 模块 | 技术 | 版本 | 理由 |
|------|------|------|------|
| 后端框架 | FastAPI | 0.104+ | 高性能异步支持、自动生成API文档 |
| 前端框架 | Vue 3 | 3.3+ | 易学易用、TypeScript友好、生态完善 |
| 数据库 | SQLite | 3.40+ | 零配置、文件存储、适合桌面应用 |
| 文件监控 | Watchdog | 3.0+ | 系统级事件通知、毫秒级响应 |
| Windows服务 | PyWin32 | 306+ | 原生Windows API支持 |
| 日志系统 | Loguru | 0.7+ | 结构化日志、异步写入、自动轮转 |
| 配置管理 | Pydantic | 2.5+ | 类型安全、数据验证 |
| 进程守护 | 自建 | - | 轻量、可监控内存CPU |

### 1.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层 (User)                            │
│         (通达信软件 → Desktop文件 → 企业微信 → Web管理后台)        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                      前端层 (Vue 3)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │  Config  │  │ History  │  │  System  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
┌───────▼─────────────▼─────────────▼─────────────▼──────────────┐
│                  API网关 (FastAPI)                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Config API│  │History API│  │Dashboard API│  │System API│   │
│  └────┬─────┘  └────┬─────┘  └────┬───────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼───────────────┼─────────────┘
        │             │             │               │
┌───────▼─────────────▼─────────────▼───────────────▼─────────────┐
│                    服务层 (Services)                             │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  FileMonitorService  Watchdog实时文件监听              │     │
│  │  ParserService       股票信号解析                     │     │
│  │  WeChatBotService    企业微信推送                     │     │
│  │  DatabaseService     SQLite持久化                    │     │
│  │  LoggerService       结构化日志                       │     │
│  └───────────────────────────────────────────────────────┘     │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                  数据层 (SQLite)                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ push_records    │  │ monitor_files   │  │ system_configs  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 1.3 核心技术挑战与应对策略

| 挑战点 | 风险等级 | 应对方案 | 监控指标 |
|--------|---------|---------|---------|
| 文件监控漏检 | 🔴 高 | Watchdog + 10秒兜底轮询 | monitor_missed_events |
| 重复推送 | 🟡 中 | SQLite去重窗口 + 哈希校验 | duplicate_detected_total |
| Windows服务崩溃 | 🔴 高 | 进程守护 + 自动重启 + 内存监控 | service_restart_total |
| 企业微信限流 | 🟡 中 | 批量推送 + 指数退避重试 | wechat_rate_limited_total |
| 配置安全性 | 🔴 高 | 环境变量 + 敏感信息加密 | config_security_check |

---

## 二、项目目录结构 (共42个文件)

```
Push_Stock/
├── .env.example              # 环境变量模板 (不提交到Git)
├── .gitignore               # Git忽略配置
├── AGENTS.md               # 开发规范
├── GIT_SETUP_COMMANDS.md    # Git配置指南
├── README.md               # 项目说明
├── requirements.txt          # Python依赖
├── requirements-dev.txt     # 开发依赖
├── pytest.ini              # pytest配置
├── alembic.ini             # 数据库迁移配置
├── alembic/               # 数据库迁移脚本
│   ├── env.py
│   └── versions/
├── tests/                  # 测试目录
│   ├── __init__.py
│   ├── conftest.py        # pytest全局配置
│   ├── unit/              # 单元测试
│   │   ├── test_file_monitor.py
│   │   ├── test_parser.py
│   │   ├── test_wechat_bot.py
│   │   └── test_database.py
│   └── integration/       # 集成测试
│       ├── test_e2e_flow.py
│       └── test_windows_service.py
├── docs/                   # 文档
│   ├── architecture.md    # 系统架构
│   ├── api.md             # API接口
│   ├── frontend.md        # 前端设计
│   └── database.md        # 数据库设计
├── scripts/               # 脚本
│   ├── install_service.bat # Windows服务安装脚本
│   └── backup_db.bat      # 数据库备份脚本
└── src/                   # 源代码
    ├── __init__.py
    ├── main.py            # 程序入口 (CLI)
    ├── config.py          # 配置管理 (Pydantic)
    ├── exceptions.py      # 自定义异常类
    ├── logger.py          # 日志配置
    ├── constants.py       # 常量定义
    ├── core/              # 核心业务逻辑
    │   ├── __init__.py
    │   ├── file_monitor.py    # 文件监控 (Watchdog)
    │   ├── parser.py          # 股票解析
    │   ├── deduplicator.py    # 去重服务
    │   ├── wechat_bot.py      # 企业微信推送
    │   ├── database_service.py # SQLite操作封装
    │   └── windows_service.py # Windows服务包装
    ├── models/            # 数据模型 (SQLAlchemy)
    │   ├── __init__.py
    │   ├── base.py
    │   ├── push_record.py
    │   ├── monitor_file.py
    │   └── system_config.py
    ├── api/               # FastAPI接口
    │   ├── __init__.py
    │   ├── main.py        # FastAPI应用入口
    │   ├── dependencies.py # 依赖注入
    │   └── routes/
    │       ├── __init__.py
    │       ├── dashboard.py
    │       ├── config.py
    │       ├── history.py
    │       └── system.py
    ├── services/          # 服务层
    │   ├── __init__.py
    │   ├── monitor_service.py    # 监控服务管理
    │   └── scheduler_service.py  # 定时任务
    └── utils/             # 工具函数
        ├── __init__.py
        ├── hash.py        # SHA256哈希
        ├── date.py        # 日期格式化
        └── retry.py       # 重试装饰器
```

---

## 三、数据库设计

### 3.1 SQLite数据库配置

**数据库文件**: `data/push_stock.db`

```sql
-- 推送记录表
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

-- 监控文件配置表
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

-- 企业微信配置表
CREATE TABLE wechat_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    webhook_url TEXT NOT NULL,
    owner_user_id TEXT,
    bot_name VARCHAR(50) DEFAULT 'StockBot',
    enabled BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 推送策略配置表
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

-- 系统日志表
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level VARCHAR(10) NOT NULL,
    module VARCHAR(50),
    message TEXT NOT NULL,
    exception TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX idx_push_records_trigger_time ON push_records(trigger_time DESC);
CREATE INDEX idx_push_records_stock_code ON push_records(stock_code);
CREATE INDEX idx_push_records_status ON push_records(status);
CREATE INDEX idx_push_records_created_at ON push_records(created_at DESC);
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at DESC);
```

### 3.2 数据字典

#### push_records (推送记录表)

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| id | INTEGER | 主键，自增 | 1001 |
| stock_code | VARCHAR(6) | 股票代码 | 600519 |
| stock_name | VARCHAR(20) | 股票名称 | 贵州茅台 |
| price | DECIMAL(10,2) | 触发价格 | 1680.50 |
| change_percent | DECIMAL(8,2) | 涨跌幅(%) | 3.92 |
| volume | INTEGER | 成交量(手) | 1250 |
| indicator | VARCHAR(20) | 指标标识 | BBIHTM_G |
| trigger_time | DATETIME | 触发时间 | 2026-03-08 10:30:25 |
| file_path | TEXT | 监控文件路径 | C:\\...\\回调买.txt |
| raw_content | TEXT | 原始文件行内容 | 600519\\t贵州茅台\\t... |
| status | VARCHAR(20) | 推送状态 | success/failed/pending |
| error_message | TEXT | 错误信息 | 网络超时 |
| retry_count | INTEGER | 已重试次数 | 0 |
| webhook_response | TEXT | 微信响应 | {"errcode":0,...} |
| wechat_message_id | VARCHAR(100) | 消息ID | undefined |
| created_at | DATETIME | 创建时间 | 2026-03-08 10:30:30 |
| updated_at | DATETIME | 更新时间 | 2026-03-08 10:31:00 |

---

## 四、性能与监控

### 4.1 性能指标要求

| 指标 | 目标值 | 监控方式 | 告警策略 |
|------|--------|---------|---------|
| 监控延迟 | <100ms | Watchdog事件 | >200ms警告 |
| 推送延迟 | <500ms | 时间戳差值 | >1000ms警告 |
| 成功率 | >99% | 统计计算 | <95%严重 |
| 错误率 | <0.1% | 错误计数 | >1%严重 |
| 内存占用 | <500MB | psutil | >800MB重启 |
| CPU占用 | <70% | psutil | >80%持续5分钟警告 |

### 4.2 Prometheus指标设计

```python
# 监控指标 (metrics.py)

monitor_file_changes_total = Counter(
    'monitor_file_changes_total',
    '文件变化总次数',
    ['file_path', 'status']
)

monitor_signals_parsed_total = Counter(
    'monitor_signals_parsed_total',
    '解析信号总数',
    ['file_path', 'status']
)

monitor_signals_duplicate_total = Counter(
    'monitor_signals_duplicate_total',
    '去重信号数',
    ['file_path', 'stock_code']
)

push_wechat_total = Counter(
    'push_wechat_total',
    '企业微信推送总数',
    ['status', 'retry_count']
)

push_latency_seconds = Histogram(
    'push_latency_seconds',
    '推送延迟 (文件变化到推送成功)',
    buckets=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

database_operations_total = Counter(
    'database_operations_total',
    '数据库操作次数',
    ['operation', 'table', 'status']
)

system_memory_mb = Gauge(
    'system_memory_mb',
    '系统内存使用 (MB)'
)

system_cpu_percent = Gauge(
    'system_cpu_percent',
    '系统CPU使用率 (%)'
)
```

---

## 五、日志策略

### 5.1 日志级别定义

| 级别 | 使用场景 | 示例 |
|------|---------|------|
| DEBUG | 开发调试信息 | 文件读取位置、解析字段 |
| INFO | 正常业务流程 | 推送成功、监控开始 |
| WARNING | 可恢复的异常 | 文件暂时被占用、重试 |
| ERROR | 需要关注的错误 | 推送失败、解析失败 |
| CRITICAL | 严重错误需立即处理 | 数据库连接失败、服务崩溃 |

### 5.2 日志轮转配置

```python
# logger.py

logger.add(
    "logs/app.log",
    rotation="500 MB",          # 500MB轮转
    retention="10 days",        # 保留10天
    compression="zip",          # 压缩旧日志
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:8} | {module}:{function}:{line} | {message}",
    enqueue=True                # 异步写入
)

logger.add(
    "logs/error.log",
    rotation="100 MB",
    retention="30 days",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:8} | {module}:{function}:{line} | {message}\n{exception}",
    enqueue=True
)
```

---

## 六、部署方案

### 6.1 Windows服务部署

**安装服务**:
```batch
:: install_service.bat

@echo off
set SERVICE_NAME=PushStockService
set DISPLAY_NAME=Push Stock Monitor Service
set DESCRIPTION=监控通达信股票信号并推送到企业微信
set PYTHON_PATH=%~dp0venv\\Scripts\\python.exe
set SCRIPT_PATH=%~dp0src\\windows_service.py

%PYTHON_PATH% %SCRIPT_PATH% install
sc config %SERVICE_NAME% start= auto
sc description %SERVICE_NAME% %DESCRIPTION%

echo 服务安装完成！
echo 启动服务: sc start %SERVICE_NAME%
echo 停止服务: sc stop %SERVICE_NAME%
echo 卸载服务: %PYTHON_PATH% %SCRIPT_PATH% remove
pause
```

**卸载服务**:
```batch
:: uninstall_service.bat

@echo off
set PYTHON_PATH=%~dp0venv\\Scripts\\python.exe
set SCRIPT_PATH=%~dp0src\\windows_service.py

%PYTHON_PATH% %SCRIPT_PATH% remove
echo 服务已卸载！
pause
```

### 6.2 开机自启设置

**任务计划程序方式** (推荐):
```batch
:: 创建开机自启任务
schtasks /create /tn "PushStockMonitor" /tr "F:\\Push_Stock\\start_service.bat" /sc onstart /ru SYSTEM
```

---

## 七、故障恢复策略

### 7.1 进程守护机制

```python
# core\windows_service.py

class ProcessGuard:
    """进程守护 - 监控内存和CPU"""
    
    def __init__(self):
        self.memory_limit = 500 * 1024 * 1024  # 500MB
        self.cpu_threshold = 80.0  # 80%
        self.check_interval = 60  # 60秒
        
    async def start_monitoring(self):
        """开始监控进程"""
        while True:
            memory = psutil.Process().memory_info().rss
            cpu = psutil.Process().cpu_percent()
            
            if memory > self.memory_limit:
                logger.critical(f"内存超限: {memory//1024//1024}MB > 500MB，将重启服务")
                self.restart_service()
                
            if cpu > self.cpu_threshold:
                logger.warning(f"CPU过高: {cpu}% > 80%")
                
            await asyncio.sleep(self.check_interval)
    
    def restart_service(self):
        """重启服务"""
        # Windows服务重启
        os.system("sc stop PushStockService")
        time.sleep(5)
        os.system("sc start PushStockService")
```

### 7.2 异常恢复矩阵

| 异常类型 | 检测方式 | 恢复策略 | 恢复时间 |
|---------|---------|----------|---------|
| Watchdog崩溃 | 心跳检测 | 重启监控线程 | <5秒 |
| 数据库锁 | 异常捕获 | 重试3次，间隔1秒 | <3秒 |
| 企业微信API失败 | HTTP错误码 | 指数退避重试 | 最大2分钟 |
| 文件被占用 | IOError | 等待100ms重试，最多3次 | <300ms |
| 内存泄漏 | 定时监控 | 重启服务 | <10秒 |
| CPU死循环 | 定时监控 | 记录dump，重启服务 | <10秒 |

---

## 八、测试策略

### 8.1 单元测试 (覆盖率>95%)

```python
# tests/unit/test_file_monitor.py

class TestFileMonitor:
    """文件监控单元测试"""
    
    def test_should_detect_file_change(self, tmp_path):
        ""'应能检测到文件变化'"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("")
        
        # 模拟文件变化
        callback_called = []
        def callback(content):
            callback_called.append(content)
        
        monitor = FileMonitor(test_file, callback)
        monitor.start()
        
        # 写入新内容
        test_file.write_text("600519\\t贵州茅台\\t10:30\\t1680.50")
        time.sleep(0.2)
        
        assert len(callback_called) == 1
        assert "600519" in callback_called[0]
    
    def test_should_ignore_duplicate_writes(self, tmp_path):
        ""'相同内容不应重复触发'"""
        # 测试去重逻辑
        pass
    
    def test_should_handle_file_not_found(self, tmp_path):
        ""'文件不存在时应记录错误不崩溃'"""
        # 测试容错性
        pass
```

### 8.2 集成测试

```python
# tests/integration/test_e2e_flow.py

class TestEndToEndFlow:
    """端到端集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_flow_from_file_to_wechat(self):
        """
        完整流程测试:
        通达信写入 → 文件监控 → 解析 → 去重 → 推送 → 存储
        """
        # 1. 创建测试文件
        # 2. 写入股票信号
        # 3. 等待监控检测
        # 4. 验证解析结果
        # 5. 验证去重逻辑
        # 6. Mock企业微信API
        # 7. 验证推送调用
        # 8. 验证数据库写入
        pass
```

### 8.3 性能测试目标

```bash
# 测试场景

1. 文件监控延迟测试
   - 写入1000条数据
   - 测量平均检测延迟
   - 目标: <100ms

2. 推送吞吐量测试
   - 模拟100条/秒并发
   - 测量成功率
   - 目标: >99.9%

3. 数据库压力测试
   - 10000条记录查询
   - 测量查询时间
   - 目标: <100ms
```

---

## 九、版本规划

### v1.0 (当前版本)
- [x] 文件实时监控 (Watchdog)
- [x] 股票信号解析
- [x] 企业微信推送
- [x] SQLite持久化
- [x] 日志系统
- [x] 去重策略
- [x] 失败重试
- [x] FastAPI基础接口

### v1.1 (2周后)
- [ ] Web管理后台 (Vue 3)
- [ ] Dashboard数据大盘
- [ ] 配置管理界面
- [ ] 推送历史查询

### v1.2 (4周后)
- [ ] 多推送渠道 (邮件、钉钉)
- [ ] 策略回测功能
- [ ] 股票基础信息库
- [ ] 移动端适配

### v1.3 (6周后)
- [ ] 多用户支持
- [ ] 权限管理
- [ ] 云端部署方案
- [ ] 自动化部署CI/CD

---

## 十、项目规范

### 10.1 Git提交规范

```bash
# 格式: type(scope): description

feat(file_monitor): 添加Watchdog文件监控
# 新功能

fix(parser): 修复涨跌幅解析错误
# Bug修复

docs(api): 更新API接口文档
# 文档更新

style(config): 统一代码格式化
# 代码格式调整

test(wechat): 添加企业微信推送测试
# 测试代码

refactor(database): 优化查询性能
# 重构
```

### 10.2 代码审查清单

```markdown
PR提交前检查清单:

- [ ] 代码符合PEP 8规范 (Black格式化)
- [ ] 类型注解覆盖率100% (mypy检查)
- [ ] 单元测试覆盖率>95% (pytest-cov)
- [ ] 所有测试通过 (pytest)
- [ ] 无flake8警告和错误
- [ ] 函数行数≤50行
- [ ] 参数个数≤5个
- [ ] 有完整的docstring
- [ ] 异常处理精确到具体异常类型
- [ ] 敏感信息未硬编码
- [ ] 更新相关文档
```

---

**文档修订历史:**
- v1.0 (2026-03-08): 初始版本，完整架构设计

**维护者:** OpenCode AI
