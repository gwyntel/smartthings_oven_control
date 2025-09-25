"""Constants for the SmartThings Oven Control integration."""
from __future__ import annotations

DOMAIN = "smartthings_oven_control"

# API Configuration
SMARTTHINGS_API_BASE = "https://api.smartthings.com/v1"
SMARTTHINGS_DEVICE_COMMANDS_URL = "/devices/{device_id}/commands"

# Oven Modes (exact modes from DA-KS-RANGE-0101X device)
OVEN_MODES = [
    "Bake",
    "Broil", 
    "ConvectionBake",
    "ConvectionRoast",
    "KeepWarm",
    "BreadProof",
    "AirFryer",
    "Dehydrate",
    "SelfClean",
    "SteamClean"
]

# Temperature limits (reasonable oven ranges)
MIN_TEMP_F = 170
MAX_TEMP_F = 550
MIN_TEMP_C = 77
MAX_TEMP_C = 288

# Default temperature ranges for different modes
TEMPERATURE_RANGES = {
    "Bake": (175, 550),
    "Broil": (0, 0),  # Special case - high/low only, no temperature setting
    "ConvectionBake": (175, 550),
    "ConvectionRoast": (175, 550),
    "KeepWarm": (95, 550),
    "BreadProof": (95, 550),
    "AirFryer": (350, 500),
    "Dehydrate": (100, 225),
    "SelfClean": (0, 0),  # No temperature setting
    "SteamClean": (0, 0)  # No temperature setting
}

# Time limits 
MIN_COOK_TIME = 1  # minutes
MAX_COOK_TIME = 599  # 9 hours 59 minutes (9*60 + 59 = 599)

# Config flow
CONF_DEVICE_ID = "device_id"
CONF_FRIENDLY_NAME = "friendly_name"
