import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Context variable to store request ID so other parts of the app can access it if needed
request_id_contextvar: ContextVar[str] = ContextVar("request_id", default="")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract or generate correlation/request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-ID", request_id)
        
        # Set context variables
        token = request_id_contextvar.set(request_id)
        
        # Inject into request state for easy access in routes
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        
        start_time = time.perf_counter()
        
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None
            }
        )
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            
            # Add headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2)
                }
            )
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time_ms": round(process_time * 1000, 2),
                    "error": str(e)
                },
                exc_info=True
            )
            raise e
        finally:
            request_id_contextvar.reset(token)
