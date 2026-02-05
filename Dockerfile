FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Use mirror for faster downloads (China)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

# Install system dependencies with retry on network errors
RUN for i in 1 2 3 4 5; do \
    apt-get update && apt-get install -y gcc g++ libgmp-dev && rm -rf /var/lib/apt/lists/* && break || sleep 10; \
    done

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .
COPY frontend/ /app/frontend/

# Create necessary directories
RUN mkdir -p logs data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run the application
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
