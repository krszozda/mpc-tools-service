"""
Tests for MPC Tools Service
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Mock protobuf imports for testing
class MockPB2:
    class SecureAggregationRequest:
        def __init__(self):
            self.computation_id = "test_001"
            self.agent_data = []
            self.aggregation_type = MockPB2.AggregationType()
            self.security_level = MockPB2.SecurityLevel()
        
        class AggregationType:
            name = "SUM"
        
        class SecurityLevel:
            name = "HIGH"
    
    class AgentData:
        def __init__(self):
            self.agent_id = "agent_1"
            self.encrypted_data = "encrypted_data"
            self.public_key = "public_key"
    
    class SecureAggregationResponse:
        def __init__(self, success=True, result="", error_message=""):
            self.success = success
            self.result = result
            self.error_message = error_message
            self.computation_id = "test_001"
            self.execution_time_ms = 100.0
            self.participant_ids = ["agent_1"]

# Mock the protobuf imports
import sys
sys.modules['mpc_tools_pb2'] = MockPB2()
sys.modules['mpc_tools_pb2_grpc'] = MagicMock()

from src.mpc_tools.service import MPCToolsService


@pytest.fixture
async def mpc_service():
    """Create MPC service instance for testing"""
    service = MPCToolsService()
    
    # Mock dependencies
    service.redis_client = AsyncMock()
    service.db_pool = AsyncMock()
    service.encryption_key = b'test-key-123456789012345678901234567890'
    
    # Mock database operations
    async def mock_execute(query, *args):
        return None
    
    async def mock_fetchrow(query, *args):
        return {'status': 'active'}
    
    service.db_pool.acquire.return_value.__aenter__.return_value.execute = mock_execute
    service.db_pool.acquire.return_value.__aenter__.return_value.fetchrow = mock_fetchrow
    
    return service


@pytest.mark.asyncio
async def test_secure_aggregation_success(mpc_service):
    """Test successful secure aggregation"""
    # Mock request
    request = MockPB2.SecureAggregationRequest()
    request.agent_data = [MockPB2.AgentData()]
    
    # Mock context
    context = MagicMock()
    
    # Mock decryption
    with patch.object(mpc_service, '_decrypt_data', return_value='{"value": 10}'):
        response = await mpc_service.SecureAggregation(request, context)
    
    assert response.success is True
    assert response.computation_id == "test_001"
    assert response.execution_time_ms > 0


@pytest.mark.asyncio
async def test_secure_aggregation_invalid_agent(mpc_service):
    """Test secure aggregation with invalid agent"""
    request = MockPB2.SecureAggregationRequest()
    request.agent_data = [MockPB2.AgentData()]
    
    # Mock invalid agent
    async def mock_fetchrow_invalid(query, *args):
        return None
    
    mpc_service.db_pool.acquire.return_value.__aenter__.return_value.fetchrow = mock_fetchrow_invalid
    
    context = MagicMock()
    response = await mpc_service.SecureAggregation(request, context)
    
    assert response.success is False
    assert "Invalid agent" in response.error_message


@pytest.mark.asyncio
async def test_differential_privacy_query(mpc_service):
    """Test differential privacy query"""
    # Mock request
    request = MagicMock()
    request.query_id = "test_query"
    request.query_type = "count"
    request.data_sources = ["source1", "source2"]
    request.epsilon = 0.5
    request.delta = 0.01
    
    context = MagicMock()
    
    response = await mpc_service.DifferentialPrivacyQuery(request, context)
    
    assert response.success is True
    assert response.query_id == "test_query"
    assert response.privacy_cost == 0.5


@pytest.mark.asyncio
async def test_coordinate_agents(mpc_service):
    """Test agent coordination"""
    request = MagicMock()
    request.coordination_id = "coord_001"
    request.agent_ids = ["agent1", "agent2"]
    request.type = MagicMock()
    request.type.name = "TASK_DISTRIBUTION"
    request.task_description = "Test task"
    
    context = MagicMock()
    
    response = await mpc_service.CoordinateAgents(request, context)
    
    assert response.success is True
    assert len(response.agent_statuses) == 2
    assert response.agent_statuses[0].agent_id == "agent1"


@pytest.mark.asyncio
async def test_advanced_risk_modeling(mpc_service):
    """Test advanced risk modeling"""
    request = MagicMock()
    request.model_id = "risk_model_001"
    request.asset_ids = ["BTC", "ETH"]
    request.model_type = MagicMock()
    request.model_type.name = "VAR"
    
    context = MagicMock()
    
    response = await mpc_service.AdvancedRiskModeling(request, context)
    
    assert response.success is True
    assert response.model_id == "risk_model_001"
    assert response.metrics.var_95 == 0.05


@pytest.mark.asyncio
async def test_health_check(mpc_service):
    """Test health check endpoint"""
    request = MagicMock()
    context = MagicMock()
    
    # Mock Redis ping
    mpc_service.redis_client.ping.return_value = True
    
    # Mock database check
    async def mock_fetchval(query):
        return 1
    
    mpc_service.db_pool.acquire.return_value.__aenter__.return_value.fetchval = mock_fetchval
    
    response = await mpc_service.HealthCheck(request, context)
    
    assert response.healthy is True
    assert "redis:healthy" in response.dependencies
    assert "database:healthy" in response.dependencies


@pytest.mark.asyncio
async def test_service_status(mpc_service):
    """Test service status endpoint"""
    request = MagicMock()
    context = MagicMock()
    
    # Set start time for uptime calculation
    mpc_service._start_time = datetime.now().timestamp() - 100
    
    response = await mpc_service.GetServiceStatus(request, context)
    
    assert response.healthy is True
    assert response.status == "operational"
    assert response.uptime_seconds >= 0
    assert "active_computations" in response.metrics


@pytest.mark.asyncio
async def test_decrypt_data(mpc_service):
    """Test data decryption"""
    test_data = "test data"
    
    # Encrypt data first
    from cryptography.fernet import Fernet
    fernet = Fernet(mpc_service.encryption_key)
    encrypted_data = fernet.encrypt(test_data.encode()).decode()
    
    # Decrypt data
    decrypted_data = await mpc_service._decrypt_data(encrypted_data)
    
    assert decrypted_data == test_data


@pytest.mark.asyncio
async def test_validate_agent(mpc_service):
    """Test agent validation"""
    # Test valid agent
    result = await mpc_service._validate_agent("valid_agent")
    assert result is True
    
    # Test invalid agent
    async def mock_fetchrow_none(query, *args):
        return None
    
    mpc_service.db_pool.acquire.return_value.__aenter__.return_value.fetchrow = mock_fetchrow_none
    
    result = await mpc_service._validate_agent("invalid_agent")
    assert result is False


@pytest.mark.asyncio
async def test_perform_secure_aggregation_sum(mpc_service):
    """Test secure aggregation with SUM type"""
    request = MagicMock()
    request.aggregation_type = MagicMock()
    request.aggregation_type.name = "SUM"
    request.agent_data = [
        MagicMock(encrypted_data="encrypted1"),
        MagicMock(encrypted_data="encrypted2")
    ]
    
    # Mock decryption
    with patch.object(mpc_service, '_decrypt_data', side_effect=['{"value": 10}', '{"value": 20}']):
        result = await mpc_service._perform_secure_aggregation(request)
    
    assert result["value"] == 30


@pytest.mark.asyncio
async def test_perform_secure_aggregation_mean(mpc_service):
    """Test secure aggregation with MEAN type"""
    request = MagicMock()
    request.aggregation_type = MagicMock()
    request.aggregation_type.name = "MEAN"
    request.agent_data = [
        MagicMock(encrypted_data="encrypted1"),
        MagicMock(encrypted_data="encrypted2")
    ]
    
    # Mock decryption
    with patch.object(mpc_service, '_decrypt_data', side_effect=['{"value": 10}', '{"value": 20}']):
        result = await mpc_service._perform_secure_aggregation(request)
    
    assert result["value"] == 15.0


@pytest.mark.asyncio
async def test_calculate_risk_metrics(mpc_service):
    """Test risk metrics calculation"""
    request = MagicMock()
    request.asset_ids = ["BTC", "ETH"]
    
    result = await mpc_service._calculate_risk_metrics(request)
    
    assert "var_95" in result
    assert "var_99" in result
    assert "cvar_95" in result
    assert "cvar_99" in result
    assert "expected_shortfall" in result
    assert "max_drawdown" in result


@pytest.mark.asyncio
async def test_generate_risk_scenarios(mpc_service):
    """Test risk scenario generation"""
    request = MagicMock()
    
    result = await mpc_service._generate_risk_scenarios(request)
    
    assert len(result) == 2
    assert result[0]["scenario_name"] == "Market Crash"
    assert result[1]["scenario_name"] == "Volatility Spike"


if __name__ == "__main__":
    pytest.main([__file__])
