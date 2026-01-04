FROM python:3.11-slim

WORKDIR /app

# 安裝 FFmpeg 和 Node.js (pytubefix WEB client 需要 Node.js 來生成 PO Token)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN ffmpeg -version
RUN node --version

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p downloads

EXPOSE 8080

CMD gunicorn app_pytubefix:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300
