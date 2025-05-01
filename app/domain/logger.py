import logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)