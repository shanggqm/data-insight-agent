import argparse
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

from .utils import *
from .lindorm_vector_search import LindormVectorSearchClient
from .lindorm_wide_table import LindormWideTableClient


class LindormContext:
    def __init__(
        self,
        lindorm_search_client: LindormVectorSearchClient,
        lindorm_sql_client: LindormWideTableClient,
    ):
        self.lindorm_search_client = lindorm_search_client
        self.lindorm_sql_client = lindorm_sql_client


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[LindormContext]:
    """Manage application lifecycle for Lindorm"""
    config = server.config

    vector_search_client = LindormVectorSearchClient(
        search_host=config.get("lindorm_search_host"),
        ai_host=config.get("lindorm_ai_host"),
        username=config.get("username"),
        password=config.get("password"),
        text_embedding_model=config.get("text_embedding_model"),
    )

    sql_client = LindormWideTableClient(
        table_host=config.get("lindorm_table_host"),
        username=config.get("username"),
        password=config.get("password"),
        database=config.get("table_database"),
    )

    try:
        yield LindormContext(vector_search_client, sql_client)
    finally:
        pass


mcp = FastMCP("Lindorm", lifespan=server_lifespan, log_level="ERROR")


@mcp.tool()
def lindorm_retrieve_from_index(
    index_name: str,
    query: str,
    content_field: str,
    vector_field: str,
    top_k: int = 5,
    ctx: Context = None,
) -> str:
    """
    Retrieve from an existing indexes(or knowledgebase) using both full-text search and vector search, and return the aggregated results
    :param index_name: the index name, or known as knowledgebase name
    :param query: the query that you want to search in knowledgebase
    :param content_field: the text field that store the content text. You can get it from the index structure by lindorm_get_index_mappings tool
    :param vector_field: the vector field that store the vector index. You can get it from the index structure by lindorm_get_index_mappings tool
    :param top_k: the result number that you want to return
    :return: the most relevant content stored in the knowledgebase.
    """
    lindorm_search_client = ctx.request_context.lifespan_context.lindorm_search_client
    contents = lindorm_search_client.rrf_search(
        index_name, query, top_k, content_field, vector_field
    )

    # 完整结果用于缓存
    full_output = (
        f"The retrieving results for query {query} in knowledgebase {index_name} is\n"
    )
    full_output += "\n".join(
        f"{i + 1}. {content}" for i, content in enumerate(contents)
    )

    # 缓存完整结果
    cache_path = save_to_cache(
        "lindorm_retrieve_from_index",
        {
            "index_name": index_name,
            "query": query,
            "content_field": content_field,
            "vector_field": vector_field,
            "top_k": top_k,
        },
        full_output,
    )

    # 返回精简结果：前3条 + summary + 缓存路径
    total_count = len(contents)
    preview_contents = contents[:3]
    response = f"[Summary] Retrieved {total_count} results from knowledgebase '{index_name}' for query '{query}'\n\n"
    response += "[Preview - First 3 results]\n"
    response += "\n".join(
        f"{i + 1}. {content}" for i, content in enumerate(preview_contents)
    )
    if total_count > 3:
        response += f"\n\n... and {total_count - 3} more results"
    response += f"\n\n[Full results cached at] {cache_path}"

    return response


@mcp.tool()
def lindorm_get_index_fields(index_name: str, ctx: Context = None) -> str:
    """
    Get the fields info of the indexes(or knowledgebase), especially get the vector stored field and content stored field.
    :param index_name: the index name, or known as knowledgebase name
    :return: the index fields information
    """
    lindorm_search_client = ctx.request_context.lifespan_context.lindorm_search_client
    mapping = lindorm_search_client.get_index_mappings(index_name)
    fields_info = simplify_mappings(mapping, index_name)

    # 完整结果用于缓存
    full_output = f"The structure(mapping) of index {index_name} is\n"
    full_output += json.dumps(fields_info, indent=2, ensure_ascii=False)

    # 缓存完整结果
    cache_path = save_to_cache(
        "lindorm_get_index_fields", {"index_name": index_name}, full_output
    )

    # 返回精简结果：前3个字段 + summary + 缓存路径
    field_names = list(fields_info.keys()) if fields_info else []
    total_fields = len(field_names)
    preview_fields = {k: fields_info[k] for k in field_names[:3]} if fields_info else {}

    response = f"[Summary] Index '{index_name}' has {total_fields} fields\n\n"
    response += "[Preview - First 3 fields]\n"
    response += json.dumps(preview_fields, indent=2, ensure_ascii=False)
    if total_fields > 3:
        response += f"\n\n... and {total_fields - 3} more fields"
    response += f"\n\n[Full results cached at] {cache_path}"

    return response


@mcp.tool()
def lindorm_list_all_index(ctx: Context = None) -> str:
    """
    List all the indexes(or knowledgebase) you have.
    :return: all the indexes(or knowledgebase) you have
    """
    lindorm_search_client = ctx.request_context.lifespan_context.lindorm_search_client
    all_index = lindorm_search_client.list_indexes()

    # 完整结果用于缓存
    full_output = "All the knowledgebase you have are\n"
    full_output += "\n".join(f"{i + 1}. {index}" for i, index in enumerate(all_index))

    # 缓存完整结果
    cache_path = save_to_cache("lindorm_list_all_index", {}, full_output)

    # 返回精简结果：前3个索引 + summary + 缓存路径
    total_count = len(all_index)
    preview_indexes = all_index[:3]

    response = f"[Summary] Found {total_count} indexes/knowledgebases\n\n"
    response += "[Preview - First 3 indexes]\n"
    response += "\n".join(
        f"{i + 1}. {index}" for i, index in enumerate(preview_indexes)
    )
    if total_count > 3:
        response += f"\n\n... and {total_count - 3} more indexes"
    response += f"\n\n[Full results cached at] {cache_path}"

    return response


@mcp.tool()
def lindorm_execute_sql(query: str, ctx: Context = None) -> str:
    """
    Execute SQL query on Lindorm database.
    :param query: The SQL query to execute which start with select
    :return: the results of executing the sql or prompt when meeting certain types of exception
    """
    lindorm_sql_client = ctx.request_context.lifespan_context.lindorm_sql_client
    res = lindorm_sql_client.execute_query(query)

    # 完整结果用于缓存
    full_output = f"The results of executing sql {query} is\n"
    full_output += res

    # 缓存完整结果
    cache_path = save_to_cache("lindorm_execute_sql", {"query": query}, full_output)

    # 解析结果行数（第一行是header）
    lines = res.strip().split("\n") if res else []
    header = lines[0] if lines else ""
    data_rows = lines[1:] if len(lines) > 1 else []
    total_rows = len(data_rows)
    preview_rows = data_rows[:3]

    # 返回精简结果：前3行数据 + summary + 缓存路径
    response = f"[Summary] SQL query returned {total_rows} rows\n\n"
    response += f"[Preview - First 3 rows]\n{header}\n"
    response += "\n".join(preview_rows)
    if total_rows > 3:
        response += f"\n\n... and {total_rows - 3} more rows"
    response += f"\n\n[Full results cached at] {cache_path}"

    return response


@mcp.tool()
def lindorm_show_tables(ctx: Context = None) -> str:
    """
    Get all tables in the Lindorm database
    :return: the tables in the lindorm database
    """
    lindorm_sql_client = ctx.request_context.lifespan_context.lindorm_sql_client
    full_output = lindorm_sql_client.show_tables()

    # 缓存完整结果
    cache_path = save_to_cache("lindorm_show_tables", {}, full_output)

    # 解析结果（第一行是header）
    lines = full_output.strip().split("\n") if full_output else []
    header = lines[0] if lines else ""
    tables = lines[1:] if len(lines) > 1 else []
    total_tables = len(tables)
    preview_tables = tables[:3]

    # 返回精简结果：前3个表 + summary + 缓存路径
    response = f"[Summary] Found {total_tables} tables in database\n\n"
    response += f"[Preview - First 3 tables]\n{header}\n"
    response += "\n".join(preview_tables)
    if total_tables > 3:
        response += f"\n\n... and {total_tables - 3} more tables"
    response += f"\n\n[Full results cached at] {cache_path}"

    return response


@mcp.tool()
def lindorm_describe_table(table_name: str, ctx: Context = None) -> str:
    """
    Get tables schema in the Lindorm database
    :param table_name: the table name
    :return: the tables schema
    """
    lindorm_sql_client = ctx.request_context.lifespan_context.lindorm_sql_client
    full_output = lindorm_sql_client.describe_table(table_name)

    # 缓存完整结果
    cache_path = save_to_cache(
        "lindorm_describe_table", {"table_name": table_name}, full_output
    )

    # 解析结果（第一行是header）
    lines = full_output.strip().split("\n") if full_output else []
    header = lines[0] if lines else ""
    columns = lines[1:] if len(lines) > 1 else []
    total_columns = len(columns)
    preview_columns = columns[:3]

    # 返回精简结果：前3个字段 + summary + 缓存路径
    response = f"[Summary] Table '{table_name}' has {total_columns} columns\n\n"
    response += f"[Preview - First 3 columns]\n{header}\n"
    response += "\n".join(preview_columns)
    if total_columns > 3:
        response += f"\n\n... and {total_columns - 3} more columns"
    response += f"\n\n[Full results cached at] {cache_path}"

    return response


def parse_arguments():
    parser = argparse.ArgumentParser(description="LINDORM MCP Server")
    parser.add_argument("--lindorm_instance_id", type=str, help="Lindorm Search Host")
    parser.add_argument(
        "--using_vpc", type=bool, default=False, help="Whether to use the VPC network"
    )
    parser.add_argument("--username", type=str, default="root", help="Lindorm username")
    parser.add_argument("--password", type=str, help="Lindorm password")
    parser.add_argument("--embedding_model", type=str, help="Text Embedding Model Name")
    parser.add_argument(
        "--database",
        type=str,
        default="default",
        help="The Lindorm Database to execute sql",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_arguments()
    instance_id = os.environ.get("LINDORM_INSTANCE_ID", args.lindorm_instance_id)
    using_vpc_env = os.environ.get("USING_VPC_NETWORK")
    if using_vpc_env is not None:
        using_vpc = str_to_bool(using_vpc_env)
    else:
        using_vpc = args.using_vpc

    # 支持直接配置完整的主机地址，优先级高于通过 instance_id 拼接
    lindorm_search_host = os.environ.get(
        "LINDORM_SEARCH_HOST"
    ) or get_lindorm_search_host(instance_id, using_vpc)
    lindorm_ai_host = os.environ.get("LINDORM_AI_HOST") or get_lindorm_ai_host(
        instance_id, using_vpc
    )
    lindorm_table_host = os.environ.get("LINDORM_TABLE_HOST") or get_lindorm_table_host(
        instance_id, using_vpc
    )

    mcp.config = {
        "lindorm_search_host": lindorm_search_host,
        "lindorm_ai_host": lindorm_ai_host,
        "lindorm_table_host": lindorm_table_host,
        "username": os.environ.get("USERNAME", args.username),
        "password": os.environ.get("PASSWORD", args.password),
        "text_embedding_model": os.environ.get(
            "TEXT_EMBEDDING_MODEL", args.embedding_model
        ),
        "table_database": os.environ.get("TABLE_DATABASE", args.database),
    }
    mcp.run()


if __name__ == "__main__":
    main()
