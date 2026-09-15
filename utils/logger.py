import logging

_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

_file_handler = logging.FileHandler('app.log', mode='w')
_file_handler.setFormatter(_formatter)

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_formatter)

# Configure the logger to write to both the console and app.log
logging.basicConfig(level=logging.INFO, handlers=[_file_handler, _console_handler])

_logger = logging.getLogger(__name__)