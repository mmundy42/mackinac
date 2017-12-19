import logging

# Configure a logger for mackinac
LOGGER = logging.getLogger('mackinac')
LOGGER.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.WARNING)
LOGGER.addHandler(handler)
