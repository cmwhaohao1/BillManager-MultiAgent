"""
MySQL Tools for Multi-Agent Demo
Provides database operations for transaction records.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def test_database_connection() -> str:
    """
    Test MySQL database connection.

    Returns:
        Connection status message
    """
    try:
        import mysql.connector
        from mysql.connector import Error as MySQLError

        logger.info(f"Testing connection to MySQL: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")

        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Test query
        cursor.execute("SELECT COUNT(*) as count FROM transactions")
        result = cursor.fetchone()
        count = result['count'] if result else 0

        cursor.close()
        conn.close()

        logger.info(f"Database connection successful. Current record count: {count}")
        return f"OK: Database connected. Current records: {count}"

    except ImportError:
        return "Error: MySQL connector not installed"
    except MySQLError as e:
        return f"Error: Database connection failed - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# MySQL connection configuration (should be configured based on environment)
MYSQL_CONFIG = {
    "host": "192.168.40.42",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "transaction_db",
    "charset": "utf8mb4"
}


def execute_sql_query(sql: str, params: Dict[str, Any] = None) -> str:
    """
    Execute SQL query and return results.

    Args:
        sql: SQL query to execute
        params: Query parameters (optional)

    Returns:
        Query results or execution status
    """
    try:
        import mysql.connector
        from mysql.connector import Error as MySQLError

        # Log connection attempt
        logger.info(f"Connecting to MySQL: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")

        # Connect to database
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        logger.info(f"Connected to MySQL successfully")

        # Convert params dict to tuple if needed
        if params and isinstance(params, dict):
            # Extract values in order of placeholders
            param_list = list(params.values())
            execute_params = tuple(param_list) if len(param_list) > 1 else param_list[0] if len(param_list) == 1 else ()
            logger.info(f"Executing SQL: {sql}")
            logger.info(f"Params: {execute_params}")
        else:
            execute_params = params or ()
            logger.info(f"Executing SQL: {sql}")

        # Execute query
        cursor.execute(sql, execute_params)

        # For SELECT queries, fetch results
        if sql.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            logger.info(f"SELECT query returned {len(results)} rows")

            if not results:
                return "No records found"

            # Format results
            formatted = []
            for row in results:
                row_str = " | ".join(f"{k}: {v}" for k, v in row.items())
                formatted.append(f"- {row_str}")

            result = f"Query results ({len(results)} records):\n\n" + "\n".join(formatted)
            return result
        else:
            # For INSERT/UPDATE/DELETE, commit and return status
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            logger.info(f"Query affected {affected} rows")

            if affected == 0:
                return f"Warning: No rows affected. SQL: {sql}"

            return f"OK: Query executed successfully. Rows affected: {affected}"

    except ImportError as e:
        logger.error(f"MySQL connector import error: {e}")
        return "Error: MySQL connector not installed. Please install: pip install mysql-connector-python"
    except MySQLError as e:
        logger.error(f"MySQL connection error: {e}")
        return f"Error: Database connection failed - {str(e)}\nConfig: host={MYSQL_CONFIG['host']}, port={MYSQL_CONFIG['port']}, database={MYSQL_CONFIG['database']}, user={MYSQL_CONFIG['user']}"
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return f"Error: Query execution failed - {str(e)}"


def validate_sql(sql: str) -> str:
    """
    Validate SQL query for security and correctness.

    Args:
        sql: SQL query to validate

    Returns:
        Validation result
    """
    try:
        sql_upper = sql.upper().strip()
        sql_lower = sql.lower().strip()

        # Check for dangerous operations
        dangerous_keywords = ["DROP", "DELETE DATABASE", "DELETE TABLE", "TRUNCATE"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return f"Error: Dangerous operation detected - {keyword} not allowed"

        # Check for valid SQL structure
        if not any(op in sql_upper for op in ["SELECT", "INSERT", "UPDATE", "DELETE"]):
            return "Error: Only SELECT, INSERT, UPDATE, DELETE operations are supported"

        # Check for required table reference
        if "transactions" not in sql_lower and "transaction_summary" not in sql_lower:
            return "Error: Query must reference 'transactions' or 'transaction_summary' table"

        return "OK: SQL validation passed"

    except Exception as e:
        return f"Error: Validation failed - {str(e)}"


def parse_date_range(date_range: str) -> Dict[str, str]:
    """
    Parse natural language date range into SQL date conditions.

    Args:
        date_range: Natural language date range (e.g., "last week", "yesterday")

    Returns:
        Dictionary with start_date and end_date conditions
    """
    try:
        today = datetime.now().date()
        date_lower = date_range.lower()

        conditions = {}

        if "today" in date_lower or "今天" in date_range:
            conditions["start_date"] = today
            conditions["end_date"] = today

        elif "yesterday" in date_lower or "昨天" in date_lower:
            yesterday = today - timedelta(days=1)
            conditions["start_date"] = yesterday
            conditions["end_date"] = yesterday

        elif "last week" in date_lower or "上周" in date_lower:
            # Calculate last Monday and last Sunday
            days_since_monday = today.weekday()
            last_monday = today - timedelta(days=days_since_monday + 7)
            last_sunday = last_monday + timedelta(days=6)
            conditions["start_date"] = last_monday
            conditions["end_date"] = last_sunday

        elif "this week" in date_lower or "本周" in date_lower:
            # Calculate this Monday and Sunday
            days_since_monday = today.weekday()
            this_monday = today - timedelta(days=days_since_monday)
            this_sunday = this_monday + timedelta(days=6)
            conditions["start_date"] = this_monday
            conditions["end_date"] = this_sunday

        elif "this month" in date_lower or "本月" in date_lower:
            first_day = today.replace(day=1)
            conditions["start_date"] = first_day
            conditions["end_date"] = today

        elif "last month" in date_lower or "上月" in date_lower:
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            conditions["start_date"] = first_day_last_month
            conditions["end_date"] = last_day_last_month

        else:
            # Default to today if unknown
            conditions["start_date"] = today
            conditions["end_date"] = today

        return conditions

    except Exception as e:
        logger.error(f"Date parsing error: {e}")
        # Fallback to today
        today = datetime.now().date()
        return {"start_date": today, "end_date": today}
