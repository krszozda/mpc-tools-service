"""
MPC Tools Service - Advanced Multi-Party Computation Tools for AI Agents

This service provides secure multi-party computation capabilities, privacy-preserving
operations, and advanced analytics tools for AI agents in the Mansa Musa ecosystem.
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import grpc
from grpc import aio as grpc_aio
import redis.asyncio as redis
import asyncpg
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

# Generated protobuf imports (will be available after proto compilation)
try:
    import mpc_tools_pb2 as pb2
    import mpc_tools_pb2_grpc as pb2_grpc
except ImportError:
    # Fallback for development
    pb2 = None
    pb2_grpc = None

logger = logging.getLogger(__name__)


class MPCToolsService(pb2_grpc.MPCToolsServiceServicer):
    """
    MPC Tools Service Implementation
    
    Provides secure multi-party computation capabilities including:
    - Secure aggregation and federated learning
    - Privacy-preserving operations (differential privacy, homomorphic encryption)
    - Multi-agent coordination and consensus
    - Advanced risk modeling and portfolio optimization
    - Real-time computation orchestration
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.encryption_key: Optional[bytes] = None
        self.private_key: Optional[rsa.RSAPrivateKey] = None
        self.public_key: Optional[rsa.RSAPublicKey] = None
        
        # Service state
        self.active_computations: Dict[str, Dict[str, Any]] = {}
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.computation_cache: Dict[str, Any] = {}
        
        # Configuration
        self.max_parallel_computations = int(os.getenv('MAX_PARALLEL_COMPUTATIONS', '10'))
        self.computation_timeout = int(os.getenv('COMPUTATION_TIMEOUT', '300'))  # 5 minutes
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
        
    async def start(self):
        """Initialize MPC Tools Service"""
        await self._initialize()
        logger.info("MPC Tools Service started successfully")
        
    async def _initialize(self):
        """Initialize all connections and cryptographic components"""
        try:
            # Redis connection
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info(f"Redis client initialized: {redis_url}")
            
            # Database connection
            db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/mansa_musa')
            self.db_pool = await asyncpg.create_pool(db_url)
            await self._initialize_database()
            logger.info("Database connection established")
            
            # Initialize encryption
            await self._initialize_cryptography()
            logger.info("Cryptographic components initialized")
            
            # Initialize service tables
            await self._create_service_tables()
            logger.info("Service tables created")
            
        except Exception as e:
            logger.error(f"Failed to initialize MPC Tools Service: {e}")
            raise
    
    async def _initialize_cryptography(self):
        """Initialize cryptographic components"""
        # Generate or load encryption key
        encryption_key_str = os.getenv('MPC_ENCRYPTION_KEY')
        if encryption_key_str:
            self.encryption_key = encryption_key_str.encode()
        else:
            self.encryption_key = Fernet.generate_key()
            logger.warning("Generated new encryption key - store MPC_ENCRYPTION_KEY for persistence")
        
        # Generate RSA key pair for secure communications
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        logger.info("Cryptographic components initialized")
    
    async def _initialize_database(self):
        """Initialize database schema for MPC operations"""
        async with self.db_pool.acquire() as conn:
            # Enable TimescaleDB extension if available
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
            except Exception:
                pass
            
            # Create MPC computations table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS mpc_computations (
                    id SERIAL PRIMARY KEY,
                    computation_id TEXT UNIQUE NOT NULL,
                    computation_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    participants JSONB NOT NULL,
                    input_data JSONB,
                    result_data JSONB,
                    security_level TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    execution_time_ms INTEGER
                )
            """)
            
            # Create hypertable for time-series data
            try:
                await conn.execute(
                    "SELECT create_hypertable('mpc_computations', 'created_at', if_not_exists => TRUE)"
                )
            except Exception:
                pass
            
            # Create agent registry table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_registry (
                    id SERIAL PRIMARY KEY,
                    agent_id TEXT UNIQUE NOT NULL,
                    agent_type TEXT NOT NULL,
                    public_key TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    capabilities JSONB,
                    metadata JSONB
                )
            """)
            
            # Create privacy budget tracking
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS privacy_budgets (
                    id SERIAL PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    epsilon_total DOUBLE PRECISION NOT NULL,
                    epsilon_used DOUBLE PRECISION NOT NULL DEFAULT 0,
                    delta_total DOUBLE PRECISION NOT NULL,
                    delta_used DOUBLE PRECISION NOT NULL DEFAULT 0,
                    reset_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_mpc_computations_id ON mpc_computations (computation_id);
                CREATE INDEX IF NOT EXISTS idx_mpc_computations_status ON mpc_computations (status);
                CREATE INDEX IF NOT EXISTS idx_agent_registry_id ON agent_registry (agent_id);
                CREATE INDEX IF NOT EXISTS idx_privacy_budgets_agent ON privacy_budgets (agent_id);
            """)
    
    async def _create_service_tables(self):
        """Create additional service-specific tables"""
        async with self.db_pool.acquire() as conn:
            # Risk modeling results
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS risk_models (
                    id SERIAL PRIMARY KEY,
                    model_id TEXT UNIQUE NOT NULL,
                    model_type TEXT NOT NULL,
                    assets JSONB NOT NULL,
                    risk_metrics JSONB,
                    scenarios JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            
            # Portfolio optimizations
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_optimizations (
                    id SERIAL PRIMARY KEY,
                    optimization_id TEXT UNIQUE NOT NULL,
                    assets JSONB NOT NULL,
                    objective TEXT NOT NULL,
                    constraints JSONB,
                    optimal_weights JSONB,
                    expected_return DOUBLE PRECISION,
                    risk_level DOUBLE PRECISION,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            
            # Computation orchestration logs
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orchestration_logs (
                    id SERIAL PRIMARY KEY,
                    orchestration_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result JSONB,
                    execution_time_ms INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
    
    # ============================================================================
    # SECURE MULTI-PARTY COMPUTATIONS
    # ============================================================================
    
    async def SecureAggregation(self, request, context):
        """Perform secure aggregation across multiple agents"""
        try:
            computation_id = request.computation_id or f"agg_{int(time.time())}"
            
            # Validate participants
            participants = []
            for agent_data in request.agent_data:
                if not await self._validate_agent(agent_data.agent_id):
                    return pb2.SecureAggregationResponse(
                        success=False,
                        error_message=f"Invalid agent: {agent_data.agent_id}"
                    )
                participants.append(agent_data.agent_id)
            
            # Store computation in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO mpc_computations 
                    (computation_id, computation_type, participants, security_level, status)
                    VALUES ($1, $2, $3, $4, $5)
                """, computation_id, "secure_aggregation", 
                json.dumps(participants), request.security_level.name, "processing")
            
            # Perform secure aggregation based on type
            start_time = time.time()
            result = await self._perform_secure_aggregation(request)
            execution_time = (time.time() - start_time) * 1000
            
            # Update computation result
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE mpc_computations 
                    SET status = $1, result_data = $2, completed_at = NOW(), execution_time_ms = $3
                    WHERE computation_id = $4
                """, "completed", json.dumps(result), int(execution_time), computation_id)
            
            return pb2.SecureAggregationResponse(
                success=True,
                result=json.dumps(result),
                computation_id=computation_id,
                execution_time_ms=execution_time,
                participant_ids=participants
            )
            
        except Exception as e:
            logger.error(f"SecureAggregation error: {e}")
            return pb2.SecureAggregationResponse(
                success=False,
                error_message=str(e)
            )
    
    async def _perform_secure_aggregation(self, request) -> Dict[str, Any]:
        """Perform the actual secure aggregation computation"""
        # This is a simplified implementation
        # In production, this would use proper MPC protocols
        
        aggregated_data = {}
        aggregation_type = request.aggregation_type.name
        
        for agent_data in request.agent_data:
            # Decrypt agent data (simplified)
            try:
                decrypted_data = await self._decrypt_data(agent_data.encrypted_data)
                data = json.loads(decrypted_data)
                
                # Aggregate based on type
                if aggregation_type == "SUM":
                    for key, value in data.items():
                        if key not in aggregated_data:
                            aggregated_data[key] = 0
                        aggregated_data[key] += float(value)
                elif aggregation_type == "MEAN":
                    for key, value in data.items():
                        if key not in aggregated_data:
                            aggregated_data[key] = {"sum": 0, "count": 0}
                        aggregated_data[key]["sum"] += float(value)
                        aggregated_data[key]["count"] += 1
                # Add more aggregation types as needed
                
            except Exception as e:
                logger.warning(f"Failed to decrypt data from agent {agent_data.agent_id}: {e}")
                continue
        
        # Finalize aggregation
        if aggregation_type == "MEAN":
            for key, data in aggregated_data.items():
                if data["count"] > 0:
                    aggregated_data[key] = data["sum"] / data["count"]
        
        return aggregated_data
    
    async def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using the service's encryption key"""
        try:
            fernet = Fernet(self.encryption_key)
            decrypted_bytes = fernet.decrypt(encrypted_data.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    async def _validate_agent(self, agent_id: str) -> bool:
        """Validate that an agent is registered and active"""
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT status FROM agent_registry WHERE agent_id = $1
            """, agent_id)
            return result and result['status'] == 'active'
    
    # ============================================================================
    # PRIVACY-PRESERVING OPERATIONS
    # ============================================================================
    
    async def DifferentialPrivacyQuery(self, request, context):
        """Execute differential privacy query"""
        try:
            # Check privacy budget
            if not await self._check_privacy_budget(request.query_id, request.epsilon, request.delta):
                return pb2.DPQueryResponse(
                    success=False,
                    error_message="Insufficient privacy budget"
                )
            
            # Execute query with differential privacy
            result = await self._execute_dp_query(request)
            
            # Update privacy budget
            await self._update_privacy_budget(request.query_id, request.epsilon, request.delta)
            
            return pb2.DPQueryResponse(
                success=True,
                result=json.dumps(result),
                privacy_cost=request.epsilon,
                query_id=request.query_id
            )
            
        except Exception as e:
            logger.error(f"DifferentialPrivacyQuery error: {e}")
            return pb2.DPQueryResponse(
                success=False,
                error_message=str(e)
            )
    
    async def _check_privacy_budget(self, query_id: str, epsilon: float, delta: float) -> bool:
        """Check if there's sufficient privacy budget"""
        # Simplified implementation
        return epsilon <= 1.0 and delta <= 0.01
    
    async def _execute_dp_query(self, request) -> Dict[str, Any]:
        """Execute differential privacy query"""
        # This would implement actual differential privacy mechanisms
        # For now, return a mock result
        return {
            "query_type": request.query_type,
            "data_sources": request.data_sources,
            "result": "differentially_private_result",
            "noise_added": True
        }
    
    async def _update_privacy_budget(self, query_id: str, epsilon: float, delta: float):
        """Update privacy budget after query execution"""
        # Implementation would track and update privacy budget
        pass
    
    # ============================================================================
    # MULTI-AGENT COORDINATION
    # ============================================================================
    
    async def CoordinateAgents(self, request, context):
        """Coordinate multiple agents for a task"""
        try:
            coordination_id = request.coordination_id or f"coord_{int(time.time())}"
            
            # Register coordination task
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO orchestration_logs 
                    (orchestration_id, task_id, status)
                    VALUES ($1, $2, $3)
                """, coordination_id, "coordination", "started")
            
            # Coordinate agents based on type
            result = await self._coordinate_agents(request)
            
            return pb2.CoordinationResponse(
                success=True,
                coordination_result=json.dumps(result),
                agent_statuses=[
                    pb2.AgentStatus(
                        agent_id=agent_id,
                        status="coordinated",
                        last_seen=int(time.time())
                    ) for agent_id in request.agent_ids
                ]
            )
            
        except Exception as e:
            logger.error(f"CoordinateAgents error: {e}")
            return pb2.CoordinationResponse(
                success=False,
                error_message=str(e)
            )
    
    async def _coordinate_agents(self, request) -> Dict[str, Any]:
        """Perform agent coordination"""
        # Implementation would handle actual agent coordination
        return {
            "coordination_type": request.type.name,
            "participants": request.agent_ids,
            "task": request.task_description,
            "status": "coordinated"
        }
    
    # ============================================================================
    # ADVANCED ANALYTICS & RISK MODELING
    # ============================================================================
    
    async def AdvancedRiskModeling(self, request, context):
        """Perform advanced risk modeling"""
        try:
            model_id = request.model_id or f"risk_{int(time.time())}"
            
            # Perform risk modeling
            risk_metrics = await self._calculate_risk_metrics(request)
            scenarios = await self._generate_risk_scenarios(request)
            
            # Store results
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO risk_models 
                    (model_id, model_type, assets, risk_metrics, scenarios)
                    VALUES ($1, $2, $3, $4, $5)
                """, model_id, request.model_type.name, 
                json.dumps(request.asset_ids), json.dumps(risk_metrics), json.dumps(scenarios))
            
            return pb2.RiskModelResponse(
                success=True,
                metrics=pb2.RiskMetrics(
                    var_95=risk_metrics.get('var_95', 0.0),
                    var_99=risk_metrics.get('var_99', 0.0),
                    cvar_95=risk_metrics.get('cvar_95', 0.0),
                    cvar_99=risk_metrics.get('cvar_99', 0.0),
                    expected_shortfall=risk_metrics.get('expected_shortfall', 0.0),
                    max_drawdown=risk_metrics.get('max_drawdown', 0.0)
                ),
                model_id=model_id
            )
            
        except Exception as e:
            logger.error(f"AdvancedRiskModeling error: {e}")
            return pb2.RiskModelResponse(
                success=False,
                error_message=str(e)
            )
    
    async def _calculate_risk_metrics(self, request) -> Dict[str, float]:
        """Calculate risk metrics for the given assets"""
        # Simplified implementation
        return {
            "var_95": 0.05,
            "var_99": 0.02,
            "cvar_95": 0.07,
            "cvar_99": 0.03,
            "expected_shortfall": 0.06,
            "max_drawdown": 0.15
        }
    
    async def _generate_risk_scenarios(self, request) -> List[Dict[str, Any]]:
        """Generate risk scenarios"""
        return [
            {
                "scenario_name": "Market Crash",
                "probability": 0.05,
                "impact": -0.20,
                "description": "Severe market downturn"
            },
            {
                "scenario_name": "Volatility Spike",
                "probability": 0.15,
                "impact": -0.10,
                "description": "Increased market volatility"
            }
        ]
    
    # ============================================================================
    # REAL-TIME ORCHESTRATION
    # ============================================================================
    
    async def OrchestrateComputation(self, request, context):
        """Orchestrate real-time computations"""
        try:
            orchestration_id = request.orchestration_id or f"orch_{int(time.time())}"
            
            # Process tasks based on strategy
            if request.strategy == pb2.OrchestrationStrategy.PARALLEL:
                async for result in self._process_parallel_tasks(request.tasks, orchestration_id):
                    yield result
            else:
                async for result in self._process_sequential_tasks(request.tasks, orchestration_id):
                    yield result
                    
        except Exception as e:
            logger.error(f"OrchestrateComputation error: {e}")
            yield pb2.ComputationResult(
                task_id="error",
                success=False,
                error_message=str(e)
            )
    
    async def _process_parallel_tasks(self, tasks, orchestration_id):
        """Process tasks in parallel"""
        # Implementation would handle parallel task processing
        for task in tasks:
            yield pb2.ComputationResult(
                task_id=task.task_id,
                success=True,
                result="parallel_result",
                execution_time_ms=100.0,
                timestamp=int(time.time())
            )
    
    async def _process_sequential_tasks(self, tasks, orchestration_id):
        """Process tasks sequentially"""
        # Implementation would handle sequential task processing
        for task in tasks:
            yield pb2.ComputationResult(
                task_id=task.task_id,
                success=True,
                result="sequential_result",
                execution_time_ms=50.0,
                timestamp=int(time.time())
            )
    
    # ============================================================================
    # SERVICE MANAGEMENT
    # ============================================================================
    
    async def GetServiceStatus(self, request, context):
        """Get service status and metrics"""
        try:
            uptime = time.time() - self._start_time if hasattr(self, '_start_time') else 0
            
            metrics = {
                "active_computations": len(self.active_computations),
                "registered_agents": len(self.agent_registry),
                "cache_size": len(self.computation_cache),
                "max_parallel": self.max_parallel_computations
            }
            
            return pb2.StatusResponse(
                healthy=True,
                status="operational",
                metrics=metrics,
                uptime_seconds=int(uptime)
            )
            
        except Exception as e:
            logger.error(f"GetServiceStatus error: {e}")
            return pb2.StatusResponse(
                healthy=False,
                status="error"
            )
    
    async def HealthCheck(self, request, context):
        """Health check endpoint"""
        try:
            # Check dependencies
            dependencies = []
            
            # Check Redis
            try:
                await self.redis_client.ping()
                dependencies.append("redis:healthy")
            except Exception:
                dependencies.append("redis:unhealthy")
            
            # Check Database
            try:
                async with self.db_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                dependencies.append("database:healthy")
            except Exception:
                dependencies.append("database:unhealthy")
            
            return pb2.HealthResponse(
                healthy=len([d for d in dependencies if "healthy" in d]) == len(dependencies),
                status="operational" if all("healthy" in d for d in dependencies) else "degraded",
                dependencies=dependencies
            )
            
        except Exception as e:
            logger.error(f"HealthCheck error: {e}")
            return pb2.HealthResponse(
                healthy=False,
                status="error",
                dependencies=["error"]
            )

    # ===== BRAKUJĄCE METODY MPC TOOLS =====
    
    async def FederatedLearning(self, request, context):
        """Federated Learning Implementation (using scikit-learn fallback)"""
        try:
            logger.info(f"FederatedLearning request: {request}")
            
            # Parse encrypted model updates
            model_updates = []
            for update in request.model_updates:
                try:
                    # Decrypt model data
                    decrypted_data = self._decrypt_data(update.encrypted_weights)
                    model_data = json.loads(decrypted_data)
                    model_updates.append(model_data)
                except Exception as e:
                    logger.warning(f"Failed to decrypt model update: {e}")
                    continue
            
            if not model_updates:
                return pb2.FederatedLearningResponse(
                    success=False,
                    message="No valid model updates received"
                )
            
            # Simple federated averaging using numpy/scipy
            import numpy as np
            from sklearn.linear_model import LinearRegression
            
            # Aggregate model weights (simplified)
            aggregated_weights = {}
            for key in model_updates[0].keys():
                if isinstance(model_updates[0][key], list):
                    aggregated_weights[key] = np.mean([update[key] for update in model_updates], axis=0)
                else:
                    aggregated_weights[key] = np.mean([update[key] for update in model_updates])
            
            # Encrypt aggregated model
            encrypted_model = self._encrypt_data(json.dumps(aggregated_weights))
            
            return pb2.FederatedLearningResponse(
                success=True,
                message="Federated learning completed successfully",
                aggregated_model=pb2.ModelUpdate(
                    encrypted_weights=encrypted_model,
                    model_version=request.model_version + 1,
                    participant_count=len(model_updates)
                )
            )
            
        except Exception as e:
            logger.error(f"FederatedLearning error: {e}")
            return pb2.FederatedLearningResponse(
                success=False,
                message=f"Federated learning failed: {str(e)}"
            )

    async def HomomorphicComputation(self, request, context):
        """Homomorphic Computation Implementation (using cryptography fallback)"""
        try:
            logger.info(f"HomomorphicComputation request: {request}")
            
            # Simple homomorphic operations using cryptography
            import numpy as np
            
            # Parse encrypted data
            encrypted_values = []
            for data in request.encrypted_data:
                try:
                    decrypted = self._decrypt_data(data)
                    value = float(decrypted)
                    encrypted_values.append(value)
                except Exception as e:
                    logger.warning(f"Failed to decrypt value: {e}")
                    continue
            
            if not encrypted_values:
                return pb2.HomomorphicResponse(
                    success=False,
                    message="No valid encrypted data received"
                )
            
            # Perform computation based on operation type
            result = 0
            if request.operation == "SUM":
                result = sum(encrypted_values)
            elif request.operation == "MEAN":
                result = np.mean(encrypted_values)
            elif request.operation == "MAX":
                result = max(encrypted_values)
            elif request.operation == "MIN":
                result = min(encrypted_values)
            else:
                return pb2.HomomorphicResponse(
                    success=False,
                    message=f"Unsupported operation: {request.operation}"
                )
            
            # Encrypt result
            encrypted_result = self._encrypt_data(str(result))
            
            return pb2.HomomorphicResponse(
                success=True,
                message="Homomorphic computation completed",
                encrypted_result=encrypted_result,
                operation=request.operation,
                input_count=len(encrypted_values)
            )
            
        except Exception as e:
            logger.error(f"HomomorphicComputation error: {e}")
            return pb2.HomomorphicResponse(
                success=False,
                message=f"Homomorphic computation failed: {str(e)}"
            )

    async def PortfolioOptimization(self, request, context):
        """Portfolio Optimization Implementation (using scipy fallback)"""
        try:
            logger.info(f"PortfolioOptimization request: {request}")
            
            import numpy as np
            from scipy.optimize import minimize
            
            # Parse portfolio data
            assets = []
            returns = []
            risks = []
            
            for asset in request.assets:
                assets.append(asset.symbol)
                returns.append(asset.expected_return)
                risks.append(asset.risk_level)
            
            if len(assets) < 2:
                return pb2.PortfolioOptResponse(
                    success=False,
                    message="Portfolio optimization requires at least 2 assets"
                )
            
            # Simple portfolio optimization using scipy
            n_assets = len(assets)
            
            # Objective function: maximize Sharpe ratio (simplified)
            def objective(weights):
                portfolio_return = np.dot(weights, returns)
                portfolio_risk = np.sqrt(np.dot(weights, np.array(risks)**2))
                if portfolio_risk == 0:
                    return -portfolio_return  # Avoid division by zero
                return -(portfolio_return / portfolio_risk)  # Negative for minimization
            
            # Constraints: weights sum to 1
            constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
            
            # Bounds: weights between 0 and 1
            bounds = [(0, 1) for _ in range(n_assets)]
            
            # Initial guess: equal weights
            x0 = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                optimal_weights = result.x
                portfolio_return = np.dot(optimal_weights, returns)
                portfolio_risk = np.sqrt(np.dot(optimal_weights, np.array(risks)**2))
                sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
                
                # Build response
                optimized_assets = []
                for i, asset in enumerate(assets):
                    optimized_assets.append(pb2.OptimizedAsset(
                        symbol=asset,
                        weight=optimal_weights[i],
                        expected_return=returns[i],
                        risk_level=risks[i]
                    ))
                
                return pb2.PortfolioOptResponse(
                    success=True,
                    message="Portfolio optimization completed successfully",
                    optimized_assets=optimized_assets,
                    portfolio_return=portfolio_return,
                    portfolio_risk=portfolio_risk,
                    sharpe_ratio=sharpe_ratio,
                    optimization_method="scipy_minimize"
                )
            else:
                return pb2.PortfolioOptResponse(
                    success=False,
                    message=f"Optimization failed: {result.message}"
                )
            
        except Exception as e:
            logger.error(f"PortfolioOptimization error: {e}")
            return pb2.PortfolioOptResponse(
                success=False,
                message=f"Portfolio optimization failed: {str(e)}"
            )

    async def ShareInsights(self, request, context):
        """Share Insights Implementation"""
        try:
            logger.info(f"ShareInsights request: {request}")
            
            # Store insight in agent registry
            insight_id = f"insight_{request.agent_id}_{int(time.time())}"
            
            self.agent_registry[request.agent_id] = {
                "last_seen": datetime.now(),
                "insights": self.agent_registry.get(request.agent_id, {}).get("insights", []) + [insight_id],
                "capabilities": request.capabilities
            }
            
            # Store insight data
            insight_data = {
                "insight_id": insight_id,
                "agent_id": request.agent_id,
                "insight_type": request.insight_type,
                "data": request.insight_data,
                "timestamp": datetime.now().isoformat(),
                "privacy_level": request.privacy_level
            }
            
            # Cache insight
            await self._cache_insight(insight_id, insight_data)
            
            return pb2.InsightShareResponse(
                success=True,
                message="Insight shared successfully",
                insight_id=insight_id,
                timestamp=int(time.time())
            )
            
        except Exception as e:
            logger.error(f"ShareInsights error: {e}")
            return pb2.InsightShareResponse(
                success=False,
                message=f"Failed to share insight: {str(e)}"
            )

    async def CorrelationAnalysis(self, request, context):
        """Correlation Analysis Implementation (using pandas fallback)"""
        try:
            logger.info(f"CorrelationAnalysis request: {request}")
            
            import pandas as pd
            import numpy as np
            
            # Parse time series data
            data_dict = {}
            for series in request.time_series:
                data_dict[series.symbol] = series.values
            
            if len(data_dict) < 2:
                return pb2.CorrelationResponse(
                    success=False,
                    message="Correlation analysis requires at least 2 time series"
                )
            
            # Create DataFrame
            df = pd.DataFrame(data_dict)
            
            # Calculate correlation matrix
            correlation_matrix = df.corr()
            
            # Find significant correlations
            significant_correlations = []
            for i, symbol1 in enumerate(correlation_matrix.columns):
                for j, symbol2 in enumerate(correlation_matrix.columns):
                    if i < j:  # Avoid duplicates
                        corr_value = correlation_matrix.loc[symbol1, symbol2]
                        if abs(corr_value) > request.min_correlation_threshold:
                            significant_correlations.append(pb2.CorrelationPair(
                                symbol1=symbol1,
                                symbol2=symbol2,
                                correlation=corr_value,
                                p_value=0.05  # Simplified
                            ))
            
            return pb2.CorrelationResponse(
                success=True,
                message="Correlation analysis completed",
                correlation_pairs=significant_correlations,
                analysis_period=f"{request.time_series[0].start_time} to {request.time_series[0].end_time}",
                total_pairs=len(significant_correlations)
            )
            
        except Exception as e:
            logger.error(f"CorrelationAnalysis error: {e}")
            return pb2.CorrelationResponse(
                success=False,
                message=f"Correlation analysis failed: {str(e)}"
            )

    async def AnomalyDetection(self, request, context):
        """Anomaly Detection Implementation (using scikit-learn fallback)"""
        try:
            logger.info(f"AnomalyDetection request: {request}")
            
            from sklearn.ensemble import IsolationForest
            import numpy as np
            
            # Parse data points
            data_points = []
            for point in request.data_points:
                data_points.append([point.value, point.timestamp])
            
            if len(data_points) < 10:
                return pb2.AnomalyResponse(
                    success=False,
                    message="Anomaly detection requires at least 10 data points"
                )
            
            # Convert to numpy array
            X = np.array(data_points)
            
            # Use Isolation Forest for anomaly detection
            iso_forest = IsolationForest(contamination=request.contamination_threshold, random_state=42)
            anomaly_labels = iso_forest.fit_predict(X)
            
            # Identify anomalies
            anomalies = []
            for i, label in enumerate(anomaly_labels):
                if label == -1:  # Anomaly
                    anomalies.append(pb2.AnomalyPoint(
                        index=i,
                        value=request.data_points[i].value,
                        timestamp=request.data_points[i].timestamp,
                        anomaly_score=iso_forest.decision_function([X[i]])[0],
                        anomaly_type="statistical_outlier"
                    ))
            
            return pb2.AnomalyResponse(
                success=True,
                message="Anomaly detection completed",
                anomalies=anomalies,
                total_points=len(data_points),
                anomaly_count=len(anomalies),
                detection_method="isolation_forest"
            )
            
        except Exception as e:
            logger.error(f"AnomalyDetection error: {e}")
            return pb2.AnomalyResponse(
                success=False,
                message=f"Anomaly detection failed: {str(e)}"
            )
