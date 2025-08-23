# Usa uma imagem base oficial do Python
FROM python:3.9-slim-bullseye

# Atualiza e instala dependências do sistema necessárias para ChromaDB e Python
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instala SQLite 3.42+ (necessário para ChromaDB)
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3420000.tar.gz \
    && tar xvfz sqlite-autoconf-3420000.tar.gz \
    && cd sqlite-autoconf-3420000 \
    && ./configure && make && make install \
    && cd .. && rm -rf sqlite-autoconf-3420000 sqlite-autoconf-3420000.tar.gz

# Configura o Python para usar a nova versão do SQLite
ENV LD_LIBRARY_PATH="/usr/local/lib"

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos do back-end
COPY src/ ./ 

# Expõe a porta do back-end (FastAPI ou Flask)
EXPOSE 80

# Comando para rodar a aplicação
# Substitua 'main:app' pelo arquivo e nome da instância da sua aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]