docker build -t wedding-app .
docker run -p 8501:8501 -v $PWD/data:/app/data -v $PWD/static:/app/static wedding-app
