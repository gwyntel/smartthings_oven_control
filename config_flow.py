"""Config flow for SmartThings Oven Control integration."""
from __future__ import annotations

import logging
import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_DEVICE_ID, CONF_FRIENDLY_NAME
from .token_utils import get_smartthings_token

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): str,
        vol.Optional(CONF_FRIENDLY_NAME, default="Oven"): str,
    }
)


async def validate_device_id(hass: HomeAssistant, device_id: str) -> str | None:
    """Validate device ID by testing API connectivity."""
    access_token = await get_smartthings_token(hass)
    if not access_token:
        raise ValueError("SmartThings integration not found or token expired")
    
    # Test device connectivity with a simple status request
    import aiohttp
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    
    url = f"https://api.smartthings.com/v1/devices/{device_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    session = async_get_clientsession(hass)
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 404:
                raise ValueError("Device ID not found")
            elif response.status != 200:
                raise ValueError(f"SmartThings API error: {response.status}")
            
            device_data = await response.json()
            
            # No longer checking for specific oven model - allow any device
            device_type = device_data.get('deviceTypeName', '')
            _LOGGER.debug("Device type: %s", device_type)
                
            return device_data.get('label', 'Oven')  # Return device name for friendly naming
    except aiohttp.ClientError as e:
        _LOGGER.error("HTTP error during device validation: %s", e)
        raise ValueError(f"HTTP error during validation: {e}")
    except Exception as e:
        _LOGGER.error("Error during device validation: %s", e)
        raise ValueError(f"Error during validation: {e}")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartThings Oven Control."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.data_schema = STEP_USER_DATA_SCHEMA

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                # Validate device ID
                device_name = await validate_device_id(self.hass, user_input[CONF_DEVICE_ID])
                
                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                
                # Create config entry
                return self.async_create_entry(
                    title=user_input.get(CONF_FRIENDLY_NAME, device_name),
                    data=user_input,
                )
            except ValueError as e:
                error_msg = str(e)
                if "Device ID not found" in error_msg:
                    errors["base"] = "device_not_found"
                else:
                    errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
