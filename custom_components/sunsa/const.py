"""Constants for the Pysunsa integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final


DOMAIN: Final = "sunsa"
IDDEVICE: Final = "idDevice"
VALUE: Final = "value"
UNIT: Final = "unit"
TEXT: Final = "text"
CLOSED_POSITION: Final = 100
OPEN_POSITION: Final = 0
DEFAULT_SMART_HOME_POISTION: Final = "defaultSmartHomeDirection"
RIGHT: Final = "Right"
USER_ID: Final = "user_id"

LOGGER = logging.getLogger(__package__)
UPDATE_INTERVAL = timedelta(seconds=30)
