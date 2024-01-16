########################################################################################################################################################################

# REFERENCE : https://github.com/GoogleCloudPlatform/generative-ai/blob/main/language/use-cases/document-qa/question_answering_documents_langchain_matching_engine.ipynb

########################################################################################################################################################################

import os
import time
import logging
import vertexai

import json
import uuid
import numpy as np 

from typing import List, Tuple

from matching_engine.matching_engine_utils import MatchingEngineUtils
from langchain_community.vectorstores.matching_engine import MatchingEngine
from langchain.embeddings import VertexAIEmbeddings

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VECTORSTORE")


vertexai.init(project=os.environ.get("PROJECT_ID"), location=os.environ.get("REGION"))


def rate_limit(max_per_minute):
    """
    A generator function that ensures a maximum number of operations per minute.
    This function is used to rate limit operations that are executed in a loop. 
    It calculates the time taken for an operation and sleeps for the remaining time 
    to ensure that the maximum number of operations per minute is not exceeded.
    Args:
        max_per_minute (int): The maximum number of operations that can be performed per minute.
    Yields:
        None: Yields None and sleeps for the calculated time period if necessary.
    """
    period = 60 / max_per_minute
    logger.info("Waiting")
    while True:
        before = time.time()
        yield
        after = time.time()
        elapsed = after - before
        sleep_time = max(0, period - elapsed)
        if sleep_time > 0:
            print(".", end="")
            time.sleep(sleep_time)


class CustomVertexAIEmbeddings(VertexAIEmbeddings):
    requests_per_minute: int
    num_instances_per_batch: int

    # Overriding embed_documents method
    def embed_documents(self, texts: List[str]):
        limiter = rate_limit(self.requests_per_minute)
        results = []
        docs = list(texts)

        while docs:
            # Working in batches because the API accepts maximum 5
            # documents per request to get embeddings
            head, docs = (
                docs[: self.num_instances_per_batch],
                docs[self.num_instances_per_batch :],
            )
            chunk = self.client.get_embeddings(head)
            results.extend(chunk)
            next(limiter)
        return [r.values for r in results]
    


def initialise_index_folder(path: str, embeddings_dimension: int = 768):
    # dummy embedding
    init_embedding = {"id": str(uuid.uuid4()), "embedding": list(np.zeros(embeddings_dimension))}
    # dump embedding to a local file
    with open("init_embeddings.json", "w") as f:
        json.dump(init_embedding, f)
    # write embedding to Cloud Storage
    os.system(f"set -x && gsutil cp init_embeddings.json gs://{path}/init_embeddings.json")

    
def get_matching_engine_and_deploy_index(
    index_name: str = "orange_index",
    embeddings_qpm: int = 100,
    embedding_num_batch: int = 5,
    embeddings_dimension: int = 768,
    embeddings_gcs_dir: str = "init_folder"
) -> Tuple[MatchingEngine, str, str]:
    """
    Creates, deploy index and return vertex matching engine object (vectorstore).
    Args:
        index_name (str, optional): The name of the matching engine index that will be created. Defaults to "me_index".
        embeddings_qpm (int, optional): The number of queries per minute for the embeddings. Defaults to 100.
        embedding_num_batch (int, optional): The number of instances per batch for the embeddings. Defaults to 5.
        embeddings_dimension (int, optional): number of dimensions for the embeddings
        embeddings_gcs_dir  (str, optional): Directory where the embeddings are stored. 

    Returns:
        MatchingEngineRetriever: A retriever to be used with langchain Chain objects mainly for Q&A.
    """

    embeddings = CustomVertexAIEmbeddings(
        location=os.environ.get("REGION"),
        project_id=os.environ.get("PROJECT_ID"),
        requests_per_minute=embeddings_qpm,
        num_instances_per_batch=embedding_num_batch,
    )
    
    # initialize file for index creation
    initialise_index_folder(path=f"{os.environ.get('BUCKET_NAME')}/{embeddings_gcs_dir}")
    
    
    # Create and deploy a matching engine endpoint
    index_maker = MatchingEngineUtils(os.environ.get('PROJECT_ID'), os.environ.get('REGION'), index_name)
    logger.info(f"Creating index from gs://{os.environ.get('BUCKET_NAME')}/{embeddings_gcs_dir}, this step can take a while ...")
    index_maker.create_index(
        embedding_gcs_uri=f"gs://{os.environ.get('BUCKET_NAME')}/{embeddings_gcs_dir}",
        dimensions=embeddings_dimension,
        index_update_method="batch",
        index_algorithm="tree-ah",
    )
    
    logger.info("Deploying index, this step can take a while ...")
    index_maker.deploy_index()
    
    # Expose matching engine to index
    ME_INDEX_ID, ME_INDEX_ENDPOINT_ID = index_maker.get_index_and_endpoint()
    mengine = MatchingEngine.from_components(
        project_id=os.environ.get('PROJECT_ID'),
        region=os.environ.get('REGION'),
        gcs_bucket_name=os.environ.get("BUCKET_NAME"),
        embedding=embeddings,
        index_id=ME_INDEX_ID,
        endpoint_id=ME_INDEX_ENDPOINT_ID,
    )
    return mengine, ME_INDEX_ID, ME_INDEX_ENDPOINT_ID


def add_documents_to_matching_engine(
    matching_engine: MatchingEngine,
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 50,
    separators: List[str]=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
) -> None :
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators
    )
    #logger.info(f"Using {RecursiveCharacterTextSplitter} for chuncks creation ...")
    doc_splits = text_splitter.split_documents(documents)
    for idx, split in enumerate(doc_splits):
        split.metadata["chunk"] = idx
    texts = [doc.page_content for doc in doc_splits]
    metadatas = [
        [
            {"namespace": "source", "allow_list": [doc.metadata["source"]]},
            {"namespace": "chunk", "allow_list": [str(doc.metadata["chunk"])]},
        ]
        for doc in doc_splits
    ]
    logger.info("Adding documents to vectorstore ...")
    matching_engine.add_texts(texts=texts, metadatas=metadatas)
