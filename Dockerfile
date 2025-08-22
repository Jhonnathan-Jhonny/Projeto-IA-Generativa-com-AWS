# Usa uma imagem base oficial do Python
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da sua aplicação (backend.py e frontend.py)
# Certifique-se de que o caminho 'src/' está correto em relação à raiz do seu contexto Docker
COPY src/backend.py .
COPY src/frontend.py .

# Expõe a porta que o Streamlit usa por padrão
EXPOSE 80

# Define a variável de ambiente para que o Streamlit não abra o navegador
ENV STREAMLIT_SERVER_PORT=80 \
    STREAMLIT_SERVER_HEADLESS=true

# Comando para iniciar a aplicação Streamlit
# O backend.py será importado por frontend.py, então basta rodar o frontend
CMD ["streamlit", "run", "frontend.py"]