import os
import logging
import json
from datetime import datetime, timezone
from backend.app.config.settings import settings

# Ensure log directory exists
os.makedirs(settings.LOG_DIR, exist_ok=True)

class StructuredJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Pull standard keys if they are passed in the 'extra' dictionary
        for key in ["request_id", "execution_time_ms", "path", "method", "status_code"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logger():
    app_logger = logging.getLogger("sentiment_analysis")
    app_logger.setLevel(logging.INFO)
    app_logger.propagate = False

    # Prevent appending multiple handlers during dev server reloads
    if app_logger.hasHandlers():
        app_logger.handlers.clear()

    # Info handler
    info_path = os.path.join(settings.LOG_DIR, "info.log")
    info_handler = logging.FileHandler(info_path, encoding="utf-8")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(StructuredJSONFormatter())

    # Error handler
    error_path = os.path.join(settings.LOG_DIR, "error.log")
    error_handler = logging.FileHandler(error_path, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredJSONFormatter())

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    app_logger.addHandler(info_handler)
    app_logger.addHandler(error_handler)
    app_logger.addHandler(console_handler)

    return app_logger

logger = setup_logger()
