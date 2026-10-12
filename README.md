# SmartThings Oven Control

[![HACS Default](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/gwyntel/smartthings_oven_control)](https://github.com/gwyntel/smartthings_oven_control/releases)
[![License: MIT](https://img.shields.io/github/license/gwyntel/smartthings_oven_control)](https://github.com/gwyntel/smartthings_oven_control/blob/main/LICENSE)

A Home Assistant custom integration for controlling Samsung SmartThings ovens (model DA-KS-RANGE-0101X) using REST API calls with tokens from HA's SmartThings integration.

## 🚀 Features

- **Oven Mode Selection**: Choose from common oven modes (Bake, Broil, ConvectionBake, etc.)
- **Temperature Control**: Set cooking temperature with mode-specific ranges (175-550°F depending on mode)
- **Cook Time Setting**: Set cooking duration up to 9 hours 59 minutes (599 minutes)
- **Start Cooking Button**: Execute stored mode/temperature/time settings
- **Time Sync Button**: Sync oven clock with Home Assistant's time
- **Device Registry Integration**: Creates a dedicated oven device in HA
- **User-Friendly Setup**: Simple device ID input via config flow

## 📋 Requirements

- Home Assistant 2023.1.0 or later
- SmartThings integration configured in Home Assistant
- Samsung SmartThings oven model DA-KS-RANGE-0101X (or compatible model)
- Valid SmartThings access token (automatically retrieved from HA's config)

## 🛠️ Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/gwyntel/smartthings_oven_control` with category "Integration"
5. Search for "SmartThings Oven Control" and install
6. Restart Home Assistant
7. Go to Settings > Devices & Services > Add Integration
8. Search for "SmartThings Oven Control"
9. Enter your SmartThings device ID from the SmartThings app
10. Optionally provide a friendly name (defaults to "Oven")

### Manual Installation

1. Copy the `smartthings_oven_control` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings > Devices & Services > Add Integration
4. Search for "SmartThings Oven Control"
5. Enter your SmartThings device ID from the SmartThings app
6. Optionally provide a friendly name (defaults to "Oven")

## 📖 Usage

After setup, you'll have 5 entities available:

- **Select Entity**: Oven mode selection
- **Number Entity**: Temperature control (°F) - range varies by selected mode
- **Number Entity**: Cook time control (minutes) - up to 599 minutes
- **Button Entity**: Start cooking with stored settings
- **Button Entity**: Sync oven time with HA

The entities will be grouped under a single "Oven Control" device in Home Assistant.

## 🔧 Supported Oven Modes and Temperature Ranges

- **Bake**: 175-550°F
- **Broil**: High/Low only (no temperature setting)
- **ConvectionBake**: 175-550°F
- **ConvectionRoast**: 175-550°F
- **KeepWarm**: 95-550°F
- **BreadProof**: 95-550°F
- **AirFryer**: 350-500°F
- **Dehydrate**: 100-225°F
- **SelfClean**: No temperature setting
- **SteamClean**: No temperature setting

## 🌐 API Integration

This integration uses SmartThings REST API endpoints:
- `POST /devices/{device_id}/commands` for oven control
- Automatically retrieves tokens from HA's SmartThings integration
- Refreshes the SmartThings access token automatically when it expires
- No need to manually configure API credentials

## ⚙️ Configuration

The integration requires only your SmartThings device ID, which can be found in the SmartThings mobile app under your oven's device settings.

## 🔧 Troubleshooting

- **"Invalid handler specified" error**: Ensure you're using the correct version of Home Assistant (2023.1.0+)
- **Device not found**: Verify the device ID is correct in the SmartThings app
- **Temperature validation errors**: Temperature ranges are enforced based on the selected oven mode
- **API errors**: Check that your SmartThings integration is properly configured and tokens are valid
- **401 / "token may be expired"**: The token is now refreshed automatically and the request retried once. Persistent 401s mean the SmartThings integration itself needs reauthenticating (Settings > Devices & Services > SmartThings)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

## 🛡️ Security

Please read our [Security Policy](SECURITY.md) for information about reporting vulnerabilities.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to the Home Assistant community for their excellent documentation and examples
- Special thanks to the SmartThings API for providing the integration points
