

"""Constants for the Pysunsa integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final


DOMAIN: Final = "sunsa"
LOGGER = logging.getLogger(__package__)

IDDEVICE: Final = "idDevice"
VALUE: Final = "value"
UNIT: Final = "unit"
TEXT: Final = "text"
DEFAULT_SMART_HOME_DIRECTION: Final = "defaultSmartHomeDirection"
USER_ID: Final = "user_id"
SERVICE_SET_ABSOLUTE_POSITION: Final = "set_absolute_position"
ATTR_POSITION: Final = "position"
ATTR_CURRENT_ABSOLUTE_POSITION: Final = "current_absolute_position"
BLIND_TYPE: Final = "blindType"
IS_CONNECTED: Final = "isConnected"

UPDATE_INTERVAL = timedelta(seconds=15)
