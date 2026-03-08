# AI 助手指南

## 项目信息
- **项目类型**: Python
- **GitHub**: south2014/Push_Stock
- **主要分支**: main

## 常用命令

### Git 操作
```bash
# 查看状态
git status

# 添加所有更改
git add .

# 提交更改
git commit -m "描述本次修改"

# 推送到 GitHub
git push origin main

# 拉取最新更改
git pull origin main
```

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行单个测试文件
python -m pytest tests/test_example.py

# 运行单个测试函数
python -m pytest tests/test_example.py::test_function_name
```

### 代码检查
```bash
# 安装 Black
pip install black

# 格式化代码
black src/

# 检查格式（不修改）
black --check src/
```

## 代码风格规范

### 导入
- 标准库导入在前
- 第三方库导入在中
- 本地模块导入在后
- 每组之间空一行

```python
# 正确示例
import os
import sys

import requests
import pandas as pd

from src.module import function
```

### 命名规范
- 函数/变量: `snake_case`
- 类: `PascalCase`
- 常量: `UPPER_CASE`
- 私有方法: `_internal_use`

### 函数设计
- 函数最多 50 行
- 参数不超过 5 个
- 一个函数只做一件事
- 使用类型注解

```python
def process_data(
    raw_data: list[dict], 
    filter_key: str = "active"
) -> list[dict]:
    """处理原始数据并过滤。
    
    Args:
        raw_data: 原始数据列表
        filter_key: 过滤键值
        
    Returns:
        过滤后的数据列表
    """
    # 实现代码
    pass
```

### 错误处理
- 不要捕获所有异常: ❌ `except:`
- 捕获具体异常: ✅ `except ValueError:`
- 使用 try-except-else-finally 模式

### 注释
- 函数必须有 docstring
- 复杂逻辑添加行内注释
- 解释"为什么"，而不是"做什么"

## Python 环境
- Python 3.8+
- 使用虚拟环境:
  ```bash
  python -m venv venv
  # Windows
  venv\Scripts\activate
  ```

## Git 提交规范
- 使用简洁的英文描述
- 动词开头: "add", "fix", "update", "remove"
- 示例:
  - ✅ "add user authentication"
  - ✅ "fix login bug"
  - ❌ "修改了代码"

## 项目技术栈
- Python 3.x
- Git + GitHub
- VS Code
