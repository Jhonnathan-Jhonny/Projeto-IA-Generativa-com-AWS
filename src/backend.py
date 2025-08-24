import os
import boto3
from langchain_community.document_loaders import S3DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings, BedrockLLM
from langchain_community.vectorstores import Chroma
from langchain.indexes import VectorstoreIndexCreator
import warnings
import contextlib
import sys
import io

# === Configuração ===
BUCKET_NAME = "juridicosprojeto4"
PREFIX = "juridicos/"
CHROMA_PERSIST_DIR = "/tmp/chroma_db"  # Para Lambda, use /tmp

# Variável global para cache do índice
cached_index = None

def silent_load(loader):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        return loader.load()

# === Criação do índice vetorial (com cache) ===
def hr_index():
    global cached_index
    
    # Se já temos o índice em cache, retorna
    if cached_index is not None:
        print("✅ Retornando índice do cache")
        return cached_index
    
    try:
        # Verifica se já existe ChromaDB persistido
        if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
            print("📂 Carregando índice persistido do ChromaDB...")
            embeddings = BedrockEmbeddings(
                region_name="us-east-1",
                model_id="amazon.titan-embed-text-v1"
            )
            
            # Carrega o ChromaDB existente
            vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=embeddings
            )
            
            cached_index = VectorstoreIndexCreator(
                vectorstore=vectorstore
            ).from_vectorstore(vectorstore)
            
            return cached_index

        # Se não existe, cria novo índice
        print("🆕 Criando novo índice vetorial...")
        
        # Testa conexão S3
        session = boto3.Session()
        s3 = session.client("s3")
        s3.head_bucket(Bucket=BUCKET_NAME)
        print("✅ Conexão com S3 validada")

        # Carregar PDFs do bucket
        loader = S3DirectoryLoader(bucket=BUCKET_NAME, prefix=PREFIX)
        documents = silent_load(loader)
        print(f"📄 Total de documentos carregados: {len(documents)}")

        if not documents:
            raise RuntimeError("Nenhum documento encontrado no S3.")

        # Quebra documentos em pedaços
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

        # Embeddings (Titan)
        embeddings = BedrockEmbeddings(
            region_name="us-east-1",
            model_id="amazon.titan-embed-text-v1"
        )

        # Cria índice vetorial com Chroma e persiste
        index_creator = VectorstoreIndexCreator(
            text_splitter=text_splitter,
            embedding=embeddings,
            vectorstore_cls=Chroma,
            vectorstore_kwargs={
                "persist_directory": CHROMA_PERSIST_DIR
            }
        )

        print("🔎 Criando e persistindo índice vetorial...")
        cached_index = index_creator.from_documents(documents)
        
        # Persiste o ChromaDB
        cached_index.vectorstore.persist()
        
        return cached_index

    except Exception as e:
        print(f"💥 Erro: {str(e)}")
        raise

# === Modelo de LLM ===
def hr_llm():
    return BedrockLLM(
        model_id="amazon.titan-text-premier-v1:0",
        region_name="us-east-1",
        model_kwargs={
            "temperature": 0.3,
            "maxTokenCount": 2048
        }
    )

# === Função de RAG ===
def hr_rag_response(index, question: str):
    rag_llm = hr_llm()
    return index.query(question=question, llm=rag_llm)