import logging
import time

from src.utils.paths import LOG_DIR

LOG_FILE = LOG_DIR / "pipeline.log"

def get_logger(name: str):
    logger = logging.getLogger(name)

    if logger.handlers: #kiểm tra logger có handler không
        return logger

    logger.setLevel(logging.INFO) 
    #Thứ tự các level: debug -> info -> warning -> error -> critical
    #Set level tối thiểu là info -> debug sẽ không được tiếp tục xử lý
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    formatter.converter = time.gmtime 
    
    file_handler = logging.FileHandler(LOG_FILE) #file_handler ghi log vào file log
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()#consol_handler ghi log console/terminal
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
