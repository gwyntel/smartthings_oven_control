# Contributing to SmartThings Oven Control

Thank you for considering contributing to SmartThings Oven Control! This document provides guidelines and information to help you contribute effectively.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for everyone.

## How to Contribute

### Reporting Issues
- Check existing issues before creating a new one
- Provide detailed information about your environment and steps to reproduce
- Include relevant logs and error messages when applicable

### Feature Requests
- Explain the use case and benefits of your proposed feature
- Consider the impact on existing functionality
- Be specific about the desired behavior

### Pull Requests
1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Add tests if applicable
4. Update documentation as needed
5. Submit your pull request with a clear description

## Development Setup

1. Clone your fork of the repository
2. Create the custom component directory in your Home Assistant config:
   ```bash
   mkdir -p custom_components/smartthings_oven_control
   ```
3. Copy the integration files to your Home Assistant instance for testing

## Code Guidelines

- Follow Home Assistant development standards
- Use type hints where appropriate
- Write clear, descriptive commit messages
- Keep changes focused and atomic

## Testing

- Test your changes in a Home Assistant development environment
- Verify that the integration works with the SmartThings API
- Ensure proper error handling and edge cases

## Getting Help

If you need assistance, please open an issue in the repository.

Thank you for your contributions!
