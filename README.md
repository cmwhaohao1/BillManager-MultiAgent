# 多代理账单助手demo演示
一个展示多智能体协作的演示，其中助手智能体与用户进行日常对话，并将数据库操作委托给 MySQL 专家智能体，用于交易记录管理。

## 架构
### 代理
1. **助理代理** (`assistant`)
   - 处理与用户的日常对话
   - 理解用户对交易操作的意图
   - 将用户请求总结成清晰、简洁的指令
   - 将数据库操作（查询/插入）委托给 `mysql_expert`
   - 协调用户交互

2. **MySQL 专家代理** (`mysql_expert`)
   - **仅**响应来自助理的命令
   - 在交易数据库上执行 SQL 查询
   - 根据自然语言日期生成合适的 SQL 查询
   - 验证 SQL 的安全性
   - 将查询/插入结果报告到公共频道

## 工作流程
### 查询交易记录
- 用户输入示例："上周什么情况？" 或 "What happened last week?"
- 助理代理（assistant）：
  - 理解用户意图
  - 将请求总结成清晰指令（如：查询上周所有交易记录）
  - 通过事件委托给 MySQL 专家代理（mysql_expert）
- MySQL 专家代理：
  - 根据自然语言日期生成对应的 SQL 查询语句
  - 验证 SQL 安全性
  - 执行查询
  - 将查询结果（包括原始数据或汇总）发送到公共频道
- 助理代理：
  - 接收结果
  - 整理成友好、可读的总结（例如：总收入、总支出、净额、当日/周平均等）
  - 以 Markdown 格式回复用户

### 添加交易记录
- 用户输入示例："昨天收入100元" 或 "Earned 100 yuan yesterday" 或 "前天花了50买咖啡"
- 助理代理（assistant）：
  - 解析关键信息：金额、正负（收入/支出）、日期、备注
  - 总结成结构化指令（如：插入记录，日期=昨天，金额=+100，备注=无）
  - 委托给 MySQL 专家代理
- MySQL 专家代理：
  - 生成安全的 INSERT SQL 语句
  - 验证语法和安全性
  - 执行插入
  - 返回执行结果（成功/失败 + 新记录 ID 等）
- 助理代理：
  - 收到确认后
  - 回复用户类似：“已记录：昨天收入 100 元。感谢添加！”

### 日常对话（非数据库操作）
- 用户输入示例："你好"、"今天天气怎么样？"、"帮我记一下就行吗"
- 助理代理直接处理：
  - 无需委托数据库操作
  - 友好、自然地回复（支持中英文）
  - 保持对话连贯性和趣味性
  - 如果用户后续转向交易相关，再切换到相应流程

所有数据库相关操作（查询、插入、更新等）都严格通过助理 → MySQL 专家 的委托机制完成，确保职责分离和安全性。

## 安装

1. 安装openagent:
   https://github.com/openagents-org/openagent
   
2. 安装 MySQL 连接器：
   ```bash
   pip install mysql-connector-python
   
3. 初始化数据库:
   ```sql
   CREATE TABLE transactions (
       id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
       transaction_date DATE NOT NULL,
       amount DECIMAL(15,2) NOT NULL,
       remark TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       INDEX idx_date (transaction_date),
       INDEX idx_amount (amount),
       INDEX idx_date_amount (transaction_date, amount)
   );
   
   CREATE VIEW transaction_summary AS
   SELECT
       transaction_date,
       COUNT(*) as total_count,
       SUM(amount) as daily_total,
       AVG(amount) as daily_avg
   FROM transactions
   GROUP BY transaction_date;
```

4. 修改BillManager-MultiAgent/tools/mysql_tools.py里的mysql配置：
   MYSQL_CONFIG = {
       "host": "192.168.40.42",
       "port": 3306,
       "user": "root",
       "password": "123456",
       "database": "transaction_db",
       "charset": "utf8mb4"
   }
   
5. 设置千问key环境变量
   $env:DASHSCOPE_API_KEY="你的千问秘钥"

6. 运行openagents网络:
   ```bash
   openagents run BillManager-MultiAgent/network.yaml
   ```

7. 运行两个openagents代理:
   ```bash
   openagents agent start BillManager-MultiAgent/agents/assistant.yaml
   ```
   
   ```bash
   openagents agent start BillManager-MultiAgent/agents/mysql_expert.yaml
   ```


## 功能演示视频
https://github.com/user-attachments/assets/ed25832e-ab46-49b6-a3b7-35d9c8e72e1e
B站链接：
https://www.bilibili.com/video/BV1RYrfBFEDP/?spm_id_from=333.1387.list.card_archive.click



## 后续开发工作
   ocr识别上传账单图片功能目前存在bug，修复中
