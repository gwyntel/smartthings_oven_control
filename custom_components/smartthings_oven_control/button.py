"""Button entities for SmartThings Oven Control."""
from __future__ import annotations

import logging
from typing import Any
from datetime import datetime

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .oven_entity import SmartThingsOvenEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SmartThings Oven Control button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_id = coordinator["device_id"]
    friendly_name = coordinator["friendly_name"]
    access_token = coordinator["access_token"]
    
    # Store entity references in hass.data for later access
    entity_storage = hass.data[DOMAIN].setdefault("entities", {})
    
    start_button = OvenStartButton(
        device_id=device_id,
        friendly_name=friendly_name,
        access_token=access_token,
        config_entry=entry,
    )
    
    sync_button = OvenSyncTimeButton(
        device_id=device_id,
        friendly_name=friendly_name,
        access_token=access_token,
        config_entry=entry,
    )
    
    # Store the button entities for reference
    entity_storage[f"{device_id}_oven_start"] = start_button
    entity_storage[f"{device_id}_oven_sync_time"] = sync_button
    
    async_add_entities([start_button, sync_button])


class OvenStartButton(SmartThingsOvenEntity, ButtonEntity):
    """Button entity for starting oven cooking."""

    def __init__(
        self,
        device_id: str,
        friendly_name: str,
        access_token: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the oven start button."""
        super().__init__(
            device_id=device_id,
            friendly_name=friendly_name,
            access_token=access_token,
            config_entry=config_entry,
        )
        
        self._attr_unique_id = f"{device_id}_oven_start"
        self._attr_name = "Start Cooking"

    async def async_press(self) -> None:
        """Start oven with stored settings."""
        try:
            # Get current values from the coordinator data
            coordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
            
            # Get the stored values from coordinator
            mode = coordinator.get("oven_mode", "Bake")
            temperature = coordinator.get("oven_temperature", 350.0)
            cook_time = coordinator.get("oven_cook_time", 30.0)
            
            # Convert cook time from minutes to seconds for API
            # Ensure all values are integers as required by API
            api_cook_time = int(cook_time * 60)  # Convert minutes to seconds
            api_temperature = int(temperature)
            
            # Execute REST command to start oven
            from .api_client import execute_oven_command
            await execute_oven_command(
                self.hass,
                self._device_id,
                self._access_token, 
                "ovenOperatingState",
                "start",
                [mode, api_cook_time, api_temperature]
            )
            
            _LOGGER.info("Oven started with mode: %s, temp: %s°F, time: %s min", 
                        mode, temperature, cook_time)
        except Exception as e:
            _LOGGER.error("Failed to start oven: %s", e)
            raise


class OvenSyncTimeButton(SmartThingsOvenEntity, ButtonEntity):
    """Button entity for syncing oven time."""

    def __init__(
        self,
        device_id: str,
        friendly_name: str,
        access_token: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the oven sync time button."""
        super().__init__(
            device_id=device_id,
            friendly_name=friendly_name,
            access_token=access_token,
            config_entry=config_entry,
        )
        
        self._attr_unique_id = f"{device_id}_oven_sync_time"
        self._attr_name = "Sync Time"

    async def async_press(self) -> None:
        """Sync oven time with HA time."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            
            # Execute REST command to sync time
            from .api_client import execute_oven_command
            await execute_oven_command(
                self.hass,
                self._device_id,
                self._access_token,
                "execute", 
                "execute",
                ["/configuration/vs/0", {"x.com.samsung.da.currentTime": current_time}]
            )
            
            _LOGGER.info("Oven time synced to: %s", current_time)
        except Exception as e:
            _LOGGER.error("Failed to sync oven time: %s", e)
            raise
