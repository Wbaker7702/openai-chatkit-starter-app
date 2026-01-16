import re
import logging
import time
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("enterprise-security")

class SecurityConfig:
    API_KEY_HEADER = "X-Enterprise-Auth"
    REQUIRED_API_KEY = os.getenv("ENTERPRISE_API_KEY")  # In production, load from env
    ENABLE_PII_REDACTION = True

def redact_pii(text: str) -> str:
    """Redacts emails and phone numbers from text."""
    if not SecurityConfig.ENABLE_PII_REDACTION:
        return text
    
    # Simple regex for email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, '[REDACTED_EMAIL]', text)
    
    # Simple regex for phone (US format roughly)
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    text = re.sub(phone_pattern, '[REDACTED_PHONE]', text)
    
    return text

class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Log Request
        logger.info(f"Incoming Request: {request.method} {request.url.path} | IP: {client_ip}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log Response
            logger.info(f"Response: {response.status_code} | Duration: {process_time:.4f}s")
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise e

def verify_api_key(request: Request):
    """Dependency to verify API Key."""
    required_key = SecurityConfig.REQUIRED_API_KEY
    if not required_key:
        logger.critical("CRITICAL: ENTERPRISE_API_KEY is not configured on the server.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not configured.",
        )

    provided_key = request.headers.get(SecurityConfig.API_KEY_HEADER)

    if not provided_key or not secrets.compare_digest(provided_key, required_key):
        logger.warning(f"Unauthorized access attempt from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return provided_key
