"""Select entity for SmartThings Oven Control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, OVEN_MODES
from .oven_entity import SmartThingsOvenEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up the SmartThings Oven Control select platform."""
    # This is called by the platform setup
    pass


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SmartThings Oven Control select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_id = coordinator["device_id"]
    friendly_name = coordinator["friendly_name"]
    access_token = coordinator["access_token"]
    
    async_add_entities([
        OvenModeSelect(
            device_id=device_id,
            friendly_name=friendly_name,
            access_token=access_token,
            config_entry=entry,
        )
    ])


class OvenModeSelect(SmartThingsOvenEntity, SelectEntity):
    """Select entity for oven mode."""

    def __init__(
        self,
        device_id: str,
        friendly_name: str,
        access_token: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the oven mode select."""
        super().__init__(
            device_id=device_id,
            friendly_name=friendly_name,
            access_token=access_token,
            config_entry=config_entry,
        )
        
        self._attr_unique_id = f"{device_id}_oven_mode"
        self._attr_name = "Oven Mode"
        self._attr_options = OVEN_MODES
        self._attr_current_option = "Bake"  # Default to Bake mode

    @property
    def device_class(self) -> str | None:
        """Return the device class."""
        return "oven_mode"

    async def async_select_option(self, option: str) -> None:
        """Update the current option."""
        if option in OVEN_MODES:
            self._attr_current_option = option
            self.async_write_ha_state()
            
            # Store the value in coordinator data for button access
            coordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
            coordinator["oven_mode"] = option
            
            _LOGGER.debug("Oven mode set to: %s", option)
        else:
            _LOGGER.warning("Invalid oven mode selected: %s", option)
