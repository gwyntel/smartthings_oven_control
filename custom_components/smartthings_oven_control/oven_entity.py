"""Base entity class for SmartThings Oven Control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity, DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmartThingsOvenEntity(Entity):
    """Base entity class for SmartThings Oven Control."""

    def __init__(
        self,
        device_id: str,
        friendly_name: str,
        access_token: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the base oven entity."""
        self._device_id = device_id
        self._friendly_name = friendly_name
        self._access_token = access_token
        self._config_entry = config_entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
        )

    @property
    def should_poll(self) -> bool:
        """Disable polling for this entity."""
        return False
