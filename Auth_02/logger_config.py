import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Ensure logs folder exists
Path("logs").mkdir(exist_ok=True)

# Create RotatingFileHandler
file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=10 #keep last 10 backuups
)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Create logger
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.propagate = False  # prevents double logging
