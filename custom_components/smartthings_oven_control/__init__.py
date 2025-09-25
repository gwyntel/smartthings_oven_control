"""SmartThings Oven Control integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo, async_get as async_get_dev_reg

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define platforms that this integration provides
PLATFORMS = [Platform.SELECT, Platform.NUMBER, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SmartThings Oven Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Validate that SmartThings token is available
    try:
        from .token_utils import get_smartthings_token
        access_token = await get_smartthings_token(hass)
        if not access_token:
            raise ConfigEntryNotReady("SmartThings integration not found or token expired")
    except Exception as e:
        _LOGGER.error("Failed to get SmartThings token: %s", e)
        raise ConfigEntryNotReady("Failed to access SmartThings token") from e
    
    # Store the config entry data with default values
    hass.data[DOMAIN][entry.entry_id] = {
        "device_id": entry.data["device_id"],
        "friendly_name": entry.data.get("friendly_name", "Oven"),
        "access_token": access_token,
        "oven_mode": "Bake",
        "oven_temperature": 350.0,
        "oven_cook_time": 30.0,
    }
    
    # Create device in device registry
    device_registry = async_get_dev_reg(hass)
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.data["device_id"])},
        name=entry.data.get("friendly_name", "Oven"),
        manufacturer="Samsung",
        model="DA-KS-RANGE-0101X",
        suggested_area="Kitchen",
        configuration_url=f"https://account.smartthings.com/devices/{entry.data['device_id']}",
    )
    
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        **device_info
    )
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
