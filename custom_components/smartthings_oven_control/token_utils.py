"""Utilities for obtaining a valid SmartThings access token.

The SmartThings OAuth access token issued to the official ``smartthings``
integration is short lived (roughly 24 hours). Rather than caching a token
string, callers should resolve one through :func:`async_get_access_token`
immediately before each API request so an expired token is transparently
refreshed via Home Assistant's OAuth2 session helpers.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .const import SMARTTHINGS_DOMAIN

_LOGGER = logging.getLogger(__name__)


def _async_get_smartthings_entry(hass: HomeAssistant) -> ConfigEntry | None:
    """Return the loaded SmartThings config entry, if there is one."""
    entries = hass.config_entries.async_entries(SMARTTHINGS_DOMAIN)
    for entry in entries:
        if entry.state is ConfigEntryState.LOADED:
            return entry
    # Fall back to any entry - it may still hold a refreshable token.
    return entries[0] if entries else None


async def _async_get_oauth_session(
    hass: HomeAssistant, entry: ConfigEntry
) -> config_entry_oauth2_flow.OAuth2Session | None:
    """Build an OAuth2 session for the SmartThings config entry."""
    try:
        implementation = (
            await config_entry_oauth2_flow.async_get_config_entry_implementation(
                hass, entry
            )
        )
    except (ValueError, KeyError) as err:
        # ValueError: the implementation is not registered. On newer cores this
        # arrives as UnknownImplementationError, which subclasses ValueError
        # precisely "so callers catching that keep working" - so this stays
        # correct without naming the newer class.
        # KeyError: the entry predates application credentials and carries no
        # "auth_implementation" key.
        #
        # Deliberately NOT caught: ImplementationUnavailableError (the OAuth
        # provider is down). It subclasses ConfigEntryNotReady so Home
        # Assistant retries setup on its own; swallowing it here would hide a
        # transient outage behind the stale storage fallback.
        _LOGGER.debug("No OAuth2 implementation for SmartThings entry: %s", err)
        return None

    return config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)


async def async_get_access_token(
    hass: HomeAssistant, *, force_refresh: bool = False
) -> str | None:
    """Return a currently valid SmartThings access token.

    Refreshes the token through the official SmartThings config entry when it
    has expired. Pass ``force_refresh`` to refresh even when the stored token
    still looks valid - used after the API rejects a token with HTTP 401.
    """
    entry = _async_get_smartthings_entry(hass)
    if entry is None:
        _LOGGER.error(
            "The SmartThings integration is not set up; cannot obtain a token"
        )
        return None

    session = await _async_get_oauth_session(hass, entry)
    if session is None:
        return await _async_get_token_from_storage(hass)

    try:
        if force_refresh:
            _LOGGER.debug("Forcing a SmartThings token refresh")
            new_token = await session.implementation.async_refresh_token(session.token)
            hass.config_entries.async_update_entry(
                entry, data={**entry.data, "token": new_token}
            )
        else:
            # Only performs a network call when the token has actually expired.
            await session.async_ensure_token_valid()
    except Exception as err:  # noqa: BLE001 - surfaced to the caller as None
        _LOGGER.error("Failed to refresh the SmartThings access token: %s", err)
        return None

    access_token = session.token.get("access_token")
    if not access_token:
        _LOGGER.error("SmartThings config entry does not contain an access token")
        return None

    return access_token


async def _async_get_token_from_storage(hass: HomeAssistant) -> str | None:
    """Read the access token straight from the config entry store.

    Legacy fallback for installations where the OAuth2 implementation cannot be
    resolved. The token cannot be refreshed on this path.
    """
    data = await _async_read_config_entries(hass)
    if data is None:
        return None

    for entry in data.get("data", {}).get("entries", []):
        if entry.get("domain") != SMARTTHINGS_DOMAIN:
            continue

        token_data = entry.get("data", {}).get("token", {})
        access_token = token_data.get("access_token")
        expires_at = token_data.get("expires_at")

        if not access_token:
            continue
        if expires_at and expires_at <= time.time():
            _LOGGER.warning(
                "Stored SmartThings token for one entry has expired and cannot "
                "be refreshed without an OAuth2 implementation; checking any "
                "remaining entries"
            )
            continue
        return access_token

    _LOGGER.error("No SmartThings config entry found in storage")
    return None


async def _async_read_config_entries(hass: HomeAssistant) -> dict | None:
    """Load the raw config entry store off the event loop."""
    config_entries_file = (
        Path(hass.config.config_dir) / ".storage" / "core.config_entries"
    )
    return await hass.async_add_executor_job(_read_config_file, config_entries_file)


def _read_config_file(config_entries_file: Path) -> dict | None:
    """Read the config entry store from disk."""
    try:
        with open(config_entries_file, encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as err:
        _LOGGER.error("Error reading %s: %s", config_entries_file, err)
        return None


async def async_get_location_id(hass: HomeAssistant) -> str | None:
    """Return the SmartThings location ID, if one is configured."""
    entry = _async_get_smartthings_entry(hass)
    if entry is not None and (location_id := entry.data.get("location_id")):
        return location_id

    data = await _async_read_config_entries(hass)
    if data is None:
        return None

    for stored in data.get("data", {}).get("entries", []):
        if stored.get("domain") == SMARTTHINGS_DOMAIN:
            if location_id := stored.get("data", {}).get("location_id"):
                return location_id

    _LOGGER.warning("No SmartThings location_id found")
    return None
