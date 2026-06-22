import logging

class ScraperLogger(logging.Formatter):
  grey = "\x1b[38;20m"
  yellow = "\x1b[33;20m"
  red = "\x1b[31;20m"
  bold_red = "\x1b[31;1m"
  reset = "\x1b[0m"

  log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  LEVEL_COLORS = {
    logging.DEBUG: grey + log_format + reset,
    logging.INFO: grey + log_format + reset, # Keeps timestamp metadata subtle
    logging.WARNING: yellow + log_format + reset,
    logging.ERROR: red + log_format + reset,
    logging.CRITICAL: bold_red + log_format + reset
  }

  def format(self, record):
    log_fmt = self.LEVEL_COLORS.get(record.levelno, self.log_format)
    formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
    return formatter.format(record)


def get_color_logger(name: str) -> logging.Logger:
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)

  # Prevent duplicating logs if handlers were already attached
  if not logger.handlers:
      console_handler = logging.StreamHandler()
      console_handler.setLevel(logging.DEBUG)
      console_handler.setFormatter(ScraperLogger())
      logger.addHandler(console_handler)
      
  return logger