FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Flask app typically runs on 5000, but Cloud Run/App Hosting expects 8080 or PORT env var
# Port is specified by the environment
CMD gunicorn --bind 0.0.0.0:$PORT app:app
