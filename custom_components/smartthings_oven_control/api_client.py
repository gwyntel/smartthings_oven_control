"""API client for SmartThings Oven Control."""
from __future__ import annotations

import logging
import json
from datetime import datetime

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import SMARTTHINGS_API_BASE

_LOGGER = logging.getLogger(__name__)


async def execute_oven_command(
    hass: HomeAssistant,
    device_id: str,
    access_token: str,
    capability: str,
    command: str,
    arguments: list | None = None
) -> dict:
    """Execute SmartThings REST API command."""
    url = f"{SMARTTHINGS_API_BASE}/devices/{device_id}/commands"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    payload = [{
        "component": "main",
        "capability": capability,
        "command": command
    }]
    
    if arguments is not None:
        payload[0]["arguments"] = arguments
    
    session = async_get_clientsession(hass)
    
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 401:
                _LOGGER.error("SmartThings API authentication error (401) - token may be expired")
                _LOGGER.error(f"Response: {await response.text()}")
                raise Exception("SmartThings API authentication failed - token may be expired")
            elif response.status != 200:
                _LOGGER.error(f"SmartThings API error: {response.status}")
                _LOGGER.error(f"Response: {await response.text()}")
                raise Exception(f"SmartThings API error: {response.status}")
            
            result = await response.json()
            _LOGGER.debug("API command executed successfully: %s", result)
            return result
            
    except aiohttp.ClientError as e:
        _LOGGER.error("HTTP client error during API call: %s", e)
        raise
    except Exception as e:
        _LOGGER.error("Unexpected error during API call: %s", e)
        raise


async def get_device_status(
    hass: HomeAssistant,
    device_id: str,
    access_token: str
) -> dict:
    """Get current device status."""
    url = f"{SMARTTHINGS_API_BASE}/devices/{device_id}/status"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    session = async_get_clientsession(hass)
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                _LOGGER.error(f"SmartThings API error getting status: {response.status}")
                raise Exception(f"SmartThings API error: {response.status}")
            
            result = await response.json()
            _LOGGER.debug("Device status retrieved: %s", result)
            return result
            
    except aiohttp.ClientError as e:
        _LOGGER.error("HTTP client error getting device status: %s", e)
        raise
    except Exception as e:
        _LOGGER.error("Unexpected error getting device status: %s", e)
        raise
