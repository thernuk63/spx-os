import logging, os

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/spx.log", encoding="utf-8")
    ]
)

def log_info(msg: str): logging.info(msg)
def log_warn(msg: str): logging.warning(msg)
def log_error(msg: str): logging.error(msg)
