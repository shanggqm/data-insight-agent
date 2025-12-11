import pytest
from src.lindorm_mcp_server.lindorm_wide_table import LindormWideTableClient

TABLE_HOST = ""
DATABASE_NAME = "default"
USERNAME = ""
PASSWORD = ""
TABLE_NAME = ""


@pytest.fixture(scope="module")
def sql_client():
    return LindormWideTableClient(TABLE_HOST, USERNAME, PASSWORD, DATABASE_NAME)


def test_lindorm_execute_sql_simple(sql_client):
    query = "SHOW TABLES;"
    sql_results = sql_client.execute_query(query)
    print(f"Sql execution results: {sql_results}")


def test_lindorm_execute_sql_select(sql_client):
    query = f"SELECT * FROM {TABLE_NAME} LIMIT 2"
    sql_results = sql_client.execute_query(query)
    print(f"Sql execution results: {sql_results}")
