# 使用官方 Python 映像
FROM python:3.11-slim

# 安裝 ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY . .

# 建立下載目錄
RUN mkdir -p downloads

# 暴露埠號
EXPOSE 8080

# 啟動應用程式
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "300", "app:app"]
