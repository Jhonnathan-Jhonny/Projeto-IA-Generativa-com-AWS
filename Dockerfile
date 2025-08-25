# Usa uma imagem base oficial do Python
FROM python:3.9-slim-bullseye

# Atualiza e instala dependências do sistema/linguagem necessárias para ChromaDB e Python
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    unzip \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*
# Instala SQLite 3.42+ (necessário para ChromaDB)
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3420000.tar.gz \
    && tar xvfz sqlite-autoconf-3420000.tar.gz \
    && cd sqlite-autoconf-3420000 \
    && ./configure && make && make install \
    && cd .. && rm -rf sqlite-autoconf-3420000 sqlite-autoconf-3420000.tar.gz
ENV LD_LIBRARY_PATH="/usr/local/lib"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./ 
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]