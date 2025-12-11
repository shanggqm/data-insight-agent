import mysql.connector
from mysql.connector import Error


class LindormWideTableClient:
    def __init__(self, table_host: str, username: str, password: str, database='default'):
        self.config = {
            'host': table_host,
            'port': 33060,
            'user': username,
            'password': password,
            'database': database
        }
        self.connection = None
        self.cursor = None
        self._connect()

    def _connect(self):
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self._close()

    def _close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def show_tables(self) -> str:
        try:
            self.cursor.execute(f"SHOW TABLES")
            tables = self.cursor.fetchall()
            result = ["Tables_in_" + self.config["database"]]  # Header
            result.extend([table[0] for table in tables])
            return "\n".join(result)
        except Error as e:
            return f"Error executing SHOW TABLES: {str(e)}"

    def describe_table(self, table_name: str) -> str:
        try:
            self.cursor.execute(f"DESCRIBE TABLE {table_name}")
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            result = [",".join(map(str, row)) for row in rows]
            return "\n".join([",".join(columns)] + result)
        except Error as e:
            return f"Error executing DESCRIBE TABLE {table_name}: {str(e)}"

    def execute_query(self, query: str) -> str:
        """Execute SQL commands."""
        try:
            if not query.strip().upper().startswith("SELECT"):
                return (f"Query should start with SELECT. " +
                        "Example: SELECT * FROM table ")

            self.cursor.execute(query)
            # Regular SELECT queries
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            result = [",".join(map(str, row)) for row in rows]
            return "\n".join([",".join(columns)] + result)
        except Error as e:
            error_msg = str(e)
            if "Detect inefficient query" in error_msg:
                return ("Your query was identified as inefficient. " +
                        "Please add /*+ _l_allow_filtering_ */ hint after the SELECT keyword.\n" +
                        "Example: SELECT /*+ _l_allow_filtering_ */ * FROM table\n" +
                        "Instead of: SELECT * FROM table")
            elif "JOIN is not allowed" in error_msg or "UNION is not allowed" in error_msg:
                return "JOIN UNION is not allowed. Please execute 'ALTER SYSTEM SET `lindorm.sql.join_union.disabled`=FALSE' to enable join."
            return f"Error executing query: {str(e)}"

    def reconnect(self):
        """Reconnect to the database."""
        self._close()
        self._connect()
