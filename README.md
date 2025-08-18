# Projeto 4 – Chatbot Jurídico com RAG e AWS Bedrock  
**Sprint 7 e 8 – Scholarship Compass UOL – Formação em Inteligência Artificial para AWS**

## 📌 Visão Geral
Este projeto consiste na implementação de um **chatbot jurídico** utilizando a arquitetura **RAG (Retrieval-Augmented Generation)**.  
O sistema realiza consultas em uma base de documentos jurídicos armazenada no **Amazon S3**, gera embeddings com **Amazon Bedrock**, indexa com **ChromaDB** e expõe a interface de interação via **Telegram**.  

Toda a orquestração do fluxo é feita a partir de uma **instância EC2**, com monitoramento de logs via **Amazon CloudWatch**.

---

## 🏗️ Arquitetura
Fluxo principal:
1. Usuários enviam mensagens ao chatbot pelo **Telegram**.  
2. O **API Gateway** recebe a requisição e encaminha para a aplicação.  
3. A aplicação (rodando em uma **instância EC2**) utiliza o **LangChain** para:  
   - Ler documentos armazenados no **S3 (dataset jurídico)**.  
   - Criar embeddings utilizando **Amazon Bedrock**.  
   - Indexar embeddings no **ChromaDB** para recuperação eficiente.  
   - Executar o mecanismo de **RAG** (busca + geração).  
4. A resposta é enviada de volta ao usuário no **Telegram**.  
5. Todos os eventos são registrados no **Amazon CloudWatch**.  

---

## ⚙️ Tecnologias Utilizadas
- **AWS**
  - Amazon S3 → armazenamento dos documentos jurídicos  
  - Amazon Bedrock → geração de embeddings e consultas  
  - Amazon EC2 → execução da aplicação  
  - Amazon API Gateway → exposição da API para o Telegram  
  - Amazon CloudWatch → monitoramento e logging  

- **Frameworks/Bibliotecas**
  - Python 3.x  
  - [LangChain](https://python.langchain.com/) → orquestração do RAG  
  - [ChromaDB](https://www.trychroma.com/) → armazenamento vetorial  
  - PyPDFLoader (LangChain) → carregamento de documentos em PDF  
  - [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) → integração com Telegram  

---

## 📂 Estrutura de Pastas
```bash
📦 projeto-chatbot
 ┣ 📂 dataset/             # documentos jurídicos em PDF
 ┣ 📂 src/
 ┃ ┣ 📂 loaders/           # carregamento de dados (PyPDFLoader, S3)
 ┃ ┣ 📂 embeddings/        # geração de embeddings com Bedrock
 ┃ ┣ 📂 retrieval/         # consultas e RAG com LangChain + Chroma
 ┃ ┣ 📂 telegram/          # integração com Telegram Bot API
 ┃ ┗ 📂 utils/             # funções auxiliares e logging
 ┣ 📂 infra/
 ┃ ┣ api_gateway.yaml      # configuração do API Gateway
 ┃ ┣ ec2_setup.sh          # script de provisionamento EC2
 ┃ ┗ cloudwatch_config/    # regras de log
 ┣ README.md
 ┗ requirements.txt
