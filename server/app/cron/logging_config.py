import logging

# Create a custom logger
logger = logging.getLogger('CronLogger')

# Create handlers
console_handler = logging.StreamHandler()

# Create formatters and add it to handlers
formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)

# Configuring Flask's logger to be less verbose
logging.getLogger('werkzeug').setLevel(logging.ERROR)


def setup_logging(verbose=False):
    # Adjust logging level based on the verbosity option.

    if verbose:
        logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)
