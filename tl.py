import logging
from griffe.logger import get_logger, Logger, LogLevel


logging.basicConfig(format="%(message)s", level=0)
logger = get_logger(__name__)

Logger.add_message("trace", "trace")

Logger.add_message("ntrace", "trace", level=LogLevel.trace)
Logger.add_message("ndebug", "debug", level=LogLevel.debug)
Logger.add_message("ninfo", "info", level=LogLevel.info)
Logger.add_message("nsuccess", "success", level=LogLevel.success)
Logger.add_message("nwarning", "warning", level=LogLevel.warning)
Logger.add_message("nerror", "error", level=LogLevel.error)
Logger.add_message("ncritical", "critical", level=LogLevel.critical)

logger.ntrace()
logger.ndebug()
logger.ninfo()
logger.nsuccess()
logger.nwarning()
logger.nerror()
logger.ncritical()
