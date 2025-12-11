import pytest
from src.lindorm_mcp_server.lindorm_vector_search import LindormVectorSearchClient

# 你需要提供实际的连接信息
SEARCH_HOST = ""
AI_HOST = ""
USERNAME = ""
PASSWORD = ""
TEXT_EMBEDDING_MODEL = ""
TEST_INDEX_NAME = ""
CONTENT_FIELD = ""
VECTOR_FIELD = ""


@pytest.fixture(scope="module")
def search_client():
    return LindormVectorSearchClient(SEARCH_HOST, AI_HOST, USERNAME, PASSWORD, TEXT_EMBEDDING_MODEL)


def test_lindorm_search_list_indexes(search_client):
    indexes = search_client.list_indexes()
    assert isinstance(indexes, list)
    assert len(indexes) > 0
    print(f"Found indexes: {indexes}")


def test_lindorm_search_get_index_mapping(search_client):
    mapping = search_client.get_index_mappings(TEST_INDEX_NAME)
    assert mapping is not None
    assert TEST_INDEX_NAME in mapping
    print(f"Index mapping: {mapping}")


def test_lindorm_search_rrf_search(search_client):
    results = search_client.rrf_search(TEST_INDEX_NAME, "test query", 5, CONTENT_FIELD, VECTOR_FIELD)
    assert isinstance(results, list)
    assert len(results) <= 5
    print(f"RRF search results: {results}")


def test_lindorm_search_full_text_search(search_client):
    results = search_client.full_text_search(TEST_INDEX_NAME, "test query", 5, CONTENT_FIELD)
    assert isinstance(results, list)
    assert len(results) <= 5
    print(f"Full text search results: {results}")


def test_lindorm_search_vector_search(search_client):
    results = search_client.vector_search(TEST_INDEX_NAME, "test query", 5, CONTENT_FIELD, VECTOR_FIELD)
    assert isinstance(results, list)
    assert len(results) <= 5
    print(f"Vector search results: {results}")
