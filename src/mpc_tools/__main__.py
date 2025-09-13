"""
MPC Tools Service Entry Point

Advanced Multi-Party Computation Tools for AI Agents
"""

import asyncio
import logging
import os
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def serve():
    """Start the MPC Tools gRPC server"""
    
    # Import service and protobuf stubs
    from .service import MPCToolsService
    try:
        import mpc_tools_pb2_grpc as pb2_grpc
        add_MPCToolsServiceServicer_to_server = pb2_grpc.add_MPCToolsServiceServicer_to_server
    except ImportError:
        logger.error("Failed to import protobuf stubs. Make sure proto files are compiled.")
        return
    
    # Create server
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=20))
    
    # Add service
    mpc_service = MPCToolsService()
    add_MPCToolsServiceServicer_to_server(mpc_service, server)
    
    # Start service (initialize database, Redis, etc.)
    await mpc_service.start()
    
    # Add reflection for debugging
    try:
        from . import mpc_tools_pb2 as pb2
        SERVICE_NAMES = (
            pb2.DESCRIPTOR.services_by_name['MPCToolsService'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
        logger.info("gRPC reflection enabled")
    except ImportError:
        logger.warning("gRPC reflection not available - protobuf files not compiled")
    
    # Configure server
    listen_addr = f"[::]:{os.getenv('PORT', '50061')}"
    server.add_insecure_port(listen_addr)
    
    # Start server
    logger.info(f"Starting MPC Tools Service on {listen_addr}")
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down MPC Tools Service...")
        await server.stop(5)


if __name__ == "__main__":
    asyncio.run(serve())
