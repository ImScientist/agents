import os
import logging
import bs4

from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

MINIO_ACCESS_TOKEN = os.environ['MINIO_ACCESS_TOKEN']
MINIO_URI = os.environ['MINIO_URI']


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


def load_preprocess_data(
        url: str = "https://lilianweng.github.io/posts/2023-06-23-agent/",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
) -> list[Document]:
    """ Load and preprocess information before inserting into vector db """

    soup_strainer = bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))

    loader = WebBaseLoader(
        web_paths=(url,),
        bs_kwargs=dict(parse_only=soup_strainer))

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap)

    doc_splits = text_splitter.split_documents(docs)

    logger.info(f"Successfully loaded and split {len(doc_splits)} documents from {url}")

    return doc_splits


if __name__ == '__main__':
    vector_store = init_vectorstore(collection_name="blog_agents")
    data_splits = load_preprocess_data()
    vector_store.add_documents(documents=data_splits)
    logger.info("Successfully populated vectorstore")
