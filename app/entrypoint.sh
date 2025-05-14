#!/bin/bash

echo "Starting FastAPI..."
uvicorn app.data_server:app --host 0.0.0.0 --port 8000 &

echo "Starting Streamlit..."
streamlit run app/web_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.baseUrlPath app &

echo "Starting Nginx..."
nginx -g "daemon off;"