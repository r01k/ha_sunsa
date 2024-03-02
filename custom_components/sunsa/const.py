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
DEFAULT_SMART_HOME_POISTION: Final = "defaultSmartHomeDirection"
USER_ID: Final = "user_id"

LOGGER = logging.getLogger(__package__)
UPDATE_INTERVAL = timedelta(seconds=10)
