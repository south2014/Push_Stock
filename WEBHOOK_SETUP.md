# 企业微信机器人创建指南

## 创建步骤

### 1. 打开企业微信群
- 在手机或电脑上打开企业微信
- 进入你想接收股票信号的群聊

### 2. 添加群机器人
**手机端：**
1. 点击右上角「···」
2. 选择「群机器人」
3. 点击「添加机器人」
4. 选择「新建机器人」
5. 输入名字：StockBot
6. 点击「确定」

**电脑端：**
1. 右键群聊 → 群设置
2. 点击「群机器人」
3. 点击「添加机器人」
4. 选择「新建机器人」
5. 输入名字：StockBot
6. 点击「确定」

### 3. 获取Webhook URL
创建成功后，会显示：
```
Webhook地址：
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxxxx
```

**复制这个URL，这就是你的机器人地址！**

### 4. 配置到项目

**方法1 - 环境变量（推荐）：**
```cmd
cd F:\OpenCode\Push_Stock
set WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的KEY
```

**方法2 - .env文件：**
创建文件 `.env` 内容：
```
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的KEY
```

### 5. 测试
```cmd
venv\Scripts\python.exe test_wechat_push.py
```

## 常见问题

### Q: 看不到"群机器人"选项？
**A:** 你可能不是群主或管理员，请联系群主添加。

### Q: Webhook URL泄露了怎么办？
**A:** 在群机器人列表中，找到StockBot → 点击「重新生成」获得新URL。

### Q: 推送没反应？
**A:** 
1. 检查URL是否完整复制
2. 检查是否被频率限制（每分钟最多20条）
3. 检查网络连接

## 安全提醒

⚠️ **重要**：Webhook URL相当于机器人的密码
- 不要分享给他人
- 不要提交到Git仓库
- 如泄露立即重新生成

## 下一步

获取Webhook URL后，告诉我，我帮你运行测试！
