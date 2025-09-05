import os
import boto3
from langchain_community.document_loaders import S3DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings, BedrockLLM
from langchain_community.vectorstores import Chroma
from langchain.indexes import VectorstoreIndexCreator
import contextlib
import io


BUCKET_NAME = "juridicosprojeto4"
PREFIX = "juridicos/"
CHROMA_PERSIST_DIR = "/tmp/chroma_db"

# Variável global para cache do índice
cached_index = None

def silent_load(loader):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        return loader.load()

# === Criação do índice vetorial (com cache) ===
def hr_index():
    global cached_index
    
    if cached_index is not None:
        return cached_index
    
    try:
        # Verifica se já existe ChromaDB persistido
        if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
            embeddings = BedrockEmbeddings(
                region_name="us-east-1",
                model_id="amazon.titan-embed-text-v1"
            )
            
            vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=embeddings
            )
            
            cached_index = VectorstoreIndexCreator(
                vectorstore=vectorstore
            ).from_vectorstore(vectorstore)
            
            return cached_index
        
        session = boto3.Session()
        s3 = session.client("s3")
        s3.head_bucket(Bucket=BUCKET_NAME)

        loader = S3DirectoryLoader(bucket=BUCKET_NAME, prefix=PREFIX)
        documents = silent_load(loader)

        if not documents:
            raise RuntimeError("Nenhum documento encontrado no S3.")

        # Quebra documentos em pedaços
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

        embeddings = BedrockEmbeddings(
            region_name="us-east-1",
            model_id="amazon.titan-embed-text-v1"
        )

        index_creator = VectorstoreIndexCreator(
            text_splitter=text_splitter,
            embedding=embeddings,
            vectorstore_cls=Chroma,
            vectorstore_kwargs={
                "persist_directory": CHROMA_PERSIST_DIR
            }
        )

        cached_index = index_creator.from_documents(documents)
        
        cached_index.vectorstore.persist()
        
        return cached_index

    except Exception as e:
        print(f"💥 Erro: {str(e)}")
        raise