"""Number entities for SmartThings Oven Control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MIN_TEMP_F, MAX_TEMP_F, MIN_COOK_TIME, MAX_COOK_TIME
from .oven_entity import SmartThingsOvenEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SmartThings Oven Control number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_id = coordinator["device_id"]
    friendly_name = coordinator["friendly_name"]
    access_token = coordinator["access_token"]
    
    async_add_entities([
        OvenTemperatureNumber(
            device_id=device_id,
            friendly_name=friendly_name,
            access_token=access_token,
            config_entry=entry,
        ),
        OvenCookTimeNumber(
            device_id=device_id,
            friendly_name=friendly_name,
            access_token=access_token,
            config_entry=entry,
        )
    ])


class OvenTemperatureNumber(SmartThingsOvenEntity, NumberEntity):
    """Number entity for oven temperature."""

    def __init__(
        self,
        device_id: str,
        friendly_name: str,
        access_token: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the oven temperature number."""
        super().__init__(
            device_id=device_id,
            friendly_name=friendly_name,
            access_token=access_token,
            config_entry=config_entry,
        )
        
        self._attr_unique_id = f"{device_id}_oven_temperature"
        self._attr_name = "Oven Temperature"
        self._attr_native_min_value = MIN_TEMP_F
        self._attr_native_max_value = MAX_TEMP_F
        self._attr_native_step = 5.0
        self._attr_native_unit_of_measurement = "°F"
        self._attr_native_value = 350.0  # Default temperature

    @property
    def device_class(self) -> str | None:
        """Return the device class."""
        return "temperature"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Get current mode to determine appropriate temperature range
        coordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
        current_mode = coordinator.get("oven_mode", "Bake")
        
        # Get temperature range for current mode
        from .const import TEMPERATURE_RANGES
        if current_mode in TEMPERATURE_RANGES:
            min_temp, max_temp = TEMPERATURE_RANGES[current_mode]
            
            # Handle special cases like Broil which has no temperature setting
            if min_temp == 0 and max_temp == 0:
                _LOGGER.warning("Temperature cannot be set for mode: %s", current_mode)
                return
        else:
            # Default range
            min_temp, max_temp = MIN_TEMP_F, MAX_TEMP_F
        
        if min_temp <= value <= max_temp:
            self._attr_native_value = value
            self.async_write_ha_state()
            
            # Store the value in coordinator data for button access
            coordinator["oven_temperature"] = value
            
            _LOGGER.debug("Oven temperature set to: %s°F for mode %s", value, current_mode)
        else:
            _LOGGER.warning("Invalid oven temperature set: %s°F (range: %s-%s°F for mode %s)", 
                          value, min_temp, max_temp, current_mode)


class OvenCookTimeNumber(SmartThingsOvenEntity, NumberEntity):
    """Number entity for cook time."""

    def __init__(
        self,
        device_id: str,
        friendly_name: str,
        access_token: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the oven cook time number."""
        super().__init__(
            device_id=device_id,
            friendly_name=friendly_name,
            access_token=access_token,
            config_entry=config_entry,
        )
        
        self._attr_unique_id = f"{device_id}_oven_cook_time"
        self._attr_name = "Cook Time"
        self._attr_native_min_value = MIN_COOK_TIME
        self._attr_native_max_value = MAX_COOK_TIME
        self._attr_native_step = 1.0
        self._attr_native_unit_of_measurement = "min"
        self._attr_native_value = 30.0  # Default cook time in minutes

    @property
    def device_class(self) -> str | None:
        """Return the device class."""
        return "duration"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if MIN_COOK_TIME <= value <= MAX_COOK_TIME:
            self._attr_native_value = value
            self.async_write_ha_state()
            
            # Store the value in coordinator data for button access
            coordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
            coordinator["oven_cook_time"] = value
            
            _LOGGER.debug("Cook time set to: %s minutes", value)
        else:
            _LOGGER.warning("Invalid cook time set: %s minutes (range: %s-%s minutes)", 
                          value, MIN_COOK_TIME, MAX_COOK_TIME)
