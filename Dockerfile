FROM python:3.11-slim

WORKDIR /app

# Dependancies installations
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit port
EXPOSE 8501

# Lauching
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]