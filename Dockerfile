# Usa uma imagem base oficial do Python
FROM python:3.9-slim-bullseye

# Atualiza e instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação
COPY src/ ./

# Expõe a porta do Streamlit
EXPOSE 80

# Variáveis de ambiente para Streamlit
ENV STREAMLIT_SERVER_PORT=80 \
    STREAMLIT_SERVER_HEADLESS=true

# Comando para rodar a aplicação
CMD ["streamlit", "run", "frontend.py"]
