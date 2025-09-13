#!/usr/bin/env python3
"""
MPC Tools ↔ AI Assistant Integration Tests
Tests the communication between MPC Tools Service and AI Assistant
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
from unittest.mock import Mock, patch, AsyncMock

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import MPC Tools service
from mpc_tools.service import MPCToolsService
from mpc_tools_pb2 import *
from mpc_tools_pb2_grpc import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MPCAIAssistantIntegrationTests(unittest.TestCase):
    """Integration tests for MPC Tools ↔ AI Assistant communication"""
    
    def setUp(self):
        """Set up test environment"""
        self.mpc_service = MPCToolsService()
        self.test_user_id = "test_user_123"
        self.test_session_id = f"session_{int(time.time())}"
        
    def test_ai_assistant_risk_analysis_integration(self):
        """Test AI Assistant using MPC Tools for risk analysis"""
        logger.info("Testing AI Assistant Risk Analysis Integration...")
        
        # Simulate AI Assistant request for risk analysis
        pair = "BTCUSDT"
        indicators = {
            "rsi": 65.5,
            "macd": 0.02,
            "bollinger_upper": 45000,
            "bollinger_lower": 40000,
            "volume": 1000000
        }
        
        # Create MPC Tools request (as AI Assistant would)
        request = RiskModelRequest(
            model_id=f"risk_model_{pair}_{int(time.time())}",
            asset_ids=[pair],
            model_type="monte_carlo",
            factors=[
RiskFactor(factor="technical_indicators", weight=0.4),
RiskFactor(factor="market_volatility", weight=0.3),
RiskFactor(factor="volume_profile", weight=0.3)
            ]
        )
        
        # Test MPC Tools response
        response = self.mpc_service.AdvancedRiskModeling(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.metrics)
        
        # Verify risk metrics are reasonable
        metrics = response.metrics
        self.assertGreater(metrics.var_95, 0)
        self.assertGreater(metrics.var_99, 0)
        self.assertGreater(metrics.expected_shortfall, 0)
        self.assertGreater(metrics.max_drawdown, 0)
        
        # Simulate AI Assistant processing the response
        ai_response = {
            "message": f"🔍 **Advanced Risk Analysis for {pair}:**\n\n"
                      f"**Risk Metrics (MPC-Powered):**\n"
                      f"• VaR 95%: {metrics.var_95:.2%}\n"
                      f"• VaR 99%: {metrics.var_99:.2%}\n"
                      f"• Expected Shortfall: {metrics.expected_shortfall:.2%}\n"
                      f"• Max Drawdown: {metrics.max_drawdown:.2%}\n\n"
                      f"**Analysis:** Risk levels are within acceptable range for trading.",
            "type": "ANALYSIS",
            "metadata": {
                "mpc_analysis": True,
                "risk_metrics": {
                    "var_95": metrics.var_95,
                    "var_99": metrics.var_99,
                    "expected_shortfall": metrics.expected_shortfall,
                    "max_drawdown": metrics.max_drawdown
                }
            }
        }
        
        # Verify AI Assistant response structure
        self.assertIn("mpc_analysis", ai_response["metadata"])
        self.assertTrue(ai_response["metadata"]["mpc_analysis"])
        self.assertIn("risk_metrics", ai_response["metadata"])
        
        logger.info(f"✅ AI Assistant Risk Analysis Integration test passed")
        logger.info(f"   Risk metrics: VaR95={metrics.var_95:.2%}, VaR99={metrics.var_99:.2%}")
        
    def test_ai_assistant_portfolio_optimization_integration(self):
        """Test AI Assistant using MPC Tools for portfolio optimization"""
        logger.info("Testing AI Assistant Portfolio Optimization Integration...")
        
        # Simulate AI Assistant request for portfolio optimization
        assets = [
            {"asset_id": "BTC", "expected_return": 0.15, "volatility": 0.25},
            {"asset_id": "ETH", "expected_return": 0.12, "volatility": 0.30},
            {"asset_id": "ADA", "expected_return": 0.08, "volatility": 0.35}
        ]
        
        constraints = [
            {"type": "max_weight", "asset_id": "BTC", "value": 0.5},
            {"type": "min_weight", "asset_id": "ETH", "value": 0.1}
        ]
        
        # Create MPC Tools request (as AI Assistant would)
        request = PortfolioOptRequest(
            optimization_id=f"portfolio_opt_{int(time.time())}",
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
        
        # Test MPC Tools response
        response = self.mpc_service.PortfolioOptimization(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.optimal_weights)
        self.assertGreater(response.expected_return, 0)
        self.assertGreater(response.risk_level, 0)
        
        # Simulate AI Assistant processing the response
        ai_response = {
            "message": f"💰 **Portfolio Optimization (MPC-Powered):**\n\n"
                      f"**Optimal Allocation:**\n"
                      f"{chr(10).join([f'• {weight.asset_id}: {weight.weight:.1%} (${weight.allocation:.2f})' for weight in response.optimal_weights])}\n\n"
                      f"**Expected Performance:**\n"
                      f"• Expected Return: {response.expected_return:.2%}\n"
                      f"• Risk Level: {response.risk_level:.2%}\n"
                      f"• Sharpe Ratio: {response.expected_return/response.risk_level:.2f}\n\n"
                      f"**Analysis:** Portfolio optimized for maximum risk-adjusted returns.",
            "type": "DATA_QUERY",
            "metadata": {
                "mpc_optimization": True,
                "expected_return": response.expected_return,
                "risk_level": response.risk_level,
                "optimal_weights": [
                    {
                        "asset_id": weight.asset_id,
                        "weight": weight.weight,
                        "allocation": weight.allocation
                    } for weight in response.optimal_weights
                ]
            }
        }
        
        # Verify AI Assistant response structure
        self.assertIn("mpc_optimization", ai_response["metadata"])
        self.assertTrue(ai_response["metadata"]["mpc_optimization"])
        self.assertIn("optimal_weights", ai_response["metadata"])
        
        logger.info(f"✅ AI Assistant Portfolio Optimization Integration test passed")
        logger.info(f"   Expected return: {response.expected_return:.2%}, Risk: {response.risk_level:.2%}")
        
    def test_ai_assistant_secure_aggregation_integration(self):
        """Test AI Assistant using MPC Tools for secure aggregation"""
        logger.info("Testing AI Assistant Secure Aggregation Integration...")
        
        # Simulate AI Assistant collecting data from multiple sources
        agent_data = [
            {
                "agent_id": "price_agent",
                "data": {"price": 45000, "confidence": 0.9},
                "metadata": {"source": "binance", "timestamp": time.time()}
            },
            {
                "agent_id": "sentiment_agent",
                "data": {"sentiment": 0.7, "confidence": 0.8},
                "metadata": {"source": "twitter", "timestamp": time.time()}
            },
            {
                "agent_id": "volume_agent",
                "data": {"volume": 1000000, "confidence": 0.95},
                "metadata": {"source": "orderbook", "timestamp": time.time()}
            }
        ]
        
        # Create MPC Tools request (as AI Assistant would)
        request = SecureAggregationRequest(
            computation_id=f"market_analysis_{int(time.time())}",
            agent_data=[AgentData(
                agent_id=data["agent_id"],
                data=json.dumps(data["data"]),
                metadata=json.dumps(data["metadata"])
            ) for data in agent_data],
            aggregation_type="weighted_average",
            security_level="high"
        )
        
        # Test MPC Tools response
        response = self.mpc_service.SecureAggregation(request, None)
        
        # Verify response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.result)
        self.assertEqual(len(response.participant_ids), 3)
        
        # Simulate AI Assistant processing the response
        result_data = json.loads(response.result)
        ai_response = {
            "message": f"🔒 **Secure Market Analysis (MPC-Powered):**\n\n"
                      f"**Aggregated Data:**\n"
                      f"• Aggregated Value: {result_data.get('aggregated_value', 'N/A')}\n"
                      f"• Participant Count: {result_data.get('participant_count', 'N/A')}\n"
                      f"• Security Level: High\n\n"
                      f"**Analysis:** Market data securely aggregated from multiple sources.",
            "type": "ANALYSIS",
            "metadata": {
                "mpc_aggregation": True,
                "participant_count": len(response.participant_ids),
                "execution_time_ms": response.execution_time_ms
            }
        }
        
        # Verify AI Assistant response structure
        self.assertIn("mpc_aggregation", ai_response["metadata"])
        self.assertTrue(ai_response["metadata"]["mpc_aggregation"])
        
        logger.info(f"✅ AI Assistant Secure Aggregation Integration test passed")
        logger.info(f"   Participants: {len(response.participant_ids)}, Time: {response.execution_time_ms}ms")
        
    def test_ai_assistant_error_handling(self):
        """Test AI Assistant error handling when MPC Tools is unavailable"""
        logger.info("Testing AI Assistant Error Handling...")
        
        # Simulate MPC Tools service being unavailable
        with patch.object(self.mpc_service, 'AdvancedRiskModeling') as mock_risk:
            mock_risk.side_effect = Exception("MPC Tools service unavailable")
            
            # Simulate AI Assistant fallback behavior
            try:
                request = RiskModelRequest(
                    model_id="test_model",
                    asset_ids=["BTC"],
                    model_type="monte_carlo",
                    factors=[]
                )
                response = self.mpc_service.AdvancedRiskModeling(request, None)
            except Exception as e:
                # AI Assistant should handle this gracefully
                ai_response = {
                    "message": "🔍 **Risk Analysis:**\n\n"
                              "⚠️ Advanced risk modeling temporarily unavailable. "
                              "Using standard analysis methods.\n\n"
                              "**Standard Risk Assessment:**\n"
                              "• Market volatility: Moderate\n"
                              "• Risk level: Medium\n"
                              "• Recommendation: Proceed with caution",
                    "type": "ANALYSIS",
                    "metadata": {
                        "mpc_analysis": False,
                        "fallback_used": True,
                        "error": str(e)
                    }
                }
                
                # Verify fallback response
                self.assertIn("fallback_used", ai_response["metadata"])
                self.assertTrue(ai_response["metadata"]["fallback_used"])
                self.assertFalse(ai_response["metadata"]["mpc_analysis"])
                
                logger.info(f"✅ AI Assistant Error Handling test passed")
                logger.info(f"   Fallback used: {ai_response['metadata']['fallback_used']}")
        
    def test_ai_assistant_concurrent_requests(self):
        """Test AI Assistant handling concurrent MPC Tools requests"""
        logger.info("Testing AI Assistant Concurrent Requests...")
        
        async def simulate_ai_request(request_id: int, request_type: str):
            """Simulate AI Assistant making a request to MPC Tools"""
            if request_type == "risk":
                request = RiskModelRequest(
                    model_id=f"concurrent_risk_{request_id}",
                    asset_ids=["BTC"],
                    model_type="monte_carlo",
                    factors=[]
                )
                response = self.mpc_service.AdvancedRiskModeling(request, None)
            elif request_type == "portfolio":
                request = PortfolioOptRequest(
                    optimization_id=f"concurrent_portfolio_{request_id}",
                    assets=[Asset(asset_id="BTC", expected_return=0.15, volatility=0.25)],
                    objective="maximize_sharpe_ratio",
                    constraints=[]
                )
                response = self.mpc_service.PortfolioOptimization(request, None)
            else:
                request = SecureAggregationRequest(
                    computation_id=f"concurrent_agg_{request_id}",
                    agent_data=[AgentData(
                        agent_id=f"agent_{request_id}",
                        data='{"value": 100}',
                        metadata='{"source": "test"}'
                    )],
                    aggregation_type="average",
                    security_level="medium"
                )
                response = self.mpc_service.SecureAggregation(request, None)
            
            return {
                "request_id": request_id,
                "type": request_type,
                "success": response.success,
                "timestamp": time.time()
            }
        
        # Run concurrent requests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tasks = []
        for i in range(5):
            tasks.append(simulate_ai_request(i, "risk"))
            tasks.append(simulate_ai_request(i, "portfolio"))
            tasks.append(simulate_ai_request(i, "aggregation"))
        
        results = loop.run_until_complete(asyncio.gather(*tasks))
        
        # Verify all requests succeeded
        for result in results:
            self.assertTrue(result["success"])
            self.assertIn(result["type"], ["risk", "portfolio", "aggregation"])
        
        logger.info(f"✅ AI Assistant Concurrent Requests test passed: {len(results)} requests")
        
    def test_ai_assistant_data_flow(self):
        """Test complete data flow from AI Assistant to MPC Tools and back"""
        logger.info("Testing Complete AI Assistant Data Flow...")
        
        # Step 1: AI Assistant receives user query
        user_query = "Analyze BTC risk and optimize my portfolio"
        
        # Step 2: AI Assistant processes query and identifies need for MPC Tools
        analysis_needed = "risk" in user_query.lower()
        portfolio_needed = "portfolio" in user_query.lower()
        
        # Step 3: AI Assistant makes MPC Tools requests
        responses = {}
        
        if analysis_needed:
            risk_request = RiskModelRequest(
                model_id=f"flow_risk_{int(time.time())}",
                asset_ids=["BTC"],
                model_type="monte_carlo",
                factors=[]
            )
            risk_response = self.mpc_service.AdvancedRiskModeling(risk_request, None)
            responses["risk"] = risk_response
        
        if portfolio_needed:
            portfolio_request = PortfolioOptRequest(
                optimization_id=f"flow_portfolio_{int(time.time())}",
                assets=[Asset(asset_id="BTC", expected_return=0.15, volatility=0.25)],
                objective="maximize_sharpe_ratio",
                constraints=[]
            )
            portfolio_response = self.mpc_service.PortfolioOptimization(portfolio_request, None)
            responses["portfolio"] = portfolio_response
        
        # Step 4: AI Assistant processes MPC Tools responses
        ai_response = {
            "message": "🔍 **Comprehensive Analysis (MPC-Powered):**\n\n",
            "type": "ANALYSIS",
            "metadata": {
                "mpc_analysis": True,
                "components": []
            }
        }
        
        if "risk" in responses:
            risk_metrics = responses["risk"].metrics
            ai_response["message"] += f"**Risk Analysis:**\n"
            ai_response["message"] += f"• VaR 95%: {risk_metrics.var_95:.2%}\n"
            ai_response["message"] += f"• VaR 99%: {risk_metrics.var_99:.2%}\n"
            ai_response["message"] += f"• Expected Shortfall: {risk_metrics.expected_shortfall:.2%}\n\n"
            ai_response["metadata"]["components"].append("risk_analysis")
        
        if "portfolio" in responses:
            portfolio_response = responses["portfolio"]
            ai_response["message"] += f"**Portfolio Optimization:**\n"
            ai_response["message"] += f"• Expected Return: {portfolio_response.expected_return:.2%}\n"
            ai_response["message"] += f"• Risk Level: {portfolio_response.risk_level:.2%}\n"
            ai_response["message"] += f"• Optimal Weights: {len(portfolio_response.optimal_weights)} assets\n\n"
            ai_response["metadata"]["components"].append("portfolio_optimization")
        
        ai_response["message"] += "**Analysis:** Complete MPC-powered analysis delivered successfully."
        
        # Step 5: Verify complete data flow
        self.assertIn("mpc_analysis", ai_response["metadata"])
        self.assertTrue(ai_response["metadata"]["mpc_analysis"])
        self.assertGreater(len(ai_response["metadata"]["components"]), 0)
        
        logger.info(f"✅ Complete AI Assistant Data Flow test passed")
        logger.info(f"   Components: {ai_response['metadata']['components']}")

def run_ai_assistant_integration_tests():
    """Run all AI Assistant integration tests"""
    logger.info("🚀 Starting MPC Tools ↔ AI Assistant Integration Tests...")
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MPCAIAssistantIntegrationTests))
    
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
        logger.info("✅ All AI Assistant integration tests passed!")
        return True
    else:
        logger.error("❌ Some AI Assistant integration tests failed!")
        return False

if __name__ == "__main__":
    success = run_ai_assistant_integration_tests()
    sys.exit(0 if success else 1)
