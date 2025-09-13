#!/usr/bin/env python3
"""
MPC Tools Service - Simple Integration Tests
Tests basic MPC Tools service functionality
"""

import asyncio
import json
import logging
import os
import sys
import time
import unittest
from unittest.mock import Mock, patch

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import MPC Tools service
from mpc_tools.service import MPCToolsService
from mpc_tools_pb2 import *
from mpc_tools_pb2_grpc import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMPCTests(unittest.TestCase):
    """Simple tests for MPC Tools Service"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = MPCToolsService()
        self.test_computation_id = f"test_{int(time.time())}"
        
    def test_service_initialization(self):
        """Test that MPC Tools service initializes correctly"""
        logger.info("Testing MPC Tools Service Initialization...")
        
        # Verify service is initialized
        self.assertIsNotNone(self.service)
        self.assertIsInstance(self.service, MPCToolsService)
        
        logger.info("✅ MPC Tools Service Initialization test passed")
        
    def test_secure_aggregation_basic(self):
        """Test basic secure aggregation functionality"""
        logger.info("Testing Basic Secure Aggregation...")
        
        # Create test data with correct field names
        agent_data = [
            AgentData(
                agent_id="agent_1",
                encrypted_data=json.dumps({"value": 100, "weight": 0.5}),
                metadata=json.dumps({"source": "test"}),
                timestamp=int(time.time())
            ),
            AgentData(
                agent_id="agent_2", 
                encrypted_data=json.dumps({"value": 200, "weight": 0.3}),
                metadata=json.dumps({"source": "test"}),
                timestamp=int(time.time())
            )
        ]
        
        request = SecureAggregationRequest(
            computation_id=self.test_computation_id,
            agent_data=agent_data,
            aggregation_type="weighted_average",
            security_level="high"
        )
        
        # Test the service
        response = self.service.SecureAggregation(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertEqual(response.computation_id, self.test_computation_id)
        self.assertIsNotNone(response.result)
        self.assertGreater(response.execution_time_ms, 0)
        self.assertEqual(len(response.participant_ids), 2)
        
        logger.info(f"✅ Basic Secure Aggregation test passed: {response.result}")
        
    def test_risk_modeling_basic(self):
        """Test basic risk modeling functionality"""
        logger.info("Testing Basic Risk Modeling...")
        
        # Create test request with correct field names
        factors = [
            RiskFactor(
                factor_name="market_volatility",
                weight=0.4,
                value=0.25,
                source="technical_analysis"
            ),
            RiskFactor(
                factor_name="liquidity",
                weight=0.3,
                value=0.8,
                source="orderbook"
            )
        ]
        
        request = RiskModelRequest(
            model_id=f"risk_model_{int(time.time())}",
            asset_ids=["BTC", "ETH"],
            model_type="monte_carlo",
            factors=factors
        )
        
        # Test the service
        response = self.service.AdvancedRiskModeling(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.metrics)
        
        # Verify risk metrics
        metrics = response.metrics
        self.assertGreater(metrics.var_95, 0)
        self.assertGreater(metrics.var_99, 0)
        self.assertGreater(metrics.expected_shortfall, 0)
        self.assertGreater(metrics.max_drawdown, 0)
        
        logger.info(f"✅ Basic Risk Modeling test passed: VaR95={metrics.var_95}")
        
    def test_portfolio_optimization_basic(self):
        """Test basic portfolio optimization functionality"""
        logger.info("Testing Basic Portfolio Optimization...")
        
        # Create test request with correct field names
        assets = [
            Asset(
                asset_id="BTC",
                expected_return=0.15,
                volatility=0.25
            ),
            Asset(
                asset_id="ETH",
                expected_return=0.12,
                volatility=0.30
            )
        ]
        
        constraints = [
            Constraint(
                constraint_type="max_weight",
                max_value=0.5,
                min_value=0.0,
                description="BTC max weight"
            )
        ]
        
        request = PortfolioOptRequest(
            optimization_id=f"portfolio_opt_{int(time.time())}",
            assets=assets,
            objective="maximize_sharpe_ratio",
            constraints=constraints
        )
        
        # Test the service
        response = self.service.PortfolioOptimization(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.optimal_weights)
        self.assertGreater(response.expected_return, 0)
        self.assertGreater(response.risk_level, 0)
        
        # Verify weights sum to approximately 1
        total_weight = sum(weight.weight for weight in response.optimal_weights)
        self.assertAlmostEqual(total_weight, 1.0, places=2)
        
        logger.info(f"✅ Basic Portfolio Optimization test passed: expected_return={response.expected_return}")
        
    def test_federated_learning_basic(self):
        """Test basic federated learning functionality"""
        logger.info("Testing Basic Federated Learning...")
        
        # Create test request with correct field names
        updates = [
            ModelUpdate(
                agent_id="agent_1",
                encrypted_weights=json.dumps({"weights": [0.1, 0.2, 0.3]}),
                sample_count=100,
                local_accuracy=0.85,
                metadata=json.dumps({"source": "test"})
            ),
            ModelUpdate(
                agent_id="agent_2",
                encrypted_weights=json.dumps({"weights": [0.2, 0.3, 0.4]}),
                sample_count=150,
                local_accuracy=0.82,
                metadata=json.dumps({"source": "test"})
            )
        ]
        
        config = json.dumps({
            "learning_rate": 0.01,
            "batch_size": 32,
            "epochs": 10
        })
        
        budget = json.dumps({
            "max_rounds": 5,
            "timeout_seconds": 300
        })
        
        request = FederatedLearningRequest(
            model_id=f"model_{int(time.time())}",
            updates=updates,
            config=config,
            budget=budget
        )
        
        # Test the service
        response = self.service.FederatedLearning(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.aggregated_model)
        self.assertGreater(response.accuracy, 0)
        self.assertGreater(response.round_number, 0)
        
        logger.info(f"✅ Basic Federated Learning test passed: accuracy={response.accuracy}")
        
    def test_health_check(self):
        """Test service health check"""
        logger.info("Testing Service Health Check...")
        
        request = HealthRequest()
        
        # Test the service
        response = self.service.HealthCheck(request, None)
        
        # Verify response
        self.assertTrue(response.healthy)
        self.assertEqual(response.status, "healthy")
        self.assertIsNotNone(response.dependencies)
        
        logger.info(f"✅ Service Health Check test passed: {response.status}")
        
    def test_service_status(self):
        """Test service status"""
        logger.info("Testing Service Status...")
        
        request = StatusRequest()
        
        # Test the service
        response = self.service.GetServiceStatus(request, None)
        
        # Verify response
        self.assertTrue(response.healthy)
        self.assertIsNotNone(response.metrics)
        self.assertGreater(response.uptime_seconds, 0)
        
        logger.info(f"✅ Service Status test passed: uptime={response.uptime_seconds}s")

def run_simple_tests():
    """Run all simple tests"""
    logger.info("🚀 Starting MPC Tools Simple Tests...")
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SimpleMPCTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    logger.info(f"📊 Test Results:")
    logger.info(f"   Tests run: {result.testsRun}")
    logger.info(f"   Failures: {len(result.failures)}")
    logger.info(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        logger.error("❌ Test Failures:")
        for test, traceback in result.failures:
            logger.error(f"   {test}: {traceback}")
    
    if result.errors:
        logger.error("❌ Test Errors:")
        for test, traceback in result.errors:
            logger.error(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        logger.info("✅ All simple tests passed!")
        return True
    else:
        logger.error("❌ Some simple tests failed!")
        return False

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)
