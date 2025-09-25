# SmartThings Oven Control

A Home Assistant custom integration for controlling Samsung SmartThings ovens (model DA-KS-RANGE-0101X) using REST API calls with tokens from HA's SmartThings integration.

## Features

- **Oven Mode Selection**: Choose from common oven modes (Bake, Broil, ConvectionBake, etc.)
- **Temperature Control**: Set cooking temperature (170-550°F)
- **Cook Time Setting**: Set cooking duration (1-599 minutes, up to 9h 59m)
- **Start Cooking Button**: Execute stored mode/temperature/time settings
- **Time Sync Button**: Sync oven clock with Home Assistant's time
- **Device Registry Integration**: Creates a dedicated oven device in HA
- **User-Friendly Setup**: Simple device ID input via config flow

## Requirements

- Home Assistant with SmartThings integration configured
- Samsung SmartThings oven model DA-KS-RANGE-0101X
- Valid SmartThings access token (automatically retrieved from HA's config)

## Installation

1. Copy the `smartthings_oven_control` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings > Devices & Services > Add Integration
4. Search for "SmartThings Oven Control"
5. Enter your SmartThings device ID from the SmartThings app
6. Optionally provide a friendly name (defaults to "Oven")

## Usage

After setup, you'll have 5 entities available:

- **Select Entity**: Oven mode selection
- **Number Entity**: Temperature control (°F)
- **Number Entity**: Cook time control (minutes)
- **Button Entity**: Start cooking with stored settings
- **Button Entity**: Sync oven time with HA

The entities will be grouped under a single "Oven Control" device in Home Assistant.

## Supported Oven Modes

- Bake
- Broil
- ConvectionBake
- ConvectionRoast
- KeepWarm
- BreadProof
- AirFryer
- Dehydrate
- SelfClean
- SteamClean

## API Integration

This integration uses SmartThings REST API endpoints:
- `POST /devices/{device_id}/commands` for oven control
- Automatically retrieves tokens from HA's SmartThings integration
- No need to manually configure API credentials

## Troubleshooting

- Ensure your SmartThings integration is properly configured in Home Assistant
- Verify the device ID corresponds to your oven in the SmartThings app
- Check that your oven supports the DA-KS-RANGE-0101X model commands
- Review Home Assistant logs for any error messages

## License

MIT License
