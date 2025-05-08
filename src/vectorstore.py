import os
import bs4

from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

MINIO_ACCESS_TOKEN = os.environ.get('MINIO_ACCESS_TOKEN', 'minioadmin:minioadmin')
MINIO_URI = os.environ.get('MINIO_URI', 'http://localhost:19530')


def init_vectorstore(collection_name: str) -> Milvus:
    """  Initialize a Milvus vectorstore """

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    vector_store = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={"uri": MINIO_URI, "token": MINIO_ACCESS_TOKEN},
        index_params={"index_type": "FLAT", "metric_type": "L2"},
        auto_id=True)

    return vector_store


def load_preprocess_data() -> list[Document]:
    """ Load and preprocess information before inserting into vector db """

    url = "https://lilianweng.github.io/posts/2023-06-23-agent/"
    soup_strainer = bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))

    loader = WebBaseLoader(
        web_paths=(url,),
        bs_kwargs=dict(parse_only=soup_strainer))

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1_000, chunk_overlap=200)
    doc_splits = text_splitter.split_documents(docs)

    return doc_splits


if __name__ == '__main__':
    vector_store = init_vectorstore(collection_name="blog_agents")

    data_splits = load_preprocess_data()

    _ = vector_store.add_documents(documents=data_splits)
