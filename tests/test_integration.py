#!/usr/bin/env python3
"""
MPC Tools Service - Integration Tests
Tests the complete MPC Tools service functionality including gRPC communication
"""

import asyncio
import grpc
import json
import logging
import os
import sys
import time
from typing import Dict, Any, List
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

class MPCIntegrationTests(unittest.TestCase):
    """Integration tests for MPC Tools Service"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = MPCToolsService()
        self.test_computation_id = f"test_{int(time.time())}"
        self.test_model_id = f"model_{int(time.time())}"
        self.test_optimization_id = f"opt_{int(time.time())}"
        
    def test_secure_aggregation(self):
        """Test secure aggregation functionality"""
        logger.info("Testing Secure Aggregation...")
        
        # Create test data
        agent_data = [
            {
                "agent_id": "agent_1",
                "data": {"value": 100, "weight": 0.5},
                "metadata": {"source": "test"}
            },
            {
                "agent_id": "agent_2", 
                "data": {"value": 200, "weight": 0.3},
                "metadata": {"source": "test"}
            },
            {
                "agent_id": "agent_3",
                "data": {"value": 150, "weight": 0.2},
                "metadata": {"source": "test"}
            }
        ]
        
        request = SecureAggregationRequest(
            computation_id=self.test_computation_id,
            agent_data=[AgentData(
                agent_id=data["agent_id"],
                data=json.dumps(data["data"]),
                metadata=json.dumps(data["metadata"])
            ) for data in agent_data],
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
        self.assertEqual(len(response.participant_ids), 3)
        
        # Verify result contains expected data
        result_data = json.loads(response.result)
        self.assertIn("aggregated_value", result_data)
        self.assertIn("participant_count", result_data)
        
        logger.info(f"✅ Secure Aggregation test passed: {response.result}")
        
    def test_federated_learning(self):
        """Test federated learning functionality"""
        logger.info("Testing Federated Learning...")
        
        # Create test model updates
        updates = [
            {
                "agent_id": "agent_1",
                "model_update": {"weights": [0.1, 0.2, 0.3]},
                "sample_count": 100
            },
            {
                "agent_id": "agent_2",
                "model_update": {"weights": [0.2, 0.3, 0.4]},
                "sample_count": 150
            }
        ]
        
        config = {
            "learning_rate": 0.01,
            "batch_size": 32,
            "epochs": 10
        }
        
        budget = {
            "max_rounds": 5,
            "timeout_seconds": 300
        }
        
        request = FederatedLearningRequest(
            model_id=self.test_model_id,
            updates=[ModelUpdate(
                agent_id=update["agent_id"],
                model_update=json.dumps(update["model_update"]),
                sample_count=update["sample_count"]
            ) for update in updates],
            config=json.dumps(config),
            budget=json.dumps(budget)
        )
        
        # Test the service
        response = self.service.FederatedLearning(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.aggregated_model)
        self.assertGreater(response.accuracy, 0)
        self.assertGreater(response.round_number, 0)
        
        logger.info(f"✅ Federated Learning test passed: accuracy={response.accuracy}")
        
    def test_differential_privacy_query(self):
        """Test differential privacy query functionality"""
        logger.info("Testing Differential Privacy Query...")
        
        request = DPQueryRequest(
            query_id=f"dp_query_{int(time.time())}",
            query_type="count",
            data_sources=["source_1", "source_2"],
            epsilon=1.0,
            delta=1e-5
        )
        
        # Test the service
        response = self.service.DifferentialPrivacyQuery(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.result)
        self.assertEqual(response.privacy_cost, 1.0)
        
        # Verify result contains differentially private data
        result_data = json.loads(response.result)
        self.assertIn("differentially_private_result", result_data)
        self.assertIn("noise_added", result_data)
        
        logger.info(f"✅ Differential Privacy Query test passed: {response.result}")
        
    def test_advanced_risk_modeling(self):
        """Test advanced risk modeling functionality"""
        logger.info("Testing Advanced Risk Modeling...")
        
        factors = [
            {"factor": "market_volatility", "weight": 0.4},
            {"factor": "liquidity", "weight": 0.3},
            {"factor": "correlation", "weight": 0.3}
        ]
        
        request = RiskModelRequest(
            model_id=self.test_model_id,
            asset_ids=["BTC", "ETH", "ADA"],
            model_type="monte_carlo",
            factors=[RiskFactor(
                factor=factor["factor"],
                weight=factor["weight"]
            ) for factor in factors]
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
        
        logger.info(f"✅ Advanced Risk Modeling test passed: VaR95={metrics.var_95}")
        
    def test_portfolio_optimization(self):
        """Test portfolio optimization functionality"""
        logger.info("Testing Portfolio Optimization...")
        
        assets = [
            {"asset_id": "BTC", "expected_return": 0.15, "volatility": 0.25},
            {"asset_id": "ETH", "expected_return": 0.12, "volatility": 0.30},
            {"asset_id": "ADA", "expected_return": 0.08, "volatility": 0.35}
        ]
        
        constraints = [
            {"type": "max_weight", "asset_id": "BTC", "value": 0.5},
            {"type": "min_weight", "asset_id": "ETH", "value": 0.1}
        ]
        
        request = PortfolioOptRequest(
            optimization_id=self.test_optimization_id,
            assets=[Asset(
                asset_id=asset["asset_id"],
                expected_return=asset["expected_return"],
                volatility=asset["volatility"]
            ) for asset in assets],
            objective="maximize_sharpe_ratio",
            constraints=[Constraint(
                type=constraint["type"],
                asset_id=constraint["asset_id"],
                value=constraint["value"]
            ) for constraint in constraints]
        )
        
        # Test the service
        response = self.service.PortfolioOptimization(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.optimal_weights)
        self.assertGreater(response.expected_return, 0)
        self.assertGreater(response.risk_level, 0)
        
        # Verify weights sum to 1
        total_weight = sum(weight.weight for weight in response.optimal_weights)
        self.assertAlmostEqual(total_weight, 1.0, places=2)
        
        logger.info(f"✅ Portfolio Optimization test passed: expected_return={response.expected_return}")
        
    def test_coordinate_agents(self):
        """Test agent coordination functionality"""
        logger.info("Testing Agent Coordination...")
        
        request = CoordinationRequest(
            coordination_id=f"coord_{int(time.time())}",
            agent_ids=["agent_1", "agent_2", "agent_3"],
            type="collaborative_analysis",
            task_description="Analyze market trends collaboratively"
        )
        
        # Test the service
        response = self.service.CoordinateAgents(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.coordination_result)
        self.assertEqual(len(response.agent_statuses), 3)
        
        # Verify all agents are coordinated
        for status in response.agent_statuses:
            self.assertEqual(status.status, "coordinated")
            self.assertGreater(status.last_seen, 0)
        
        logger.info(f"✅ Agent Coordination test passed: {len(response.agent_statuses)} agents")
        
    def test_orchestrate_computation(self):
        """Test computation orchestration functionality"""
        logger.info("Testing Computation Orchestration...")
        
        tasks = [
            {
                "task_id": "task_1",
                "type": "risk_analysis",
                "parameters": {"asset": "BTC", "timeframe": "1d"}
            },
            {
                "task_id": "task_2", 
                "type": "portfolio_optimization",
                "parameters": {"assets": ["BTC", "ETH"], "objective": "max_return"}
            }
        ]
        
        request = OrchestrationRequest(
            orchestration_id=f"orch_{int(time.time())}",
            tasks=[ComputationTask(
                task_id=task["task_id"],
                type=task["type"],
                parameters=json.dumps(task["parameters"])
            ) for task in tasks],
            strategy="parallel",
            max_parallel_tasks=2
        )
        
        # Test the service
        response = self.service.OrchestrateComputation(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.results)
        self.assertEqual(len(response.results), 2)
        
        # Verify all tasks completed
        for result in response.results:
            self.assertTrue(result.success)
            self.assertGreater(result.execution_time_ms, 0)
            self.assertGreater(result.timestamp, 0)
        
        logger.info(f"✅ Computation Orchestration test passed: {len(response.results)} tasks")
        
    def test_service_health(self):
        """Test service health check"""
        logger.info("Testing Service Health...")
        
        request = HealthCheckRequest()
        
        # Test the service
        response = self.service.HealthCheck(request, None)
        
        # Verify response
        self.assertTrue(response.healthy)
        self.assertEqual(response.status, "healthy")
        self.assertIsNotNone(response.dependencies)
        
        logger.info(f"✅ Service Health test passed: {response.status}")
        
    def test_service_status(self):
        """Test service status"""
        logger.info("Testing Service Status...")
        
        request = ServiceStatusRequest()
        
        # Test the service
        response = self.service.GetServiceStatus(request, None)
        
        # Verify response
        self.assertTrue(response.healthy)
        self.assertIsNotNone(response.metrics)
        self.assertGreater(response.uptime_seconds, 0)
        
        logger.info(f"✅ Service Status test passed: uptime={response.uptime_seconds}s")

class MPCPerformanceTests(unittest.TestCase):
    """Performance tests for MPC Tools Service"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = MPCToolsService()
        
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        logger.info("Testing Concurrent Requests...")
        
        async def make_request(request_id: int):
            request = SecureAggregationRequest(
                computation_id=f"concurrent_{request_id}",
                agent_data=[AgentData(
                    agent_id=f"agent_{request_id}",
                    data='{"value": 100}',
                    metadata='{"source": "test"}'
                )],
                aggregation_type="average",
                security_level="medium"
            )
            
            start_time = time.time()
            response = self.service.SecureAggregation(request, None)
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "success": response.success,
                "execution_time": end_time - start_time
            }
        
        # Run 10 concurrent requests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tasks = [make_request(i) for i in range(10)]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        
        # Verify all requests succeeded
        for result in results:
            self.assertTrue(result["success"])
            self.assertLess(result["execution_time"], 1.0)  # Should complete within 1 second
        
        logger.info(f"✅ Concurrent Requests test passed: {len(results)} requests")
        
    def test_large_data_handling(self):
        """Test handling of large data sets"""
        logger.info("Testing Large Data Handling...")
        
        # Create large dataset
        large_agent_data = []
        for i in range(1000):
            large_agent_data.append(AgentData(
                agent_id=f"agent_{i}",
                data=json.dumps({"value": i, "weight": 1.0/1000}),
                metadata=json.dumps({"source": "large_test"})
            ))
        
        request = SecureAggregationRequest(
            computation_id="large_data_test",
            agent_data=large_agent_data,
            aggregation_type="weighted_average",
            security_level="high"
        )
        
        start_time = time.time()
        response = self.service.SecureAggregation(request, None)
        end_time = time.time()
        
        # Verify response
        self.assertTrue(response.success)
        self.assertEqual(len(response.participant_ids), 1000)
        self.assertLess(end_time - start_time, 5.0)  # Should complete within 5 seconds
        
        logger.info(f"✅ Large Data Handling test passed: {len(response.participant_ids)} agents in {end_time - start_time:.2f}s")

def run_integration_tests():
    """Run all integration tests"""
    logger.info("🚀 Starting MPC Tools Integration Tests...")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add integration tests
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MPCIntegrationTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MPCPerformanceTests))
    
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
        logger.info("✅ All integration tests passed!")
        return True
    else:
        logger.error("❌ Some integration tests failed!")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
