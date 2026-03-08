# Push_Stock API接口设计文档

**版本**: v1.0  
**制定日期**: 2026-03-08  
**状态**: 已确认

---

## 一、接口总览

### 1.1 技术规范

- **框架**: FastAPI 0.104.1
- **协议**: HTTP/1.1, HTTP/2
- **数据格式**: JSON (application/json)
- **认证方式**: 无认证 (内网部署，后续可添加JWT)
- **API前缀**: `/api`
- **文档**: Swagger UI (自动生成)

### 1.2 API文档访问

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 二、Dashboard API (数据大盘)

### 2.1 获取大盘摘要

```http
GET /api/dashboard/summary
```

**请求参数**: 无

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "today_total": 124,
    "today_success": 121,
    "today_failed": 3,
    "success_rate": "97.58%",
    "monitor_status": "running",
    "uptime": "2天3小时15分钟",
    "last_push_time": "2026-03-08 10:30:25"
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| today_total | int | 今日推送总数 | 124 |
| today_success | int | 今日成功数 | 121 |
| today_failed | int | 今日失败数 | 3 |
| success_rate | string | 成功率(%) | "97.58%" |
| monitor_status | string | 监控状态 | running/stopped/error |
| uptime | string | 运行时间 | "2天3小时15分钟" |
| last_push_time | string | 最后推送时间 | "2026-03-08 10:30:25" |

**可能的错误**:

| HTTP状态码 | 错误码 | 说明 |
|-----------|--------|------|
| 500 | -1 | 数据库查询失败 |

---

### 2.2 获取成功率趋势

```http
GET /api/dashboard/success-rate-trend?days=7
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| days | int | 否 | 7 | 天数 (1-365) |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "date": "2026-03-01",
        "success_count": 145,
        "failed_count": 2,
        "success_rate": 0.986
      },
      {
        "date": "2026-03-02",
        "success_count": 132,
        "failed_count": 5,
        "success_rate": 0.964
      }
    ],
    "total": 7
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| date | string | 日期 | "2026-03-01" |
| success_count | int | 成功数 | 145 |
| failed_count | int | 失败数 | 2 |
| success_rate | float | 成功率(0-1) | 0.986 |

**ECharts配置示例**:

```javascript
// 成功率趋势图 (折线图)
option = {
  title: { text: '推送成功率趋势' },
  xAxis: {
    type: 'category',
    data: response.data.list.map(item => item.date)
  },
  yAxis: { type: 'value', min: 0, max: 1 },
  series: [{
    data: response.data.list.map(item => item.success_rate),
    type: 'line',
    smooth: true
  }]
}
```

---

### 2.3 获取股票分布TOP20

```http
GET /api/dashboard/stock-distribution?days=30&limit=20
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| days | int | 否 | 30 | 统计天数 (1-365) |
| limit | int | 否 | 20 | 返回数量 (1-100) |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "code": "600519",
        "name": "贵州茅台",
        "count": 15,
        "percentage": 12.1
      },
      {
        "code": "000858",
        "name": "五粮液",
        "count": 12,
        "percentage": 9.7
      }
    ],
    "total": 20
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| code | string | 股票代码 | "600519" |
| name | string | 股票名称 | "贵州茅台" |
| count | int | 触发次数 | 15 |
| percentage | float | 占比(%) | 12.1 |

**ECharts配置示例**:

```javascript
// 股票分布饼图
option = {
  title: { text: '股票触发分布' },
  series: [{
    type: 'pie',
    radius: '50%',
    data: response.data.list.map(item => ({
      value: item.count,
      name: `${item.code} ${item.name}`
    }))
  }]
}
```

---

### 2.4 获取时间分布热力图

```http
GET /api/dashboard/time-distribution?days=7
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| days | int | 否 | 7 | 天数 (1-365) |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "hours": ["09:00", "10:00", "11:00", "13:00", "14:00"],
    "days": ["周一", "周二", "周三", "周四", "周五"],
    "data": [
      [0, 0, 5], [0, 1, 8], [0, 2, 12],
      [1, 0, 15], [1, 1, 20], [1, 2, 18],
      [2, 0, 10], [2, 1, 25], [2, 2, 30]
    ]
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| hours | array | 时间维度(小时) | ["09:00", "10:00"] |
| days | array | 日期维度(星期) | ["周一", "周二"] |
| data | array | 热力图数据(二维数组) | [[时间索引, 日期索引, 值]] |

**ECharts配置示例**:

```javascript
// 时间分布热力图
option = {
  title: { text: '推送时间分布热力图' },
  xAxis: {
    type: 'category',
    data: response.data.hours
  },
  yAxis: {
    type: 'category',
    data: response.data.days
  },
  series: [{
    type: 'heatmap',
    data: response.data.data.map(item => [item[1], item[0], item[2]]),
    label: {
      show: true
    }
  }]
}
```

---

### 2.5 获取最近推送记录

```http
GET /api/dashboard/recent-pushes?limit=10
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| limit | int | 否 | 10 | 返回数量 (1-100) |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1234,
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "price": 1680.50,
        "change_percent": 3.92,
        "trigger_time": "2026-03-08 10:30:25",
        "file_path": "C:\\Users\\ckyto\\Desktop\\回调买.txt",
        "status": "success",
        "created_at": "2026-03-08 10:30:30"
      }
    ],
    "total": 10
  }
}
```

---

## 三、Config API (配置管理)

### 3.1 获取文件监控配置列表

```http
GET /api/config/file-monitors
```

**请求参数**: 无

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "file_path": "C:\\Users\\ckyto\\Desktop\\回调买.txt",
      "enabled": true,
      "description": "回调买入策略",
      "created_at": "2026-03-08 09:00:00",
      "updated_at": "2026-03-08 10:00:00"
    }
  ]
}
```

---

### 3.2 添加/更新文件监控配置

```http
POST /api/config/file-monitors
```

**请求体**:

```json
{
  "file_path": "C:\\Users\\ckyto\\Desktop\\回调买.txt",
  "enabled": true,
  "description": "回调买入策略"
}
```

**响应示例** (新增):

```json
{
  "code": 0,
  "message": "创建成功",
  "data": {
    "id": 2,
    "file_path": "C:\\Users\\ckyto\\Desktop\\回调买.txt",
    "enabled": true,
    "description": "回调买入策略",
    "created_at": "2026-03-08 11:00:00",
    "updated_at": "2026-03-08 11:00:00"
  }
}
```

**响应示例** (更新):

```http
PUT /api/config/file-monitors/2
```

```json
{
  "code": 0,
  "message": "更新成功",
  "data": {
    "id": 2,
    "file_path": "C:\\Users\\ckyto\\Desktop\\回调买.txt",
    "enabled": false,
    "description": "回调买入策略(已暂停)",
    "created_at": "2026-03-08 11:00:00",
    "updated_at": "2026-03-08 12:00:00"
  }
}
```

---

### 3.3 删除文件监控配置

```http
DELETE /api/config/file-monitors/2
```

**响应示例**:

```json
{
  "code": 0,
  "message": "删除成功"
}
```

---

### 3.4 获取企业微信配置

```http
GET /api/config/wechat
```

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
    "owner_user_id": "ZhangSan",
    "bot_name": "StockBot",
    "enabled": true
  }
}
```

---

### 3.5 更新企业微信配置

```http
PUT /api/config/wechat
```

**请求体**:

```json
{
  "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=NEW_KEY",
  "owner_user_id": "ZhangSan",
  "bot_name": "StockBot",
  "enabled": true
}
```

**响应示例**:

```json
{
  "code": 0,
  "message": "更新成功",
  "data": {
    "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=NEW_KEY",
    "owner_user_id": "ZhangSan",
    "bot_name": "StockBot",
    "enabled": true
  }
}
```

---

### 3.6 测试企业微信Webhook连通性

```http
POST /api/config/wechat/test
```

**请求体**: 无

**响应示例** (成功):

```json
{
  "code": 0,
  "message": "测试消息发送成功",
  "data": {
    "success": true,
    "response": {
      "errcode": 0,
      "errmsg": "ok"
    }
  }
}
```

**响应示例** (失败):

```json
{
  "code": -1,
  "message": "测试消息发送失败: 网络超时",
  "data": {
    "success": false,
    "error": "网络超时"
  }
}
```

---

### 3.7 获取推送策略配置

```http
GET /api/config/push-strategy
```

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "retry_count": 3,
    "retry_intervals": [5, 30, 120],
    "duplicate_window_seconds": 3600,
    "batch_enabled": false,
    "batch_interval_seconds": 30,
    "daily_push_limit": 1000
  }
}
```

**字段说明**:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| retry_count | int | 失败重试次数 | 3 |
| retry_intervals | array | 重试间隔(秒) | [5, 30, 120] |
| duplicate_window_seconds | int | 去重时间窗口 | 3600 (1小时) |
| batch_enabled | boolean | 是否启用批量推送 | false |
| batch_interval_seconds | int | 批量推送间隔 | 30 |
| daily_push_limit | int | 每日推送上限 | 1000 |

---

### 3.8 更新推送策略配置

```http
PUT /api/config/push-strategy
```

**请求体**:

```json
{
  "retry_count": 5,
  "retry_intervals": [5, 30, 120, 300, 600],
  "duplicate_window_seconds": 1800,
  "batch_enabled": true,
  "batch_interval_seconds": 60,
  "daily_push_limit": 2000
}
```

**响应示例**:

```json
{
  "code": 0,
  "message": "更新成功",
  "data": {
    "retry_count": 5,
    "retry_intervals": [5, 30, 120, 300, 600],
    "duplicate_window_seconds": 1800,
    "batch_enabled": true,
  "batch_interval_seconds": 60,
  "daily_push_limit": 2000
  }
}
```

---

## 四、History API (推送历史)

### 4.1 获取推送历史列表 (分页+筛选)

```http
GET /api/history/pushes?page=1&page_size=20&stock_code=&status=&start_date=&end_date=&file_id=
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | int | 否 | 1 | 页码 (≥1) |
| page_size | int | 否 | 20 | 每页数量 (1-100) |
| stock_code | string | 否 | - | 股票代码筛选 |
| status | string | 否 | - | 状态筛选 (success/failed/pending) |
| start_date | string | 否 | - | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | - | 结束日期 (YYYY-MM-DD) |
| file_id | int | 否 | - | 监控文件ID |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1234,
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "price": 1680.50,
        "change_percent": 3.92,
        "volume": 1250,
        "indicator": "BBIHTM_G",
        "trigger_time": "2026-03-08 10:30:25",
        "file_path": "C:\\Users\\ckyto\\Desktop\\回调买.txt",
        "raw_content": "600519\\t贵州茅台\\t2026-03-08 10:30\\t1680.50\\t+3.92%\\t1250\\tBBIHTM_G",
        "status": "success",
        "error_message": null,
        "retry_count": 0,
        "webhook_response": "{\\"errcode\\":0,\\"errmsg\\":\\"ok\\"}",
        "created_at": "2026-03-08 10:30:30",
        "updated_at": "2026-03-08 10:30:30"
      }
    ],
    "total": 156,
    "page": 1,
    "page_size": 20
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| id | int | 记录ID | 1234 |
| stock_code | string | 股票代码 | "600519" |
| stock_name | string | 股票名称 | "贵州茅台" |
| price | float | 触发价格 | 1680.50 |
| change_percent | float | 涨跌幅(%) | 3.92 |
| volume | int | 成交量 | 1250 |
| indicator | string | 指标标识 | "BBIHTM_G" |
| trigger_time | string | 触发时间 | "2026-03-08 10:30:25" |
| file_path | string | 监控文件路径 | "C:\\\\...\\\\回调买.txt" |
| raw_content | string | 原始文件行 | "600519\\t..." |
| status | string | 推送状态 | "success" |
| error_message | string | 错误信息 | "网络超时" |
| retry_count | int | 已重试次数 | 0 |
| webhook_response | string | Webhook响应 | JSON字符串 |
| created_at | string | 创建时间 | "2026-03-08 10:30:30" |
| updated_at | string | 更新时间 | "2026-03-08 10:30:30" |

---

### 4.2 获取单条推送记录详情

```http
GET /api/history/pushes/{record_id}
```

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1234,
    "stock_code": "600519",
    "stock_name": "贵州茅台",
    "price": 1680.50,
    "change_percent": 3.92,
    "volume": 1250,
    "indicator": "BBIHTM_G",
    "trigger_time": "2026-03-08 10:30:25",
    "file_path": "C:\\Users\\ckyto\\Desktop\\回调买.txt",
    "raw_content": "600519\\t贵州茅台\\t2026-03-08 10:30\\t1680.50\\t+3.92%\\t1250\\tBBIHTM_G",
    "status": "success",
    "error_message": null,
    "retry_count": 0,
    "webhook_response": "{\\"errcode\\":0,\\"errmsg\\":\\"ok\\"}",
    "wechat_message_id": "",
    "created_at": "2026-03-08 10:30:30",
    "updated_at": "2026-03-08 10:30:30"
  }
}
```

---

### 4.3 重新推送失败记录

```http
POST /api/history/pushes/{record_id}/retry
```

**响应示例 (成功)**:

```json
{
  "code": 0,
  "message": "重推成功",
  "data": {
    "success": true,
    "new_record_id": 1235
  }
}
```

**响应示例 (失败)**:

```json
{
  "code": -1,
  "message": "重推失败: 网络超时",
  "data": {
    "success": false,
    "error": "网络超时"
  }
}
```

**注意**: 只有 `status=failed` 的记录可以重推。

---

### 4.4 导出推送历史

```http
GET /api/history/export?format=csv&start_date=2026-03-01&end_date=2026-03-08
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| format | string | 是 | csv | 导出格式 (csv/xlsx) |
| start_date | string | 否 | - | 开始日期 |
| end_date | string | 否 | - | 结束日期 |
| stock_code | string | 否 | - | 股票代码筛选 |
| status | string | 否 | - | 状态筛选 |

**响应**:

返回文件下载，Content-Type: `text/csv` 或 `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**CSV格式示例**:

```csv
ID,股票代码,股票名称,价格,涨跌幅,成交量,指标,触发时间,状态,创建时间
1234,600519,贵州茅台,1680.50,3.92,1250,BBIHTM_G,2026-03-08 10:30:25,success,2026-03-08 10:30:30
```

---

## 五、System API (系统管理)

### 5.1 获取系统运行状态

```http
GET /api/system/status
```

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "service_status": "running",
    "monitor_status": "watching",
    "uptime": "2天3小时15分钟",
    "last_push_time": "2026-03-08 10:30:25",
    "error_count": 3,
    "cpu_percent": 12.5,
    "memory_percent": 35.2,
    "memory_used_mb": 180,
    "disk_usage_percent": 45.8,
    "database_size_mb": 12.5,
    "webhook_configured": true
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| service_status | string | 服务状态 | running/stopped/error |
| monitor_status | string | 监控状态 | watching/paused/error |
| uptime | string | 运行时间 | "2天3小时15分钟" |
| last_push_time | string | 最后推送时间 | "2026-03-08 10:30:25" |
| error_count | int | 今日错误数 | 3 |
| cpu_percent | float | CPU使用率(%) | 12.5 |
| memory_percent | float | 内存使用率(%) | 35.2 |
| memory_used_mb | float | 内存使用(MB) | 180 |
| disk_usage_percent | float | 磁盘使用率(%) | 45.8 |
| database_size_mb | float | 数据库大小(MB) | 12.5 |
| webhook_configured | boolean | Webhook是否配置 | true |

---

### 5.2 启动监控服务

```http
POST /api/system/start-monitor
```

**响应示例** (成功):

```json
{
  "code": 0,
  "message": "监控服务已启动",
  "data": {
    "success": true,
    "status": "watching"
  }
}
```

**响应示例** (失败):

```json
{
  "code": -1,
  "message": "启动失败: 文件路径不存在",
  "data": {
    "success": false,
    "error": "C:\\Users\\ckyto\\Desktop\\回调买.txt not found"
  }
}
```

---

### 5.3 停止监控服务

```http
POST /api/system/stop-monitor
```

**响应示例**:

```json
{
  "code": 0,
  "message": "监控服务已停止",
  "data": {
    "success": true,
    "status": "paused"
  }
}
```

---

### 5.4 获取系统日志

```http
GET /api/system/logs?level=INFO&page=1&page_size=50&start_time=&end_time=&module=
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| level | string | 否 | INFO | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 50 | 每页数量 (10-200) |
| start_time | string | 否 | - | 开始时间 (YYYY-MM-DD HH:MM:SS) |
| end_time | string | 否 | - | 结束时间 |
| module | string | 否 | - | 模块名筛选 |

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "timestamp": "2026-03-08 10:30:30",
        "level": "INFO",
        "module": "file_monitor",
        "message": "检测到文件变化: 回调买.txt",
        "exception": null
      },
      {
        "timestamp": "2026-03-08 10:30:25",
        "level": "ERROR",
        "module": "wechat_bot",
        "message": "企业微信推送失败",
        "exception": "TimeoutError: 请求超时"
      }
    ],
    "total": 1587
  }
}
```

---

### 5.5 清理系统日志

```http
DELETE /api/system/logs?before_date=2026-02-01&level=INFO
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| before_date | string | 否 | - | 删除该日期之前的日志 |
| level | string | 否 | - | 只删除指定级别的日志 |

**响应示例**:

```json
{
  "code": 0,
  "message": "已清理 1587 条日志",
  "data": {
    "deleted_count": 1587
  }
}
```

---

### 5.6 健康检查接口

```http
GET /api/system/health
```

**说明**: 用于监控系统健康状态，被监控工具(如Prometheus)调用。

**响应示例** (健康):

```json
{
  "code": 0,
  "message": "系统健康",
  "data": {
    "status": "healthy",
    "database": "ok",
    "monitor": "running",
    "wechat": "ok",
    "timestamp": "2026-03-08T10:30:30+08:00"
  }
}
```

**响应示例** (不健康, HTTP 503):

```json
{
  "code": -1,
  "message": "系统不健康: 数据库连接失败",
  "data": {
    "status": "unhealthy",
    "database": "error",
    "monitor": "running",
    "wechat": "ok",
    "timestamp": "2026-03-08T10:30:30+08:00"
  }
}
```

**HTTP状态码**: 503 (Service Unavailable)

---

### 5.7 获取Prometheus指标

```http
GET /api/system/metrics
```

**说明**: 返回Prometheus格式的系统指标。

**响应示例**:

```text
# HELP monitor_file_changes_total 文件变化总次数
# TYPE monitor_file_changes_total counter
monitor_file_changes_total{file_path="C:\\Users\\ckyto\\Desktop\\回调买.txt",status="success"} 124

# HELP push_wechat_total 企业微信推送总数
# TYPE push_wechat_total counter
push_wechat_total{status="success",retry_count="0"} 121
push_wechat_total{status="failed",retry_count="3"} 3

# HELP push_latency_seconds 推送延迟
# TYPE push_latency_seconds histogram
push_latency_seconds_bucket{le="0.1"} 15
push_latency_seconds_bucket{le="0.5"} 98
push_latency_seconds_bucket{le="1.0"} 118
push_latency_seconds_sum 65.8
push_latency_seconds_count 124

# HELP system_memory_mb 系统内存使用
# TYPE system_memory_mb gauge
system_memory_mb 180.5

# HELP system_cpu_percent 系统CPU使用率
# TYPE system_cpu_percent gauge
system_cpu_percent 12.5
```

**Content-Type**: `text/plain`

---

## 六、错误响应格式

### 6.1 统一错误格式

所有API错误都遵循以下格式:

```json
{
  "code": -1,
  "message": "错误描述",
  "data": null
}
```

### 6.2 HTTP状态码映射

| HTTP状态码 | 含义 | 场景 |
|-----------|------|------|
| 200 | 成功 | 正常响应 |
| 400 | 请求参数错误 | 参数验证失败 |
| 404 | 资源未找到 | 查询的记录不存在 |
| 422 | 业务逻辑错误 | 数据验证失败 |
| 500 | 服务器内部错误 | 未捕获的异常 |
| 503 | 服务不可用 | 健康检查失败 |

### 6.3 业务错误码

| 错误码 | 说明 | HTTP状态码 |
|--------|------|-----------|
| -1 | 通用错误 | 500 |
| -2 | 参数验证失败 | 400 |
| -3 | 资源未找到 | 404 |
| -4 | 权限不足 | 403 |
| -5 | 数据库操作失败 | 500 |
| -6 | 外部服务调用失败 | 502 |
| -7 | 重复操作 | 422 |
| -8 | 配置错误 | 500 |

---

## 七、请求示例

### 7.1 Python调用示例

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 获取大盘摘要
response = requests.get(f"{BASE_URL}/dashboard/summary")
summary = response.json()
print(f"今日成功率: {summary['data']['success_rate']}")

# 获取推送历史
response = requests.get(
    f"{BASE_URL}/history/pushes",
    params={
        "page": 1,
        "page_size": 20,
        "status": "failed"
    }
)
failed_pushes = response.json()
print(f"失败推送数: {failed_pushes['data']['total']}")

# 重新推送失败记录
response = requests.post(
    f"{BASE_URL}/history/pushes/1234/retry"
)
print(response.json()['message'])
```

### 7.2 JavaScript调用示例 (Axios)

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

// 获取大盘数据
async function fetchDashboard() {
  const [summary, trend, distribution] = await Promise.all([
    axios.get(`${API_BASE}/dashboard/summary`),
    axios.get(`${API_BASE}/dashboard/success-rate-trend`, {
      params: { days: 7 }
    }),
    axios.get(`${API_BASE}/dashboard/stock-distribution`)
  ]);
  
  return {
    summary: summary.data.data,
    trend: trend.data.data.list,
    distribution: distribution.data.data.list
  };
}

// 导出CSV
async function exportCSV() {
  const response = await axios.get(
    `${API_BASE}/history/export`,
    {
      params: {
        format: 'csv',
        start_date: '2026-03-01',
        end_date: '2026-03-08'
      },
      responseType: 'blob'  // 文件下载
    }
  );
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'push_history.csv');
  document.body.appendChild(link);
  link.click();
}
```

---

## 八、版本历史

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-03-08 | 初始版本，完整API设计 | OpenCode AI |

---

**说明：**

- 所有时间字段格式: `YYYY-MM-DD HH:MM:SS`
- 所有价格字段保留2位小数
- 所有百分比字段单位: %
