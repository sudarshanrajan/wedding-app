#!/bin/bash
echo "hello"
echo "$DATA_SERVER_PORT"
uvicorn app.data_server:app --host 0.0.0.0 --port $DATA_SERVER_PORT &

streamlit run app/web_app.py --server.port $WEB_APP_PORT
