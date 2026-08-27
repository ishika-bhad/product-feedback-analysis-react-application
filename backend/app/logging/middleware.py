import time
import contextvars
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.logging.logger import logger

# ContextVar to store request_id throughout the request lifecycle
request_id_ctx = contextvars.ContextVar("request_id", default="N/A")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Check header for X-Request-ID (usually for GET historical requests)
        request_id = request.headers.get("x-request-id", "N/A")
        token = request_id_ctx.set(request_id)
        
        response = None
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Let the exception propagate to global handlers, we'll log in finally
            raise e
        finally:
            duration = int((time.time() - start_time) * 1000)
            current_request_id = request_id_ctx.get()
            
            status_code = response.status_code if response else 500
            path = request.url.path
            method = request.method
            
            log_msg = f"{method} {path} - Status: {status_code} - Duration: {duration}ms"
            extra_fields = {
                "request_id": current_request_id,
                "execution_time_ms": duration,
                "path": path,
                "method": method,
                "status_code": status_code
            }
            
            if status_code >= 400:
                logger.error(log_msg, extra=extra_fields)
            else:
                logger.info(log_msg, extra=extra_fields)
                
            request_id_ctx.reset(token)
