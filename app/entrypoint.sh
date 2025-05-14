#!/bin/bash
echo "hello from entrypoint!"
uvicorn app.data_server:app --host 0.0.0.0 &

streamlit run app/web_app.py
