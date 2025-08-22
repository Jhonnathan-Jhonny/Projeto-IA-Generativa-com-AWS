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

    # === Configuração AWS ===
# PROFILE_NAME="default"
BUCKET_NAME = "juridicosprojeto4"
PREFIX = "juridicos/"

def silent_load(loader):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        return loader.load()

# === Criação do índice vetorial ===
def hr_index():
    try:
        # Testa conexão S3
        session = boto3.Session(
            # profile_name=PROFILE_NAME,
        )
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
            # credentials_profile_name=PROFILE_NAME,
            region_name="us-east-1",
            model_id="amazon.titan-embed-text-v1"
        )

        # Cria índice vetorial com Chroma
        index_creator = VectorstoreIndexCreator(
            text_splitter=text_splitter,
            embedding=embeddings,
            vectorstore_cls=Chroma
        )

        print("🔎 Criando índice vetorial...")
        return index_creator.from_documents(documents)

    except Exception as e:
        print(f"💥 Erro: {str(e)}")
        raise

# === Modelo de LLM ===
def hr_llm():
    return BedrockLLM(
        # credentials_profile_name=PROFILE_NAME,
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

                    # Testes
# "Quem são as partes envolvidas no processo?"
# Resposta esperada: Instituto de Hematologia e Hemoterapia de Sergipe (embargante) e Fundação de Saúde Parreiras Horta (embargado)

# "Qual é o objeto da controvérsia?"
# Resposta esperada: Cobrança por serviços de exames sorológicos realizados e discussão sobre validade de contrato verbal com a administração pública

# "Qual foi o resultado dos embargos de declaração?"
# Resposta esperada: Embargos conhecidos mas desprovidos (negado provimento)

# "Qual fundamento legal foi utilizado para invalidar o contrato verbal?"
# Resposta esperada: Artigo 60 da Lei Federal nº 8.666/93 (Lei de Licitações)

# "Qual o valor da dívida discutida no processo?"
# Resposta esperada: R$ 178.265,86

# "Qual o tipo de ação processual discutida?"
# Resposta esperada: Ação Monitória com Embargos Monitórios

# "Qual o argumento principal do embargante para contestar o valor?"
# Resposta esperada: Alegava excesso de cobrança e que o preço deveria ser baseado na tabela do IHENE (Instituto de Hematologia do Nordeste)

# "Qual tribunal julgou o processo?"
# Resposta esperada: Tribunal de Justiça do Estado de Sergipe

# "Houve aplicação de multa por embargos protelatórios? E o Porque?"
# Resposta esperada: Não, pois não foi caracterizado caráter protelatório