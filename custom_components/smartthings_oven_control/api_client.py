"""API client for SmartThings Oven Control."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import SMARTTHINGS_API_BASE
from .token_utils import async_get_access_token

_LOGGER = logging.getLogger(__name__)


class SmartThingsAuthError(HomeAssistantError):
    """Raised when SmartThings rejects our credentials."""


class SmartThingsApiError(HomeAssistantError):
    """Raised when the SmartThings API returns an unexpected response."""


async def _async_request(
    hass: HomeAssistant,
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    json_payload: Any | None = None,
) -> dict:
    """Perform a SmartThings API request, refreshing the token on a 401.

    SmartThings access tokens are short lived, so a token that was valid when
    the request was built may already have been revoked. On a 401 we force a
    token refresh and retry the request exactly once.
    """
    session = async_get_clientsession(hass)

    for attempt in range(2):
        force_refresh = attempt > 0
        access_token = await async_get_access_token(hass, force_refresh=force_refresh)
        if not access_token:
            raise SmartThingsAuthError(
                "No valid SmartThings access token is available. Check that the "
                "SmartThings integration is set up and reauthenticated."
            )

        request_headers = {**headers, "Authorization": f"Bearer {access_token}"}

        try:
            async with session.request(
                method, url, headers=request_headers, json=json_payload
            ) as response:
                if response.status == 401:
                    body = await response.text()
                    if attempt == 0:
                        _LOGGER.debug(
                            "SmartThings rejected the access token (401); "
                            "refreshing and retrying"
                        )
                        continue
                    _LOGGER.error(
                        "SmartThings authentication failed after refreshing the "
                        "token: %s",
                        body,
                    )
                    raise SmartThingsAuthError(
                        "SmartThings authentication failed after refreshing the "
                        "access token"
                    )

                if response.status != 200:
                    body = await response.text()
                    _LOGGER.error(
                        "SmartThings API error %s: %s", response.status, body
                    )
                    raise SmartThingsApiError(
                        f"SmartThings API error: {response.status}"
                    )

                payload = await response.json()
                # aiohttp returns None for an empty body rather than raising,
                # and this function is annotated -> dict. Normalise so callers
                # never get None where they expect a mapping.
                return payload if payload is not None else {}

        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP client error during SmartThings API call: %s", err)
            raise SmartThingsApiError(
                f"Error communicating with SmartThings: {err}"
            ) from err
        except ValueError as err:
            # response.json() raises json.JSONDecodeError (a ValueError) on an
            # empty or malformed 200 body. That is not a ClientError, so without
            # this it would escape as a raw ValueError instead of our own type.
            _LOGGER.error("Malformed JSON in SmartThings API response: %s", err)
            raise SmartThingsApiError(
                f"Malformed response from SmartThings: {err}"
            ) from err

    # Unreachable: the loop either returns or raises.
    raise SmartThingsAuthError("Unable to authenticate with SmartThings")


async def execute_oven_command(
    hass: HomeAssistant,
    device_id: str,
    capability: str,
    command: str,
    arguments: list | None = None,
) -> dict:
    """Execute a SmartThings device command."""
    payload: dict[str, Any] = {
        "component": "main",
        "capability": capability,
        "command": command,
    }
    if arguments is not None:
        payload["arguments"] = arguments

    result = await _async_request(
        hass,
        "POST",
        f"{SMARTTHINGS_API_BASE}/devices/{device_id}/commands",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json_payload=[payload],
    )
    _LOGGER.debug("API command executed successfully: %s", result)
    return result


async def get_device_status(hass: HomeAssistant, device_id: str) -> dict:
    """Get the current device status."""
    result = await _async_request(
        hass,
        "GET",
        f"{SMARTTHINGS_API_BASE}/devices/{device_id}/status",
        headers={"Accept": "application/json"},
    )
    _LOGGER.debug("Device status retrieved: %s", result)
    return result
