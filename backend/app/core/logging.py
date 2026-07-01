import json
import logging
import logging.config
import os
import sys
from datetime import datetime, timezone
from typing import Any

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging in production environments.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        for key, val in record.__dict__.items():
            if key not in {
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "levelname", "levelno", "lineno", "module", "msecs",
                "msg", "name", "pathname", "process", "processName", "relativeCreated",
                "stack_info", "thread", "threadName"
            }:
                try:
                    json.dumps(val)
                    log_record[key] = val
                except (TypeError, OverflowError):
                    log_record[key] = str(val)

        return json.dumps(log_record)


def setup_logging() -> None:
    """
    Configures application-wide logging.
    Supports console/JSON logging to stdout, and optionally rotating file logging.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "console").lower()  # 'console' or 'json'
    
    # File logging config
    log_to_file = os.getenv("LOG_TO_FILE", "false").lower() == "true"
    log_file_path = os.getenv("LOG_FILE_PATH", "logs/app.log")
    log_file_max_bytes = int(os.getenv("LOG_FILE_MAX_BYTES", "10485760"))  # Default 10MB
    log_file_backup_count = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))    # Default keep 5 files

    # Handlers list for root logger
    active_handlers = ["default"]

    # Base logging configuration dictionary
    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JSONFormatter,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": log_format if log_format in {"console", "json"} else "console",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": active_handlers,
                "level": log_level,
            },
            "uvicorn": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "level": log_level,
                "propagate": True,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "azure.cosmos": {
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

    # Setup file logging handler if enabled
    if log_to_file:
        try:
            # Create logging directory if it doesn't exist
            log_dir = os.path.dirname(log_file_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            logging_config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": log_format if log_format in {"console", "json"} else "console",
                "filename": log_file_path,
                "maxBytes": log_file_max_bytes,
                "backupCount": log_file_backup_count,
                "encoding": "utf8",
            }
            active_handlers.append("file")
        except Exception as e:
            # Fallback output to stdout if directory creation or file setup fails
            print(f"WARNING: Failed to configure file logging handler: {str(e)}", file=sys.stderr)

    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Configure Azure Application Insights if connection string exists
    from app.core.config import settings
    if settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
        try:
            # pyrefly: ignore [missing-import]
            from azure.monitor.opentelemetry import configure_azure_monitor
            configure_azure_monitor(connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING)
            print("Azure Monitor OpenTelemetry configured.")
        except ImportError:
            print("WARNING: azure-monitor-opentelemetry is not installed. Application Insights integration is disabled.", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Failed to configure Azure Monitor OpenTelemetry: {str(e)}", file=sys.stderr)


    # Confirmation message
    root_logger = logging.getLogger()
    root_logger.info(
        f"Logging configured. Level: {log_level}, Format: {log_format}, File Logging: {log_to_file} ({log_file_path if log_to_file else 'N/A'})"
    )
