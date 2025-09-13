# MPC Tools Service

Advanced Multi-Party Computation Tools for AI Agents in the Mansa Musa Ecosystem.

## 🎯 Overview

The MPC Tools Service provides secure multi-party computation capabilities, privacy-preserving operations, and advanced analytics tools for AI agents. It enables:

- **Secure Multi-Party Computations** - Aggregation, federated learning, secure sums
- **Privacy-Preserving Operations** - Differential privacy, homomorphic encryption, zero-knowledge proofs
- **Multi-Agent Coordination** - Consensus protocols, agent synchronization, insight sharing
- **Advanced Analytics** - Risk modeling, portfolio optimization, correlation analysis
- **Real-time Orchestration** - Stream processing, parallel computations, adaptive strategies

## 🏗️ Architecture

```
┌─────────────────┐    gRPC     ┌──────────────────┐
│   AI Assistant  │◄──────────►│   MPC Tools      │
│   (Port 50051)  │             │   (Port 50061)  │
└─────────────────┘             └──────────────────┘
                                        │
                                        │ gRPC
                                        ▼
                               ┌──────────────────┐
                               │   Other Services │
                               │ (Price, News,    │
                               │  Sentiment, etc) │
                               └──────────────────┘
                                        │
                                        │ Database
                                        ▼
                               ┌──────────────────┐
                               │ TimescaleDB +    │
                               │ Redis Cache      │
                               └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- PostgreSQL with TimescaleDB extension
- Redis

### Local Development

1. **Clone and setup:**
   ```bash
   cd mpc-tools-service
   make dev-setup
   ```

2. **Generate protobuf files:**
   ```bash
   make proto
   ```

3. **Configure environment:**
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost:5432/mansa_musa"
   export REDIS_URL="redis://localhost:6379"
   export MPC_ENCRYPTION_KEY="your-encryption-key"
   ```

4. **Run the service:**
   ```bash
   make run
   ```

### Docker Deployment

1. **Build Docker image:**
   ```bash
   make docker-build
   ```

2. **Run container:**
   ```bash
   make docker-run
   ```

## 📡 gRPC API

### Core Services

- **SecureAggregation** - Multi-party secure aggregation
- **FederatedLearning** - Distributed machine learning
- **DifferentialPrivacyQuery** - Privacy-preserving queries
- **CoordinateAgents** - Multi-agent coordination
- **AdvancedRiskModeling** - Risk analysis and modeling
- **OrchestrateComputation** - Real-time computation orchestration

### Example Usage

```python
import grpc
from mpc_tools_pb2_grpc import MPCToolsServiceStub
from mpc_tools_pb2 import SecureAggregationRequest, AggregationType, SecurityLevel

# Connect to service
channel = grpc.insecure_channel('localhost:50061')
client = MPCToolsServiceStub(channel)

# Perform secure aggregation
request = SecureAggregationRequest(
    computation_id="test_agg_001",
    aggregation_type=AggregationType.SUM,
    security_level=SecurityLevel.HIGH,
    agent_data=[
        AgentData(
            agent_id="agent_1",
            encrypted_data="encrypted_data_1",
            public_key="public_key_1"
        )
    ]
)

response = client.SecureAggregation(request)
print(f"Result: {response.result}")
```

## 🔐 Security Features

### Cryptographic Components

- **Fernet Encryption** - Symmetric encryption for data at rest
- **RSA Key Pairs** - Asymmetric encryption for secure communications
- **Differential Privacy** - Privacy budget tracking and enforcement
- **Homomorphic Encryption** - Computations on encrypted data
- **Zero-Knowledge Proofs** - Verification without revealing data

### Privacy Budget Management

The service tracks privacy budgets per agent to ensure differential privacy compliance:

```sql
CREATE TABLE privacy_budgets (
    agent_id TEXT NOT NULL,
    epsilon_total DOUBLE PRECISION NOT NULL,
    epsilon_used DOUBLE PRECISION NOT NULL DEFAULT 0,
    delta_total DOUBLE PRECISION NOT NULL,
    delta_used DOUBLE PRECISION NOT NULL DEFAULT 0,
    reset_date DATE NOT NULL DEFAULT CURRENT_DATE
);
```

## 📊 Database Schema

### Core Tables

- **mpc_computations** - Track all MPC operations
- **agent_registry** - Manage registered agents
- **privacy_budgets** - Track privacy budget usage
- **risk_models** - Store risk modeling results
- **portfolio_optimizations** - Portfolio optimization results
- **orchestration_logs** - Computation orchestration logs

### TimescaleDB Integration

All time-series data is stored in TimescaleDB hypertables for optimal performance:

```sql
SELECT create_hypertable('mpc_computations', 'created_at', if_not_exists => TRUE);
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_secure_aggregation.py -v

# Run with coverage
pytest --cov=src tests/
```

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `MPC_ENCRYPTION_KEY` - Encryption key for data security
- `PORT` - gRPC server port (default: 50061)
- `MAX_PARALLEL_COMPUTATIONS` - Max parallel computations (default: 10)
- `COMPUTATION_TIMEOUT` - Computation timeout in seconds (default: 300)
- `CACHE_TTL` - Cache TTL in seconds (default: 3600)

### Service Configuration

```python
# In service.py
self.max_parallel_computations = int(os.getenv('MAX_PARALLEL_COMPUTATIONS', '10'))
self.computation_timeout = int(os.getenv('COMPUTATION_TIMEOUT', '300'))
self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))
```

## 🚀 Production Deployment

### Docker Compose Integration

Add to your `docker-compose.vps.yml`:

```yaml
mpc-tools-service:
  image: ghcr.io/simple-crypto-master/mpc-tools-service:latest
  container_name: mpc-tools-service
  networks:
    - mansa-musa-network
  environment:
    <<: *common-env
    MPC_ENCRYPTION_KEY: ${MPC_ENCRYPTION_KEY}
  depends_on:
    - redis
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "python", "-c", "import grpc; channel = grpc.insecure_channel('localhost:50061'); grpc.channel_ready_future(channel).result(timeout=5)"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mpc-tools-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mpc-tools-service
  template:
    metadata:
      labels:
        app: mpc-tools-service
    spec:
      containers:
      - name: mpc-tools-service
        image: ghcr.io/simple-crypto-master/mpc-tools-service:latest
        ports:
        - containerPort: 50061
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mansa-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis:6379"
```

## 📈 Monitoring

### Health Checks

- **gRPC Health Check** - Standard gRPC health checking
- **Dependency Checks** - Redis and database connectivity
- **Service Metrics** - Active computations, registered agents, cache size

### Logging

Structured logging with correlation IDs for tracing:

```python
logger.info("SecureAggregation started", extra={
    "computation_id": computation_id,
    "participants": len(participants),
    "security_level": security_level
})
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests
- Update documentation
- Use conventional commit messages

## 📄 License

This project is part of the Mansa Musa ecosystem and follows the same licensing terms.

## 🆘 Support

For issues and questions:

1. Check the logs: `docker logs mpc-tools-service`
2. Verify configuration: `curl http://localhost:50061/health`
3. Check database connectivity
4. Review privacy budget usage

---

**🎯 Ready for production deployment with advanced MPC capabilities!**
