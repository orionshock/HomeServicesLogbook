FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Optional but helpful for clean signal handling
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY templates ./templates

# Create runtime data dirs inside container
RUN mkdir -p /data/uploads

# Runtime defaults for container
ENV APP_DATA_DIR=/data
ENV APP_UPLOADS_DIR=/data/uploads
ENV APP_DB_PATH=/data/logbook.db
ENV APP_ROOT_PATH=

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]