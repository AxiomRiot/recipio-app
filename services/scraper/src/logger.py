import json
import logging
import traceback

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
        }

        # Attach exception info if present (e.g. logger.exception(...))
        if record.exc_info:
            log_record["exception"] = "".join(
                traceback.format_exception(*record.exc_info)
            )

        # Allow arbitrary structured fields via logger.info("msg", extra={"key": "value"})
        reserved = set(vars(logging.makeLogRecord({})).keys()) | {"message"}
        extras = {
            k: v for k, v in vars(record).items()
            if k not in reserved and not k.startswith("_")
        }
        if extras:
            log_record.update(extras)

        return json.dumps(log_record)


def get_json_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)

    return logger