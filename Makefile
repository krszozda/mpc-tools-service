# MPC Tools Service Makefile

.PHONY: help build run test clean proto docker-build docker-run

# Default target
help:
	@echo "MPC Tools Service - Available commands:"
	@echo "  build        - Build the service"
	@echo "  run          - Run the service locally"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean build artifacts"
	@echo "  proto        - Generate protobuf files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"

# Build the service
build: proto
	@echo "Building MPC Tools Service..."
	pip install -r requirements.txt

# Generate protobuf files
proto:
	@echo "Generating protobuf files..."
	python -m grpc_tools.protoc \
		--proto_path=./proto \
		--python_out=./src \
		--grpc_python_out=./src \
		./proto/mpc_tools.proto
	@echo "Protobuf files generated"

# Run the service locally
run: build
	@echo "Starting MPC Tools Service..."
	PYTHONPATH=./src python -m src.mpc_tools

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pb2.py" -delete
	find . -type f -name "*_pb2_grpc.py" -delete

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t mpc-tools-service:latest .

docker-run:
	@echo "Running Docker container..."
	docker run -p 50061:50061 \
		-e DATABASE_URL="postgresql://postgres:password@host.docker.internal:5432/mansa_musa" \
		-e REDIS_URL="redis://host.docker.internal:6379" \
		mpc-tools-service:latest

# Development setup
dev-setup: build
	@echo "Setting up development environment..."
	pip install -r requirements.txt
	pre-commit install

# Production deployment
deploy:
	@echo "Deploying to production..."
	docker build -t ghcr.io/simple-crypto-master/mpc-tools-service:latest .
	docker push ghcr.io/simple-crypto-master/mpc-tools-service:latest
