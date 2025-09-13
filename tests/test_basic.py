#!/usr/bin/env python3
"""
MPC Tools Service - Basic Functionality Test
Tests basic MPC Tools service functionality
"""

import json
import logging
import os
import sys
import time
import unittest

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import MPC Tools service
from mpc_tools.service import MPCToolsService
from mpc_tools_pb2 import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BasicMPCTests(unittest.TestCase):
    """Basic tests for MPC Tools Service"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = MPCToolsService()
        
    def test_service_initialization(self):
        """Test that MPC Tools service initializes correctly"""
        logger.info("Testing MPC Tools Service Initialization...")
        
        # Verify service is initialized
        self.assertIsNotNone(self.service)
        self.assertIsInstance(self.service, MPCToolsService)
        
        logger.info("✅ MPC Tools Service Initialization test passed")
        
    def test_secure_aggregation_simple(self):
        """Test simple secure aggregation functionality"""
        logger.info("Testing Simple Secure Aggregation...")
        
        # Create minimal test data
        agent_data = [
            AgentData(
                agent_id="agent_1",
                encrypted_data="test_data_1",
                timestamp=int(time.time())
            ),
            AgentData(
                agent_id="agent_2", 
                encrypted_data="test_data_2",
                timestamp=int(time.time())
            )
        ]
        
        request = SecureAggregationRequest(
            computation_id=f"test_{int(time.time())}",
            agent_data=agent_data,
            aggregation_type=AggregationType.SUM,
            security_level=SecurityLevel.MEDIUM
        )
        
        # Test the service
        response = self.service.SecureAggregation(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.result)
        self.assertGreater(response.execution_time_ms, 0)
        self.assertEqual(len(response.participant_ids), 2)
        
        logger.info(f"✅ Simple Secure Aggregation test passed")
        
    def test_risk_modeling_simple(self):
        """Test simple risk modeling functionality"""
        logger.info("Testing Simple Risk Modeling...")
        
        # Create minimal test request
        factors = [
            RiskFactor(
                factor_name="volatility",
                weight=0.5,
                value=0.25,
                source="test"
            )
        ]
        
        request = RiskModelRequest(
            model_id=f"test_model_{int(time.time())}",
            asset_ids=["BTC"],
            model_type=RiskModelType.VAR,
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
        
        logger.info(f"✅ Simple Risk Modeling test passed")
        
    def test_portfolio_optimization_simple(self):
        """Test simple portfolio optimization functionality"""
        logger.info("Testing Simple Portfolio Optimization...")
        
        # Create minimal test request
        assets = [
            Asset(
                asset_id="BTC",
                expected_return=0.15,
                volatility=0.25
            )
        ]
        
        request = PortfolioOptRequest(
            optimization_id=f"test_opt_{int(time.time())}",
            assets=assets,
            objective="maximize_return",
            constraints=[]
        )
        
        # Test the service
        response = self.service.PortfolioOptimization(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.optimal_weights)
        self.assertGreater(response.expected_return, 0)
        self.assertGreater(response.risk_level, 0)
        
        logger.info(f"✅ Simple Portfolio Optimization test passed")

def run_basic_tests():
    """Run all basic tests"""
    logger.info("🚀 Starting MPC Tools Basic Tests...")
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BasicMPCTests))
    
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
        logger.info("✅ All basic tests passed!")
        return True
    else:
        logger.error("❌ Some basic tests failed!")
        return False

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
