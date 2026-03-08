# Push_Stock 项目状态文档

**最后更新**: 2026-03-08  
**当前版本**: v1.0.0 (后端完成)  
**下次开发**: Phase 4 - Vue.js前端

---

## 🎯 项目概述

**Push_Stock** 是一个股票信号推送监控系统，实时监控通达信软件生成的股票信号文件，自动推送到企业微信。

### 核心功能
- 实时监控通达信生成的 `回调买.txt` 等文件
- 毫秒级文件变化检测 (Watchdog)
- 股票信号解析与验证
- 去重处理 (1小时窗口)
- 企业微信推送 (Markdown格式)
- 数据持久化 (SQLite)
- RESTful API (FastAPI)
- Windows服务部署

---

## ✅ 已完成模块 (100%)

### Phase 1: 后端核心 (Day 1-3)
```
✅ src/config.py          - Pydantic配置管理 (245行)
✅ src/logger.py          - Loguru日志系统 (154行)
✅ src/exceptions.py      - 自定义异常体系 (245行)
✅ src/constants.py       - 常量定义 (187行)
✅ src/database_service.py - CRUD服务 (494行)
✅ src/models/            - SQLAlchemy模型 (5文件, 575行)
✅ src/core/              - 核心服务 (6文件, 1,615行)
   ├── parser.py         - 股票解析器
   ├── deduplicator.py   - 去重服务
   ├── wechat_bot.py     - 微信推送
   ├── file_monitor.py   - 文件监控
   └── windows_service.py - Windows服务
```

### Phase 2: API层 (Day 4-5)
```
✅ src/api/main.py        - FastAPI应用 (95行)
✅ src/api/dependencies.py - 依赖注入 (85行)
✅ src/api/routes/        - API路由 (5文件, 415行)
   ├── dashboard.py      - Dashboard数据
   ├── config.py         - 配置管理
   ├── history.py        - 推送历史
   └── system.py         - 系统状态
```

### Phase 3: 部署 (Day 6-7)
```
✅ scripts/install_service.bat    - 服务安装
✅ scripts/uninstall_service.bat  - 服务卸载
✅ requirements.txt               - 完整依赖
✅ docs/                          - 完整文档 (4文件, 3,143行)
```

**总计**: 34个文件, ~6,000行代码

---

## ⏳ 待开发模块 (Phase 4)

### Phase 4: Vue.js前端 (预计5天)

```
⏳ web/                      - Vue 3项目根目录
   ├── package.json         - 依赖配置
   ├── vite.config.ts       - Vite配置
   ├── tsconfig.json        - TypeScript配置
   │
   ├── src/
   │   ├── main.ts          - 入口文件
   │   ├── App.vue          - 根组件
   │   │
   │   ├── views/           - 页面视图
   │   │   ├── Dashboard.vue    - 数据大盘 (Day 8-9)
   │   │   ├── Config.vue       - 配置管理 (Day 9)
   │   │   ├── History.vue      - 推送历史 (Day 10-11)
   │   │   └── System.vue       - 系统状态 (Day 11)
   │   │
   │   ├── components/      - 公共组件
   │   │   ├── dashboard/
   │   │   │   ├── PushSuccessRateChart.vue
   │   │   │   ├── StockDistributionChart.vue
   │   │   │   └── TimeDistributionChart.vue
   │   │   └── common/
   │   │       ├── Loading.vue
   │   │       └── Pagination.vue
   │   │
   │   ├── api/             - API封装
   │   │   ├── dashboard.ts
   │   │   ├── config.ts
   │   │   ├── history.ts
   │   │   └── system.ts
   │   │
   │   ├── stores/          - Pinia状态管理
   │   │   ├── dashboard.ts
   │   │   └── config.ts
   │   │
   │   ├── types/           - TypeScript类型
   │   │   ├── dashboard.ts
   │   │   ├── config.ts
   │   │   └── api.ts
   │   │
   │   └── utils/           - 工具函数
   │       └── request.ts   - Axios封装
   │
   └── index.html           - HTML模板
```

### 前端技术栈
- **框架**: Vue 3.3+ (Composition API)
- **语言**: TypeScript 5.0+
- **构建**: Vite 5.0+
- **UI库**: Element Plus 2.4+
- **图表**: ECharts 5.4+
- **状态**: Pinia 2.1+
- **HTTP**: Axios 1.6+

---

## 🚀 快速启动指南

### 环境准备
```bash
# 1. 克隆仓库
git clone https://github.com/south2014/Push_Stock.git
cd Push_Stock

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

### 配置环境变量
```bash
# 创建 .env 文件
echo WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY > .env
```

### 启动开发服务器
```bash
# 启动API服务 (带热重载)
python -m uvicorn src.api.main:app --reload

# 访问API文档
open http://localhost:8000/docs
```

### 安装Windows服务
```bash
# 以管理员身份运行
scripts\install_service.bat

# 管理命令
sc start PushStockService    # 启动服务
sc stop PushStockService     # 停止服务
sc query PushStockService    # 查询状态
```

---

## 📊 项目架构

```
Push_Stock/
│
├── 📄 文档层
│   ├── AGENTS.md              # 开发规范
│   ├── docs/architecture.md   # 系统架构
│   ├── docs/api.md            # API接口
│   ├── docs/frontend.md       # 前端设计
│   └── docs/database.md       # 数据库设计
│
├── ⚙️ 配置层
│   ├── src/config.py          # 配置管理
│   ├── src/constants.py       # 常量定义
│   ├── src/exceptions.py      # 异常体系
│   └── src/logger.py          # 日志系统
│
├── 💾 数据层
│   ├── src/models/            # SQLAlchemy模型
│   └── src/database_service.py # CRUD服务
│
├── 🔧 服务层
│   └── src/core/              # 核心业务逻辑
│       ├── parser.py          # 股票解析
│       ├── deduplicator.py    # 去重服务
│       ├── wechat_bot.py      # 微信推送
│       ├── file_monitor.py    # 文件监控
│       └── windows_service.py # Windows服务
│
├── 🌐 API层
│   └── src/api/               # FastAPI接口
│       ├── main.py
│       ├── dependencies.py
│       └── routes/
│
├── 🎨 前端层 (待开发)
│   └── web/                   # Vue 3项目
│
├── 🔨 部署脚本
│   ├── scripts/install_service.bat
│   └── scripts/uninstall_service.bat
│
└── 📦 依赖配置
    └── requirements.txt
```

---

## 🔧 继续开发指南

### 场景1: 开发Vue前端
```bash
# 1. 进入前端目录
mkdir web && cd web

# 2. 初始化Vue项目
npm create vue@latest .
# 选择: TypeScript, Pinia, Router

# 3. 安装依赖
npm install element-plus echarts axios

# 4. 启动开发服务器
npm run dev
```

### 场景2: 后端功能扩展
```python
# 在 src/core/ 添加新模块
# 在 src/api/routes/ 添加新接口
# 遵循现有代码风格 (50行函数限制)
```

### 场景3: 修复Bug
```bash
# 1. 创建分支
git checkout -b fix/bug-description

# 2. 修改代码
# ...

# 3. 测试
python -m pytest tests/

# 4. 提交
git add .
git commit -m "fix: description"
git push origin fix/bug-description
```

---

## 📋 检查清单

### 启动开发前检查
- [ ] Python 3.11+ 已安装
- [ ] 虚拟环境已激活
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] `.env` 文件已配置 (WECHAT_WEBHOOK_URL)
- [ ] 数据库目录可写入 (`data/`)
- [ ] 日志目录可写入 (`logs/`)

### 代码提交前检查
- [ ] 代码符合PEP 8规范
- [ ] 类型注解完整
- [ ] 函数行数 ≤ 50行
- [ ] 无敏感信息泄露
- [ ] 提交信息规范 (feat/fix/docs)

---

## 🐛 常见问题

### Q1: 导入错误 (pydantic/sqlalchemy/loguru)
**解决**: 依赖未安装
```bash
pip install -r requirements.txt
```

### Q2: 数据库连接失败
**解决**: 检查data目录权限
```bash
mkdir -p data logs
# 确保目录可写入
```

### Q3: 微信推送失败
**解决**: 检查Webhook URL
```bash
# 测试Webhook
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"msgtype": "text", "text": {"content": "test"}}'
```

### Q4: Windows服务无法安装
**解决**: 以管理员身份运行CMD
```bash
# 右键点击CMD -> 以管理员身份运行
scripts\install_service.bat
```

---

## 🔗 关键配置

### 环境变量 (.env)
```bash
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
WECHAT_OWNER_USER_ID=YourUserID

MONITOR_BASE_PATH=C:\Users\ckyto\Desktop
MONITOR_FILES=回调买.txt,反弹卖.txt

DATABASE_PATH=./data/push_stock.db
LOG_LEVEL=INFO

RETRY_COUNT=3
DUPLICATE_WINDOW=3600

API_HOST=127.0.0.1
API_PORT=8000
```

### 文件格式 (通达信输出)
```
600176	中国巨石	2026-03-02 11:21	28.10	 3.92%	69	BBIHTM_G
300861	美畅股份	2026-03-02 13:19	18.78	-1.26%	15	BBIHTM_G
```

---

## 📈 项目统计

| 类别 | 数量 | 说明 |
|------|------|------|
| Python文件 | 27个 | 后端代码 |
| 文档文件 | 4个 | 设计文档 |
| 脚本文件 | 2个 | 部署脚本 |
| 总代码行 | ~6,000行 | 不含注释 |
| 测试覆盖率 | 待补充 | 需要补充单元测试 |

---

## 🎯 下一步计划

### 优先级1: 前端开发
- [ ] Vue 3项目初始化
- [ ] Dashboard数据大盘
- [ ] 配置管理界面
- [ ] 推送历史页面

### 优先级2: 测试完善
- [ ] 单元测试 (pytest)
- [ ] 集成测试
- [ ] 性能测试

### 优先级3: 功能增强
- [ ] 多推送渠道 (邮件/钉钉)
- [ ] 策略回测
- [ ] 移动端适配

---

## 👨‍💻 开发者信息

**项目**: Push_Stock  
**作者**: south2014  
**技术栈**: Python + FastAPI + Vue.js + SQLite  
**协议**: MIT  

**开发规范**:
- 函数行数 ≤ 50行
- 参数个数 ≤ 5个
- 类型注解覆盖率 100%
- 文档覆盖率 100%

---

## 📝 更新日志

### v1.0.0 (2026-03-08)
- ✅ 后端核心功能完成
- ✅ API接口完成
- ✅ Windows服务部署
- ✅ 完整文档
- ⏳ Vue前端 (待开发)

---

**下次启动时请阅读本文件恢复开发上下文**
