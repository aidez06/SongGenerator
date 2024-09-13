import logging

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Set up logging to file only, with no console output
logging.basicConfig(
    filename="suno_cookie.log",  # Log to file
    filemode="a",  # Append to the log file
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO  # Adjust the level as needed (INFO, DEBUG, WARNING, etc.)
)

# Alternatively, you can explicitly create a FileHandler and set it manually:
file_handler = logging.FileHandler("suno_cookie.log", mode='a')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Clear existing handlers and set only the file handler
logging.getLogger().handlers = [file_handler]

logging.info("Logging configured to file only, console output removed.")
