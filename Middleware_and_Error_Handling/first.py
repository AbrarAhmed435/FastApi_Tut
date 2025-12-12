from fastapi import FastAPI,Request
import logging 
from logging.handlers import RotatingFileHandler
import time

app=FastAPI()

handler=RotatingFileHandler(
    "logs/app.log",
    maxBytes=5*1024*1024,
    backupCount=10 # keep latest 10 log files
)

# Max size of log file is 5 mb and so we will have (app.log,app.log1,app.log2)

logging.basicConfig(
    # filename="logs/app.log",
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s-%(message)s",
)


@app.middleware('http')
async def log_requests(request:Request,call_next):
    start_time=time.time()
    client_ip=request.client.host # ip of client 
    method=request.method #(GET,POST)
    url=request.url.path #endpoint("/upload")
    
    # print(f"Request: {method} {url} from {client_ip}")
    logging.info(f"Request: {method} {url} from {client_ip}")
    
    response=await call_next(request)
    
    duration=time.time()-start_time
    
    # print("After endpoint finished")
    
    logging.info(f"Response: {method} {url} completed in {duration:.3f}s")
    
    return response
    
    
@app.get("/hello")
async def hello():
    print("Inside the hello endpoint")
    return {
        "message":"hello world"
    }