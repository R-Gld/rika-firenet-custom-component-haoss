# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for switch and number domains in HACS configuration
- Enhanced HACS integration metadata

### Changed
- Improved code formatting with Black formatter
- Enhanced logging and variable naming for better clarity
- Improved temperature and value validation

### Fixed
- Enhanced error handling for Rika Firenet integration
- Better connection error management
- Improved validation for climate and number entities

## [2.0.0] - 2025-02

### Added
- Custom exceptions for better error handling
  - `RikaAuthenticationError`
  - `RikaApiError`
  - `RikaConnectionError`
  - `RikaTimeoutError`
  - `RikaValidationError`
- HTTP configuration and API URLs constants
- Number entity platform support
- Multi Air support

### Changed
- Updated code for HASS 2025.2 compatibility
- Removed errors and warnings
- Adopted new number entity pattern following Home Assistant guidelines
- Made test credentials setup method async
- Improved state updates after switch actions

### Fixed
- State retrieval with nocache epoch value as query parameter
- DataUpdateCoordinator configuration for config flow
- Version key in manifest.json

## [1.0.0] - Initial Release

### Added
- Initial integration with Rika Firenet cloud API
- Climate platform for temperature control
- Sensor platform for monitoring stove status
  - Consumption (kg)
  - Runtime (hours)
  - Temperatures (stove and room)
  - Stove status and state
  - Heating power
  - Room power request
- Switch platform for stove and convection fan control
- Configuration flow via Home Assistant UI
- Multi-language support (English, French, German, Dutch)
- Support for:
  - Target temperature control (16-30°C)
  - HVAC modes (OFF, HEAT, AUTO)
  - Preset modes (HOME, AWAY)
  - Convection fan control (2 fans)
  - Heating power adjustment
  - Room power request levels

### Technical
- DataUpdateCoordinator pattern for API management
- Session-based authentication with Rika Firenet
- 15-second update interval (configurable minimum: 10 seconds)
- Automatic reconnection on session loss
- HTTP timeout and retry configuration
