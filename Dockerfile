FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Download Overkiz certificate
RUN curl -o overkiz-root-ca-2048.crt https://ca.overkiz.com/overkiz-root-ca-2048.crt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Singapore

EXPOSE 3888

CMD ["python", "bus_server.py"]