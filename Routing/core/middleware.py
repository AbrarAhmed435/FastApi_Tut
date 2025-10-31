import os
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

LOG_DIR="logs"
os.makedirs(LOG_DIR,exist_ok=True)

LOG_FILE=os.path.join(LOG_DIR,"app.log")

logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


logger=logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request:Request,call_next):
        start_time=time.time()
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response: Response= await call_next(request)
        except Exception as e:
            logger.exception(f"❌Erro processing {request.method} {request.url.path}")
            raise e
        
        process_time=(time.time()-start_time)*1000
        client_ip=request.client.host if request.client else "Unknown"
        
        logger.info(
            f" Response: {request.method} {request.url.path} |"
            f"Status:{response.status_code} | Time:{process_time:.2f}ms | IP:{client_ip}"
        )
        return response
        