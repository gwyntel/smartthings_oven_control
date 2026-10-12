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
from .token_utils import async_get_access_token

_LOGGER = logging.getLogger(__name__)

# Define platforms that this integration provides
PLATFORMS = [Platform.SELECT, Platform.NUMBER, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SmartThings Oven Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Verify we can obtain a SmartThings token before setting up entities.
    # The token itself is deliberately not cached here: SmartThings access
    # tokens expire after roughly 24 hours, so it is resolved (and refreshed
    # when needed) at request time instead.
    if not await async_get_access_token(hass):
        raise ConfigEntryNotReady(
            "Unable to obtain a SmartThings access token. Make sure the "
            "SmartThings integration is set up and authenticated."
        )

    # Store the config entry data with default values
    hass.data[DOMAIN][entry.entry_id] = {
        "device_id": entry.data["device_id"],
        "friendly_name": entry.data.get("friendly_name", "Oven"),
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
