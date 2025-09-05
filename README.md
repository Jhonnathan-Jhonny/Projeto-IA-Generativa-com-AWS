# Projeto 4 – Chatbot Jurídico com RAG e AWS Bedrock  
**Sprint 7 e 8 – Scholarship Compass UOL – Formação em Inteligência Artificial para AWS**

## 📌 Visão Geral
Este projeto consiste na implementação de um **chatbot jurídico** utilizando a arquitetura **RAG (Retrieval-Augmented Generation)**.  
O sistema realiza consultas em uma base de documentos jurídicos armazenada no **Amazon S3**, gera embeddings com **Amazon Bedrock**, indexa com **ChromaDB** e expõe a interface de interação via **Telegram**.  

Toda a orquestração do fluxo é feita a partir de uma **instância EC2**, sendo acionada por um **Lambda** que recebe gatilhos do **API Gateway**, com monitoramento de logs via **Amazon CloudWatch**.  

---

## 🏗️ Arquitetura
Fluxo principal:
1. Usuários enviam mensagens ao chatbot pelo **Telegram**.  
2. O **API Gateway** recebe a requisição.  
3. O **Lambda** é acionado e redireciona a requisição para a aplicação rodando em uma **instância EC2**.  
4. A aplicação na **EC2**, utilizando **LangChain**, realiza:  
   - Leitura de documentos jurídicos armazenados no **S3 (dataset jurídico)**;  
   - Criação de embeddings utilizando **Amazon Bedrock**;  
   - Indexação dos embeddings no **ChromaDB** para recuperação eficiente;  
   - Execução do mecanismo de **RAG** (busca + geração de resposta).  
5. A resposta é enviada de volta ao usuário via **Telegram**.  
6. Logs e eventos são registrados no **Amazon CloudWatch**.  

---

## ⚙️ Tecnologias Utilizadas
- **AWS**
  - Amazon S3 → armazenamento dos documentos jurídicos  
  - Amazon Bedrock → geração de embeddings e consultas  
  - Amazon EC2 → execução da aplicação  
  - Amazon API Gateway → exposição da API para o Telegram  
  - AWS Lambda → intermediação entre API Gateway e EC2  
  - Amazon CloudWatch → monitoramento e logging  

- **Frameworks/Bibliotecas**
  - Python 3.x  
  - [LangChain](https://python.langchain.com/) → orquestração do RAG  
  - [LangChain AWS](https://pypi.org/project/langchain-aws/) → integração com Bedrock  
  - [LangChain Community](https://pypi.org/project/langchain-community/) → loaders e utilidades  
  - [ChromaDB](https://www.trychroma.com/) → armazenamento vetorial  
  - [unstructured](https://unstructured-io.github.io/unstructured/) → processamento de PDFs  
  - PyPDFLoader (LangChain) → carregamento de documentos PDF  
  - [FastAPI](https://fastapi.tiangolo.com/) → criação da API  
  - [Uvicorn](https://www.uvicorn.org/) → servidor ASGI  
  - [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) → integração com Telegram  
  - [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) → SDK AWS  

---

## 📂 Estrutura de Pastas
```bash
📦 projeto-chatbot
 ┣ 📂 src/
 ┃ ┣ 📂 indexing/    # carregamento de dados, geração de embeddings e armazenamento (ChromaDB)
 ┃ ┣ 📂 llm/         # acesso ao LLM
 ┃ ┣ 📂 rag/         # consultas e RAG com LangChain
 ┃ ┣ main.py
 ┣ Dockerfile
 ┣ README.md
 ┣ testes.txt
 ┗ requirements.txt