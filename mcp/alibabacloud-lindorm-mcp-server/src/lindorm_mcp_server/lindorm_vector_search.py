import logging
from opensearchpy import OpenSearch
from .utils import text_embedding


class LindormVectorSearchClient:
    def __init__(self, search_host: str, ai_host: str, username: str, password: str, text_embedding_model: str):
        self.search_host = search_host
        self.username = username
        self.password = password
        self.client = OpenSearch(
            hosts=[{'host': self.search_host, 'port': 30070}],
            http_auth=(self.username, self.password),
            use_ssl=False,
        )
        self.ai_host = ai_host
        self.text_embedding_model = text_embedding_model

    def _check_index_exist(self, index_name: str) -> bool:
        try:
            return self.client.indices.exists(index=index_name)
        except Exception as e:
            # 处理可能的异常
            logging.error(f"client call check_index_exist exception {index_name}: {e}")
            return False

    def _embedding_query(self, query: str) -> list[float]:
        code, res_or_exception = text_embedding(self.ai_host, self.username, self.password, self.text_embedding_model,
                                                query)
        if code < 0:
            raise RuntimeError(f"failed to get embedding, cause:{res_or_exception}")
        assert isinstance(res_or_exception, list)
        return res_or_exception[0]

    def list_indexes(self) -> list[str]:
        try:
            indices = self.client.cat.indices(format="json")
            index_names = [index['index'] for index in indices]
            return index_names
        except Exception as e:
            logging.error(f"Error listing indexes: {e}")
            return []

    def get_index_mappings(self, index_name: str):
        try:
            mappings = self.client.indices.get_mapping(index=index_name)
            return mappings
        except Exception as e:
            logging.error(f"Error getting mappings for index {index_name}: {e}")
            return None

    def full_text_search(self, index_name: str, query_text: str, size: int, content_field: str) -> list[str]:
        if not self._check_index_exist(index_name):
            return [f"{index_name} not exist"]
        query = {
            "size": size,
            "_source": [content_field],
            "query": {
                "match": {
                    content_field: query_text
                }
            }
        }

        try:
            response = self.client.search(
                body=query,
                index=index_name
            )
            return [hit["_source"][content_field] for hit in response['hits']['hits']]
        except Exception as e:
            logging.error(f"Error performing full text search: {e}")
            return []

    def vector_search(self, index_name: str, query_text: str, top_k: int, content_field: str, vector_field: str) -> list[str]:
        if not self._check_index_exist(index_name):
            return [f"{index_name} not exist"]
        vector = self._embedding_query(query_text)
        query = {
            "size": top_k,
            "_source": [content_field],
            "query": {
                "knn": {
                    vector_field: {
                        "vector": vector,
                        "k": top_k
                    }
                }
            },
        }
        try:
            response = self.client.search(
                body=query,
                index=index_name
            )
            return [hit["_source"][content_field] for hit in response['hits']['hits']]
        except Exception as e:
            logging.error(f"Error performing vector search: {e}")
            return []

    def rrf_search(self, index_name: str, query_text: str, top_k: int, content_field: str, vector_field: str) -> list[str]:
        if not self._check_index_exist(index_name):
            return [f"{index_name} not exist"]
        vector = self._embedding_query(query_text)
        query = {
            "size": top_k,
            "_source": [content_field],
            "query": {
                "knn": {
                    vector_field: {
                        "vector": vector,
                        "filter": {
                            "match": {
                                content_field: query_text
                            }
                        },
                        "k": top_k
                    }
                }
            },
            "ext": {
                "lvector": {
                    "hybrid_search_type": "filter_rrf",
                    "rrf_rank_constant": "60",
                }
            }
        }
        try:
            response = self.client.search(
                body=query,
                index=index_name
            )
            return [hit["_source"][content_field] for hit in response['hits']['hits']]
        except Exception as e:
            logging.error(f"Error performing RRF search: {e}")
            return []
