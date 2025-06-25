from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import config
from app.core.logging import setup_logging, get_logger
import time
import uuid

# Setup logging first
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app with configuration
app_config = config.get_section("app")
app = FastAPI(
    title=app_config.get("name", "Renter Chat API"),
    version=app_config.get("version", "1.0.0"),
    debug=config.get("server.debug", False)
)

# CORS configuration
cors_config = config.get_section("cors")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get("allow_origins", ["http://localhost:3000"]),
    allow_credentials=cors_config.get("allow_credentials", True),
    allow_methods=cors_config.get("allow_methods", ["*"]),
    allow_headers=cors_config.get("allow_headers", ["*"]),
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if config.get("observability.enable_request_logging", True):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request details at DEBUG level (without consuming body)
        headers = dict(request.headers)
        query_params = dict(request.query_params)
        
        start_time = time.time()
        
        # Debug level logging with request details (no body to avoid consumption)
        logger.debug(f"Request started - ID: {request_id}")
        logger.debug(f"  Method: {request.method}")
        logger.debug(f"  URL: {request.url}")
        logger.debug(f"  Headers: {headers}")
        logger.debug(f"  Query Params: {query_params}")
        
        # Info level logging for basic request info
        logger.info(f"Request started - ID: {request_id}, Method: {request.method}, URL: {request.url}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Debug level logging with response details
        logger.debug(f"Request completed - ID: {request_id}")
        logger.debug(f"  Status: {response.status_code}")
        logger.debug(f"  Duration: {process_time:.3f}s")
        logger.debug(f"  Response Headers: {dict(response.headers)}")
        
        # Info level logging for basic response info
        logger.info(f"Request completed - ID: {request_id}, Status: {response.status_code}, Duration: {process_time:.3f}s")
        
        response.headers["X-Request-ID"] = request_id
        return response
    else:
        return await call_next(request)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": f"{app_config.get('name', 'Renter Chat API')} is running",
        "environment": config.environment,
        "version": app_config.get("version", "1.0.0")
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": config.environment}

if __name__ == "__main__":
    import uvicorn
    
    server_config = config.get_section("server")
    logger.info(f"Starting server in {config.environment} mode")
    logger.info(f"Server config: {server_config}")
    
    uvicorn.run(
        app,
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 8000),
        reload=server_config.get("reload", False),
        log_level=config.get("logging.level", "info").lower()
    )