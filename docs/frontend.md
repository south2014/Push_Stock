# Push_Stock 前端设计文档

**版本**: v1.0  
**制定日期**: 2026-03-08  
**状态**: 已确认  
**技术栈**: Vue 3.3 + TypeScript 5.0 + Vite 5.0 + Element Plus 2.4

---

## 一、项目概述

### 1.1 项目定位

Push_Stock前端是一个基于Vue 3的企业级股票推送监控系统管理后台，提供数据可视化、配置管理、历史查询和系统监控功能。

### 1.2 技术选型

| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|---------|
| Vue | 3.3+ | 前端框架 | 性能优秀、Composition API、生态完善 |
| TypeScript | 5.0+ | 类型系统 | 类型安全、降低维护成本 |
| Vite | 5.0+ | 构建工具 | 极速启动、HMR、开箱即用 |
| Element Plus | 2.4+ | UI组件库 | 企业级组件、文档完善 |
| ECharts | 5.4+ | 图表库 | 功能强大、可定制性高 |
| Pinia | 2.1+ | 状态管理 | 轻量、TypeScript友好 |
| Axios | 1.6+ | HTTP客户端 | 拦截器、请求取消 |
| Vue Router | 4.2+ | 路由管理 | Vue 3官方路由 |

---

## 二、项目结构

```
web/
├── public/                     # 静态资源
│   ├── favicon.ico
│   └── logo.png
├── src/
│   ├── api/                    # API接口层
│   │   ├── config.ts           # 配置管理API
│   │   ├── dashboard.ts        # Dashboard数据API
│   │   ├── history.ts          # 推送历史API
│   │   └── system.ts           # 系统状态API
│   ├── assets/                 # 资源文件
│   │   ├── images/
│   │   └── styles/
│   │       └── main.scss       # 全局样式
│   ├── components/             # 公共组件
│   │   ├── common/             # 通用组件
│   │   │   ├── Loading.vue
│   │   │   ├── Empty.vue
│   │   │   └── Pagination.vue
│   │   └── dashboard/          # Dashboard专用组件
│   │       ├── PushSuccessRateChart.vue
│   │       ├── StockDistributionChart.vue
│   │       └── TimeDistributionChart.vue
│   ├── composables/            # Composition函数
│   │   ├── usePagination.ts    # 分页逻辑
│   │   └── useDateRange.ts     # 日期范围选择
│   ├── router/                 # 路由配置
│   │   └── index.ts
│   ├── stores/                 # Pinia状态管理
│   │   ├── config.ts           # 配置状态
│   │   └── system.ts           # 系统状态
│   ├── types/                  # TypeScript类型定义
│   │   ├── api.ts              # API响应类型
│   │   ├── config.ts           # 配置类型
│   │   └── dashboard.ts        # Dashboard数据类型
│   ├── utils/                  # 工具函数
│   │   ├── request.ts          # Axios封装
│   │   ├── date.ts             # 日期格式化
│   │   └── notification.ts     # 通知提示
│   ├── views/                  # 页面视图
│   │   ├── Dashboard.vue       # 数据大盘
│   │   ├── Config.vue          # 配置管理
│   │   ├── History.vue         # 推送历史
│   │   └── NotFound.vue        # 404页面
│   ├── App.vue                 # 根组件
│   └── main.ts                 # 入口文件
├── .env.development            # 开发环境变量
├── .env.production             # 生产环境变量
├── index.html                  # HTML模板
├── package.json                # 依赖配置
├── tsconfig.json               # TypeScript配置
├── vite.config.ts              # Vite配置
├── .eslintrc.js                # ESLint配置
└── .gitignore                  # Git忽略
```

---

## 三、核心功能设计

### 3.1 Dashboard 数据大盘

**页面布局**:

```
┌─────────────────────────────────────────────────────────────┐
│  Push_Stock 数据大盘                           [刷新] [导出]  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │今日推送  │  │成功数    │  │失败率    │  │监控状态  │  │
│  │   124    │  │   121    │  │   2.4%   │  │  正常    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│  推送成功率趋势                    股票触发分布              │
│  ┌──────────────────────────┐    ┌──────────────────┐     │
│  │                          │    │                  │     │
│  │      ECharts折线图       │    │   ECharts饼图    │     │
│  │                          │    │                  │     │
│  └──────────────────────────┘    └──────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  时间分布热力图          │  最近推送记录(快速预览)          │
│  ┌─────────────────┐     │  ┌─────────────────────────┐   │
│  │                 │     │  │ 10:30 600519 贵州茅台  │   │
│  │  ECharts热力图  │     │  │ 10:28 000858 五粮液    │   │
│  │                 │     │  │ 10:25 002734 利民股份  │   │
│  └─────────────────┘     │  │ ...                     │   │
└──────────────────────────┴───────────────────────────────┘
```

**核心组件**:

- **StatCard.vue**: 统计卡片组件 (今日推送、成功率、监控状态)
- **SuccessRateChart.vue**: 推送成功率趋势图 (ECharts折线图)
- **StockDistributionChart.vue**: 股票分布饼图 (ECharts饼图)
- **TimeDistributionChart.vue**: 时间分布热力图 (ECharts热力图)
- **RecentPushes.vue**: 最近推送记录列表

---

### 3.2 Config 配置管理

**页面布局**:

```
┌─────────────────────────────────────────────────────────────┐
│  系统配置管理                                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐                                               │
│  │文件监控 │  右侧配置内容                                   │
│  │企业微信 │  ┌─────────────────────────────────────────┐  │
│  │推送策略 │  │ 配置文件监控路径                          │  │
│  │         │  │  ┌───────────────────────────────────┐  │  │
│  │         │  │  │ 监控路径: C:\\...\\回调买.txt      │  │  │
│  │         │  │  │ [测试连通性] [新增路径]            │  │  │
│  │         │  │  ├───────────────────────────────────┤  │  │
│  │         │  │  │ 文件列表:                         │  │  │
│  │         │  │  │  ┌─────────────────────────┐      │  │  │
│  │         │  │  │ │ 回调买.txt  [启用] [删除]│      │  │  │
│  │         │  │  │ │ 反弹卖.txt  [禁用] [删除]│      │  │  │
│  │         │  │  │ └─────────────────────────┘      │  │  │
│  │         │  │  └───────────────────────────────────┘  │  │
│  └─────────┤  │                                        │  │
│            │  │  [保存配置] [重置] [导出配置]            │  │
│            │  └─────────────────────────────────────────┘  │
└────────────┴─────────────────────────────────────────────────┘
```

**功能模块**:

- **文件监控配置**: 添加、删除、启用/禁用监控文件
- **企业微信配置**: Webhook URL、群主ID、机器人名称
- **推送策略配置**: 重试次数、重试间隔、去重窗口、批量推送
- **配置验证**: 测试Webhook连通性
- **导入/导出**: JSON格式配置导入导出

---

### 3.3 History 推送历史

**页面布局**:

```
┌─────────────────────────────────────────────────────────────┐
│  推送历史记录                                [导出] [刷新]  │
├─────────────────────────────────────────────────────────────┤
│                                                           │
│  筛选条件:                                                 │
│  [股票代码: ________] [日期范围: ________] [状态: 全部 ▼]  │
│  [文件: 全部 ▼] [开始时间: ____] [结束时间: ____] [查询]    │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 时间       │ 股票    │ 价格  │ 状态    │ 操作     │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ 10:30:25   │ 600519  │ 1680.50│ 成功 ✓  │ [详情]  │  │
│  │            │ 贵州茅台│       │         │ [重推]  │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ 10:28:15   │ 000858  │ 156.30 │ 失败 ✗  │ [详情]  │  │
│  │            │ 五粮液  │       │ 网络超时│ [重推]  │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ ...                                                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
│  [上一页] 1 2 3 4 5 ... 20 [下一页]   每页: [20 ▼] 条      │
└─────────────────────────────────────────────────────────────┘
```

**功能模块**:

- **多维度筛选**: 股票代码、日期范围、状态、监控文件、时间范围
- **分页展示**: 每页20/50/100条可选
- **状态标签**: 成功(绿色)、失败(红色)、重试中(黄色)
- **操作按钮**: 查看详情、重新推送、导出
- **批量操作**: 批量导出、批量重试

---

### 3.4 System 系统状态

**页面布局**:

```
┌─────────────────────────────────────────────────────────────┐
│  系统状态监控                                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐  │
│  │ 服务运行状态     │  │ 系统资源使用     │  │ 数据库   │  │
│  │ Status: Running  │  │ CPU: 12.5%       │  │ Size:    │  │
│  │ Monitor: Watching│  │ Memory: 180MB    │  │ 12.5MB   │  │
│  │ Uptime: 2d3h     │  │ Disk: 45.8%      │  │          │  │
│  └──────────────────┘  └──────────────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│  [启动监控] [停止监控] [重启服务] [查看日志]                 │
├─────────────────────────────────────────────────────────────┤
│  系统日志:                                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 时间              级别  模块          消息          │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ 10:30:30  INFO   file_monitor  检测到文件变化      │  │
│  │ 10:30:25  ERROR  wechat_bot   推送失败: 网络超时   │  │
│  │ ...                                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│  [清理日志] [导出日志]                                     │
└─────────────────────────────────────────────────────────────┘
```

**功能模块**:

- **系统状态监控**: 服务状态、监控状态、运行时长
- **资源监控**: CPU使用率、内存占用、磁盘使用率
- **数据库信息**: 数据库大小、表数量、最后备份时间
- **控制面板**: 启动/停止监控、重启服务
- **日志查看**: 实时日志、按级别筛选、清理旧日志

---

## 四、TypeScript 类型定义

### 4.1 API响应类型 (types/api.ts)

```typescript
// 通用响应格式
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

// 分页信息
export interface Pagination {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

// 带分页的响应
export interface PaginatedResponse<T> extends ApiResponse<T> {
  data: T & {
    list: any[];
    total: number;
    page: number;
    page_size: number;
  };
}
```

### 4.2 Dashboard 类型 (types/dashboard.ts)

```typescript
// 大盘摘要
export interface DashboardSummary {
  today_total: number;
  today_success: number;
  today_failed: number;
  success_rate: string; // "97.58%"
  monitor_status: 'running' | 'stopped' | 'error';
  uptime: string;
  last_push_time?: string;
}

// 成功率趋势
export interface SuccessRateTrendItem {
  date: string; // "2026-03-01"
  success_count: number;
  failed_count: number;
  success_rate: number; // 0.986
}

export interface SuccessRateTrendResponse {
  list: SuccessRateTrendItem[];
  total: number;
}

// 股票分布
export interface StockDistributionItem {
  code: string;
  name: string;
  count: number;
  percentage: number; // 12.5
}

export interface StockDistributionResponse {
  list: StockDistributionItem[];
  total: number;
}

// 时间分布热力图
export interface TimeDistributionResponse {
  hours: string[]; // ["09:00", "10:00", ...]
  days: string[]; // ["周一", "周二", ...]
  data: number[][]; // [[hourIndex, dayIndex, value], ...]
}

// 推送记录
export interface PushRecord {
  id: number;
  stock_code: string;
  stock_name: string;
  price: number;
  change_percent?: number;
  volume?: number;
  indicator?: string;
  trigger_time: string;
  file_path: string;
  raw_content: string;
  status: 'success' | 'failed' | 'retrying' | 'pending';
  error_message?: string;
  retry_count: number;
  webhook_response?: string;
  created_at: string;
  updated_at: string;
}

export interface RecentPushListResponse {
  list: PushRecord[];
  total: number;
}
```

### 4.3 Config 类型 (types/config.ts)

```typescript
// 文件监控配置
export interface FileMonitorConfig {
  id?: number;
  file_path: string;
  enabled: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

// 企业微信配置
export interface WeChatConfig {
  webhook_url: string;
  owner_user_id?: string;
  bot_name: string;
  enabled: boolean;
}

// 推送策略配置
export interface PushStrategyConfig {
  retry_count: number;
  retry_intervals: number[]; // [5, 30, 120]
  duplicate_window_seconds: number;
  batch_enabled: boolean;
  batch_interval_seconds: number;
  daily_push_limit: number;
}
```

---

## 五、API 调用封装 (api 层)

### 5.1 request.ts (Axios封装)

```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { ElMessage } from 'element-plus';

const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 添加认证token（如需要）
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    
    if (res.code !== 0) {
      ElMessage.error(res.message || '请求失败');
      return Promise.reject(new Error(res.message || '请求失败'));
    }
    
    return res;
  },
  (error: AxiosError) => {
    const message = error.response?.data?.message || error.message;
    ElMessage.error(`请求失败: ${message}`);
    return Promise.reject(error);
  }
);

export default service;
```

### 5.2 dashboard.ts

```typescript
import service from '@/utils/request';
import type {
  DashboardSummary,
  SuccessRateTrendResponse,
  StockDistributionResponse,
  TimeDistributionResponse,
  RecentPushListResponse
} from '@/types/dashboard';

export const dashboardApi = {
  // 获取大盘摘要
  getSummary(): Promise<DashboardSummary> {
    return service.get('/dashboard/summary').then(res => res.data);
  },
  
  // 获取成功率趋势
  getSuccessRateTrend(days: number = 7): Promise<SuccessRateTrendResponse> {
    return service.get('/dashboard/success-rate-trend', {
      params: { days }
    }).then(res => res.data);
  },
  
  // 获取股票分布
  getStockDistribution(days: number = 30, limit: number = 20): Promise<StockDistributionResponse> {
    return service.get('/dashboard/stock-distribution', {
      params: { days, limit }
    }).then(res => res.data);
  },
  
  // 获取时间分布热力图
  getTimeDistribution(days: number = 7): Promise<TimeDistributionResponse> {
    return service.get('/dashboard/time-distribution', {
      params: { days }
    }).then(res => res.data);
  },
  
  // 获取最近推送
  getRecentPushes(limit: number = 10): Promise<RecentPushListResponse> {
    return service.get('/dashboard/recent-pushes', {
      params: { limit }
    }).then(res => res.data);
  }
};
```

---

## 六、状态管理 (Pinia)

### 6.1 Dashboard Store (stores/dashboard.ts)

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { dashboardApi } from '@/api/dashboard';
import type { DashboardSummary } from '@/types/dashboard';

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const summary = ref<DashboardSummary | null>(null);
  const loading = ref(false);
  
  // Actions
  async function fetchSummary() {
    loading.value = true;
    try {
      summary.value = await dashboardApi.getSummary();
    } catch (error) {
      console.error('获取摘要失败:', error);
    } finally {
      loading.value = false;
    }
  }
  
  // 自动刷新 (每30秒)
  function startAutoRefresh() {
    setInterval(() => {
      fetchSummary();
    }, 30000);
  }
  
  return {
    summary,
    loading,
    fetchSummary,
    startAutoRefresh
  };
});
```

### 6.2 Config Store (stores/config.ts)

```typescript
import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { FileMonitorConfig, WeChatConfig, PushStrategyConfig } from '@/types/config';

export const useConfigStore = defineStore('config', () => {
  // State
  const fileMonitors = ref<FileMonitorConfig[]>([]);
  const wechatConfig = ref<WeChatConfig | null>(null);
  const pushStrategy = ref<PushStrategyConfig | null>(null);
  const loading = ref(false);
  
  // Actions
  async function fetchFileMonitors() {
    loading.value = true;
    try {
      const res = await configApi.getFileMonitors();
      fileMonitors.value = res;
    } finally {
      loading.value = false;
    }
  }
  
  async function addFileMonitor(config: Partial<FileMonitorConfig>) {
    const newConfig = await configApi.createFileMonitor(config);
    fileMonitors.value.push(newConfig);
  }
  
  async function testWebhook() {
    const result = await configApi.testWeChatConfig();
    return result.success;
  }
  
  return {
    fileMonitors,
    wechatConfig,
    pushStrategy,
    loading,
    fetchFileMonitors,
    addFileMonitor,
    testWebhook
  };
});
```

---

## 七、路由配置 (router/index.ts)

```typescript
import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      title: '数据大盘',
      icon: 'Odometer'
    }
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/Config.vue'),
    meta: {
      title: '配置管理',
      icon: 'Setting'
    }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: {
      title: '推送历史',
      icon: 'Document'
    }
  },
  {
    path: '/system',
    name: 'System',
    component: () => import('@/views/System.vue'),
    meta: {
      title: '系统状态',
      icon: 'Monitor'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - Push Stock`;
  }
  next();
});

export default router;
```

---

## 八、ECharts 图表配置

### 8.1 成功率趋势图

```typescript
// composables/useSuccessRateChart.ts

import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

export function useSuccessRateChart() {
  const chartRef = ref<HTMLDivElement>();
  let chart: echarts.ECharts | null = null;
  
  function initChart() {
    if (!chartRef.value) return;
    
    chart = echarts.init(chartRef.value);
    
    const option: EChartsOption = {
      title: {
        text: '推送成功率趋势',
        textStyle: { fontSize: 16, fontWeight: 'normal' }
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const data = params[0];
          return `${data.name}<br/>成功率: ${(data.value * 100).toFixed(2)}%`;
        }
      },
      xAxis: {
        type: 'category',
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 1,
        axisLabel: {
          formatter: (value: number) => `${(value * 100).toFixed(0)}%`
        }
      },
      series: [{
        type: 'line',
        smooth: true,
        areaStyle: {
          opacity: 0.3
        },
        lineStyle: {
          width: 3
        },
        itemStyle: {
          color: '#00c851'
        }
      }]
    };
    
    chart.setOption(option);
  }
  
  function setData(data: { date: string; success_rate: number }[]) {
    if (!chart) return;
    
    const option: EChartsOption = {
      xAxis: {
        data: data.map(item => item.date)
      },
      series: [{
        data: data.map(item => item.success_rate)
      }]
    };
    
    chart.setOption(option);
  }
  
  function resize() {
    chart?.resize();
  }
  
  function dispose() {
    chart?.dispose();
    chart = null;
  }
  
  onMounted(() => {
    initChart();
    window.addEventListener('resize', resize);
  });
  
  onUnmounted(() => {
    dispose();
    window.removeEventListener('resize', resize);
  });
  
  return {
    chartRef,
    setData,
    resize
  };
}
```

---

## 九、UI/UX 设计规范

### 9.1 颜色方案

```scss
// src/assets/styles/variables.scss

// 主色调
$primary: #0066cc;        // 专业蓝
$success: #52c41a;        // 成功绿
$warning: #faad14;        // 警告橙
$error: #f5222d;          // 错误红

// 中性色
$bg-primary: #121a2a;     // 深蓝黑背景
$bg-card: #1a243f;        // 卡片背景
$text-primary: #e6f7ff;   // 主要文字
$text-secondary: #8b9dc3; // 次要文字
$border: #2a3f6f;         // 边框

// 图表颜色
$chart-success: #00c851;
$chart-warning: #ff9800;
$chart-error: #ff4444;
$chart-grid: rgba(255, 255, 255, 0.1);
```

### 9.2 组件样式规范

```scss
// Element Plus 主题定制

// 覆盖默认主题
:root {
  --el-color-primary: #0066cc;
  --el-bg-color: #121a2a;
  --el-text-color-primary: #e6f7ff;
  --el-text-color-regular: #8b9dc3;
  --el-border-color: #2a3f6f;
  --el-fill-color-blank: #1a243f;
  --el-box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.5);
}

// 自定义组件样式
.el-card {
  background-color: $bg-card;
  border: 1px solid $border;
  border-radius: 8px;
  
  .el-card__header {
    border-bottom: 1px solid $border;
    color: $text-primary;
  }
}

.el-table {
  background-color: transparent;
  color: $text-primary;
  
  th, td {
    border-bottom: 1px solid $border;
  }
  
  th {
    background-color: rgba(0, 0, 0, 0.2);
    color: $text-primary;
  }
  
  tbody tr:hover {
    background-color: rgba(0, 102, 204, 0.1);
  }
}
```

---

## 十、性能优化

### 10.1 代码分割

```typescript
// router/index.ts

const routes: RouteRecordRaw[] = [
  {
    path: '/dashboard',
    component: () => import(/* webpackChunkName: "dashboard" */ '@/views/Dashboard.vue')
  },
  {
    path: '/config',
    component: () => import(/* webpackChunkName: "config" */ '@/views/Config.vue')
  },
  {
    path: '/history',
    component: () => import(/* webpackChunkName: "history" */ '@/views/History.vue')
  }
];
```

### 10.2 虚拟滚动 (大数据量列表)

```vue
<template>
  <el-table-v2
    :columns="columns"
    :data="tableData"
    :width="700"
    :height="400"
    fixed
  />
</template>

<script setup lang="ts">
// 使用 Element Plus 的虚拟表格组件
// 适用于10万+数据量场景
</script>
```

### 10.3 Keep-Alive 缓存

```vue
<template>
  <router-view v-slot="{ Component }">
    <keep-alive include="Dashboard,Config">
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>
```

---

## 十一、开发规范

### 11.1 命名规范

- **组件文件名**: PascalCase (Dashboard.vue)
- **组合函数**: camelCase (usePagination.ts)
- **变量**: camelCase (fileMonitors)
- **常量**: UPPER_CASE (API_BASE_URL)
- **接口**: PascalCase + 前缀 I (IPushRecord)

### 11.2 Git提交规范

```bash
feat(Dashboard): 添加推送成功率趋势图组件
# 新功能

fix(Config): 修复Webhook测试连通性验证
# Bug修复

style: 统一按钮组件样式
# 样式调整

docs: 更新API接口文档
# 文档更新
```

### 11.3 代码质量检查

```json
{
  "scripts": {
    "lint": "eslint src --ext .vue,.js,.ts --fix",
    "type-check": "vue-tsc --noEmit",
    "test": "vitest",
    "build": "vite build"
  }
}
```

---

## 十二、构建与部署

### 12.1 开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
# http://localhost:5173

# 运行测试
npm run test

# 代码检查
npm run lint

# 类型检查
npm run type-check
```

### 12.2 生产构建

```bash
# 构建生产版本
npm run build

# 输出到 dist/ 目录
# 将 dist/ 目录部署到静态服务器

# 预览构建结果
npm run preview
```

### 12.3 部署配置

**Nginx配置**:

```nginx
server {
  listen 80;
  server_name localhost;
  
  location / {
    root /path/to/dist;
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

---

## 十三、版本规划

### v1.0 (当前)

- [x] Dashboard数据大盘
- [x] Config配置管理
- [x] History推送历史
- [x] System系统状态
- [x] ECharts图表集成
- [x] Element Plus组件库

### v1.1 (2周后)

- [ ] 移动端响应式适配
- [ ] 暗黑/亮色主题切换
- [ ] 自定义Dashboard布局
- [ ] 推送通知声音提醒

### v1.2 (4周后)

- [ ] WebSocket实时推送
- [ ] 数据导出Excel
- [ ] 图表数据钻取
- [ ] 快捷键支持

---

**文档修订历史:**
- v1.0 (2026-03-08): 初始版本，完整前端设计

**维护者:** OpenCode AI
