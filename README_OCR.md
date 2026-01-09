# Multi-Agent Demo with OCR Support

## 智能体架构

### 1. Assistant (assistant)
- 与用户对话，理解用户意图
- 处理数据库查询请求（查询、插入、更新、删除）
- 处理 OCR 结果，询问用户确认收入/支出类型
- 将数据库操作委托给 mysql_expert

### 2. MySQL Expert (mysql_expert)
- 执行 SQL 查询
- 参数化查询，防止 SQL 注入
- 验证 SQL 安全性

### 3. OCR Agent (ocr_agent)
- 处理上传的图片文件
- 调用本地 OCR 服务
- 提取财务信息（金额、类型）
- 简化为一行摘要
- 将结果发送给 assistant

## 工作流程

### 文件上传流程
1. 用户上传图片文件
2. ocr_agent 接收文件上传事件
3. ocr_agent 调用本地 OCR 服务 (http://localhost:8080/ocr)
4. OCR 服务返回 JSON 格式的财务数据
5. ocr_agent 简化并分类（invoice/expense/income/unknown）
6. ocr_agent 发送 ocr.result 事件给 assistant
7. assistant 显示 OCR 结果，询问用户是支出还是收入
8. 用户确认后，assistant 将交易发送给 mysql_expert 保存

### 数据库操作流程
1. 用户请求查询/插入/更新/删除
2. assistant 理解意图并发送事件给 mysql_expert
3. mysql_expert 生成 SQL 并执行
4. mysql_expert 发送 db.result 事件给 assistant
5. assistant 格式化结果并回复用户

## 启动步骤

### 1. 初始化数据库
```bash
mysql -u root -p < init_database.sql
```

### 2. 启动 OCR 服务（模拟）
```bash
cd demos/09_multi_agent
python ocr_service.py
```

### 3. 启动网络服务
```bash
cd demos/09_multi_agent
openagents network start
```

### 4. 启动智能体（分别在不同终端）

```bash
# Terminal 1: MySQL Expert
openagents agent run mysql_expert

# Terminal 2: OCR Agent  
openagents agent run ocr_agent

# Terminal 3: Assistant
openagents agent run assistant
```

## OCR 摘要格式

### 发票类 (invoice)
```
Buyer: [公司A], Seller: [公司B], Invoice Amount: [总额]RMB
```

### 明确支出/收入 (expense/income)
```
[上下文] expense/income [金额]RMB
例: Supermarket shopping expense 120RMB
例: Salary income 5000RMB
```

### 不明确类型 (unknown)
```
Unknown [金额]RMB
例: Unknown 23.12RMB
```

## 配置说明

### 数据库配置
在 `tools/mysql_tools.py` 中修改：
```python
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "transaction_db",
    "charset": "utf8mb4"
}
```

### OCR 服务地址
在 `tools/ocr_tools.py` 中修改：
```python
OCR_SERVICE_URL = "http://localhost:8080/ocr"
```

## 实际部署说明

当前 OCR 服务是模拟的，实际使用时需要：

1. 安装真实的 OCR 库（如 PaddleOCR、Tesseract）
2. 替换 `ocr_service.py` 中的模拟逻辑
3. 确保数据库配置正确
