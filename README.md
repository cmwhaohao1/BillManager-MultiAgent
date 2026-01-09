# Multi-Agent Demo

A demo showcasing multi-agent collaboration where an **assistant agent** communicates with users and delegates database operations to a **MySQL expert agent** for transaction record management.

## Architecture

### Agents

1. **Assistant Agent** (`assistant`)
   - Handles daily conversation with users
   - Understands user intent for transaction operations
   - Summarizes user requests into clear, concise instructions
   - Delegates database operations (query/insert) to mysql_


expert
   - Coordinates user interaction

2. **MySQL Expert Agent** (`mysql_expert`)
   - ONLY responds to commands from assistant
   - Executes SQL queries on transaction database
   - Generates appropriate SQL queries based on natural language dates
   - Validates SQL for security
   - Reports query/insert results to public channel

## Database Schema

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

## Workflow

### Query Transactions
- User: "What happened last week?", "上周什么情况"
- Assistant summarizes request and delegates to mysql_expert
- MySQL expert generates SQL query
- MySQL expert executes query and returns results
- Results shown to user with summary (total income, expense, net)

### Add Transaction
- User: "Earned 100 yuan yesterday", "昨天收入100"
- Assistant summarizes: income 100, yesterday, remark
- MySQL expert generates INSERT query
- MySQL expert executes and confirms
- User receives confirmation

### Daily Conversation
- User: "Hello", "Hi"
- Assistant responds directly with friendly message

## MySQL Configuration

Database configuration in `tools/mysql_tools.py`:
```python
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "transaction_db",
    "charset": "utf8mb4"
}
```

Update the password as needed for your MySQL installation.

## Setup

1. Install MySQL connector:
   ```bash
   pip install mysql-connector-python
   ```

2. Create database and tables:
   ```sql
   CREATE DATABASE IF NOT EXISTS transaction_db;
   USE transaction_db;

   CREATE TABLE IF NOT EXISTS transactions (...);  -- See schema above
   ```

3. Update `MYSQL_CONFIG` in `tools/mysql_tools.py` with your credentials

4. Run the network:
   ```bash
   openagents run demos/09_multi_agent/network.yaml
   ```

5. Access studio at `http://localhost:8700/studio`


## Demo video
https://github.com/user-attachments/assets/ed25832e-ab46-49b6-a3b7-35d9c8e72e1e


## Tools


### mysql_tools.py
- `execute_sql_query(sql, params)` - Execute SQL and return results
- `validate_sql(sql)` - Validate SQL for security
- `parse_date_range(date_range)` - Parse natural language dates to SQL conditions

Supported date ranges:
- "today", "yesterday", "last week", "this week", "this month", "last month"
- "今天", "昨天", "上周", "本周", "本月", "上月"

## Key Features

- **Multi-agent collaboration**: Clear separation of concerns
- **Natural language dates**: Parse colloquial time expressions
- **SQL validation**: Security checks before execution
- **Markdown responses**: All public replies in Markdown format
- **Multilingual**: Supports Chinese and English queries

## Important Notes

- MySQL expert ONLY responds to events from assistant, not user messages directly
- Assistant delegates all database operations and lets MySQL expert reply
- All prompts are in English (GBK compatible)
- Agents reply in user's language (Chinese or English)
- Ensure MySQL connector is installed before running

## Known Issues

**File Upload Bug**: The file upload functionality is currently experiencing issues. Files uploaded via the messaging interface are not being properly saved or accessed by the agents. This is under active investigation and will be fixed in an upcoming update.
