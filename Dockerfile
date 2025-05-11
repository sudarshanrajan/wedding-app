# Dockerfile

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

# Install dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create working directory
WORKDIR /app
COPY . /app

# Streamlit entrypoint
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.enableCORS=false", "--server.headless=true"]
