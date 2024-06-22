import sys

sys.path.append('.')
import inspect
import logging
import os
from logging.handlers import TimedRotatingFileHandler



FORMAT=logging.Formatter("%(levelname) -10s- %(asctime)s- %(name)s - %(message)s - function=%(funcName)s - line=%(lineno)s", "%H:%M:%S ")
# print(logging.Handler())

if not os.path.isdir(os.path.join(os.getcwd(), "logs")):
    os.mkdir(os.path.join(os.getcwd(), "logs"))

def log_level_get():
    log_level = os.getenv("LOG_LEVEL")
    if log_level == None or log_level.upper() not in ["DEBUG", "INFO", "ERROR", "EXCEPTION", "CUSTOMER"]:
        log_level = "INFO" #"DEBUG"
    log_level = log_level.upper()
    return log_level

# get the filepath to the importer
def caller_name() -> str:
    frame=inspect.currentframe()
    frame=frame.f_back.f_back
    code=frame.f_code
    return os.path.relpath(code.co_filename).rstrip(".py").replace("/", ".").replace("\\",".")

def logfile_path_get(name: str) -> str:
  name = name.replace(".__init__", "").split(".")
  name[-1] += ".log"

  res = os.path.join("logs", *name)
  dir_path = os.path.join("logs", *name[:-1])

  if not os.path.isdir(dir_path):
    os.makedirs(dir_path)
  return res


def get_logger(name: str = None, logfile: bool = True, console_log: bool = True) -> logging.Logger:
    if not name:
        name = caller_name()



    logger = logging.getLogger(name)
    logger.setLevel(log_level_get())


    if console_log:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMAT)
        logger.addHandler(console_handler)

    if logfile:
        file = logfile_path_get(name)
        file_handler = TimedRotatingFileHandler(file, when="midnight", interval=1)
        file_handler.setFormatter(FORMAT)
        logger.addHandler(file_handler)

    if not logger.handlers:
        raise MissingHandlerError(f"No Handler was configured for logger: {name}")

    return logger



class MissingHandlerError(Exception):
    pass


if __name__ == '__main__':
    logger = get_logger()