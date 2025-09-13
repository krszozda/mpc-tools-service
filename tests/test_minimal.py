#!/usr/bin/env python3
"""
MPC Tools Service - Minimal Test
Tests minimal MPC Tools service functionality
"""

import logging
import os
import sys
import unittest

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import MPC Tools service
from mpc_tools.service import MPCToolsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalMPCTests(unittest.TestCase):
    """Minimal tests for MPC Tools Service"""
    
    def test_service_initialization(self):
        """Test that MPC Tools service initializes correctly"""
        logger.info("Testing MPC Tools Service Initialization...")
        
        # Verify service is initialized
        service = MPCToolsService()
        self.assertIsNotNone(service)
        self.assertIsInstance(service, MPCToolsService)
        
        logger.info("✅ MPC Tools Service Initialization test passed")
        
    def test_service_attributes(self):
        """Test that MPC Tools service has required attributes"""
        logger.info("Testing MPC Tools Service Attributes...")
        
        service = MPCToolsService()
        
        # Check required attributes exist
        self.assertTrue(hasattr(service, 'redis_client'))
        self.assertTrue(hasattr(service, 'db_pool'))
        self.assertTrue(hasattr(service, 'encryption_key'))
        self.assertTrue(hasattr(service, 'active_computations'))
        self.assertTrue(hasattr(service, 'agent_registry'))
        
        logger.info("✅ MPC Tools Service Attributes test passed")
        
    def test_service_methods(self):
        """Test that MPC Tools service has required methods"""
        logger.info("Testing MPC Tools Service Methods...")
        
        service = MPCToolsService()
        
        # Check required methods exist
        self.assertTrue(hasattr(service, 'SecureAggregation'))
        self.assertTrue(hasattr(service, 'FederatedLearning'))
        self.assertTrue(hasattr(service, 'DifferentialPrivacyQuery'))
        self.assertTrue(hasattr(service, 'AdvancedRiskModeling'))
        self.assertTrue(hasattr(service, 'PortfolioOptimization'))
        self.assertTrue(hasattr(service, 'CoordinateAgents'))
        self.assertTrue(hasattr(service, 'OrchestrateComputation'))
        self.assertTrue(hasattr(service, 'HealthCheck'))
        self.assertTrue(hasattr(service, 'GetServiceStatus'))
        
        logger.info("✅ MPC Tools Service Methods test passed")

def run_minimal_tests():
    """Run all minimal tests"""
    logger.info("🚀 Starting MPC Tools Minimal Tests...")
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MinimalMPCTests))
    
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
        logger.info("✅ All minimal tests passed!")
        return True
    else:
        logger.error("❌ Some minimal tests failed!")
        return False

if __name__ == "__main__":
    success = run_minimal_tests()
    sys.exit(0 if success else 1)
