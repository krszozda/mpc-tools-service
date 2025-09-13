# MPC Tools Service Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY proto/ ./proto/

# Generate protobuf files
RUN python -m grpc_tools.protoc \
    --proto_path=./proto \
    --python_out=./src \
    --grpc_python_out=./src \
    ./proto/mpc_tools.proto

# Set Python path
ENV PYTHONPATH=/app/src

# Create non-root user
RUN useradd -m -u 1000 mpcuser && chown -R mpcuser:mpcuser /app
USER mpcuser

# Expose gRPC port
EXPOSE 50061

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import grpc; channel = grpc.insecure_channel('localhost:50061'); grpc.channel_ready_future(channel).result(timeout=5)"

# Run the service
CMD ["python", "-m", "src.mpc_tools"]
