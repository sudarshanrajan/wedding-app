# Dockerfile

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y build-essential nginx xclip && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create working directory
WORKDIR /app
COPY . /app

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

RUN chmod +x app/entrypoint.sh

EXPOSE 80

# entrypoint
CMD ["app/entrypoint.sh"]
