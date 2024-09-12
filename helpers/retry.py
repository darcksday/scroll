import time

from loguru import logger

MAX_RETRIES = 10


def retry(func):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"{e}. {'Retry...' if retries + 1 < MAX_RETRIES else 'Max retries reached, skip.'}")
                time.sleep(10)
                retries += 1

    return wrapper
