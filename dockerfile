FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY /models/ /models/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]]
