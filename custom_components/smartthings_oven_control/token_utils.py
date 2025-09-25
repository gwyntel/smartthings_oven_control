"""Utilities for accessing SmartThings tokens from Home Assistant's stored config entries."""
from __future__ import annotations

import json
import time
import logging
from pathlib import Path

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def get_smartthings_token(hass: HomeAssistant) -> str | None:
    """Get SmartThings access token from stored config entries."""
    config_entries_file = Path(hass.config.config_dir) / ".storage" / "core.config_entries"
    
    if not config_entries_file.exists():
        _LOGGER.error("Config entries file does not exist: %s", config_entries_file)
        return None
        
    try:
        with open(config_entries_file, 'r') as f:
            data = json.load(f)
        
        # Find SmartThings config entry
        for entry in data.get('data', {}).get('entries', []):
            if entry.get('domain') == 'smartthings':
                token_data = entry.get('data', {}).get('token', {})
                access_token = token_data.get('access_token')
                
                # Check if token is still valid (not expired)
                expires_at = token_data.get('expires_at')
                if expires_at and expires_at > time.time():
                    _LOGGER.debug("Found valid SmartThings token")
                    return access_token
                else:
                    _LOGGER.warning("SmartThings token is expired or missing expiration time")
                    
        _LOGGER.error("No valid SmartThings integration found")
        return None
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        _LOGGER.error("Error reading SmartThings token: %s", e)
        return None


async def get_smartthings_location_id(hass: HomeAssistant) -> str | None:
    """Get SmartThings location ID from stored config entries."""
    config_entries_file = Path(hass.config.config_dir) / ".storage" / "core.config_entries"
    
    if not config_entries_file.exists():
        _LOGGER.error("Config entries file does not exist: %s", config_entries_file)
        return None
        
    try:
        with open(config_entries_file, 'r') as f:
            data = json.load(f)
        
        # Find SmartThings config entry
        for entry in data.get('data', {}).get('entries', []):
            if entry.get('domain') == 'smartthings':
                location_id = entry.get('data', {}).get('location_id')
                if location_id:
                    return location_id
                else:
                    _LOGGER.warning("No location_id found in SmartThings config entry")
                    return None
                
        _LOGGER.error("No SmartThings integration found")
        return None
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        _LOGGER.error("Error reading SmartThings location: %s", e)
        return None
