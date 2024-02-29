"""Constants for the Pysunsa integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final


DOMAIN: Final = "sunsa"
IDDEVICE: Final = "idDevice"

LOGGER = logging.getLogger(__package__)
UPDATE_INTERVAL = timedelta(seconds=20)
