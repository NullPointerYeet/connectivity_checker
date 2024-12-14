# Network Monitor

A desktop application for monitoring network connectivity with real-time status updates and notifications.

## Features

- Real-time network connectivity monitoring
- System tray integration with status indicators
- Customizable notification settings
- Connection quality monitoring
- Connection logging
- OS Native Notifications
- Configurable monitoring settings

## Requirements

- Python 3.8+
- PyQt6
- ping3

## Installation

1. Clone the repository:
   ```
   cd network-monitor
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python src/main.py
```

The application will start with a splash screen and minimize to the system tray. You can:

- Click the tray icon to open the main window
- Right-click the tray icon for additional options
- Monitor connection status in real-time
- Configure notification settings
- View connection logs

## Configuration

The application settings are stored in `settings.json` and include:

- Server to ping (default: 8.8.8.8)
- Check interval
- Notification preferences
- Log rotation settings

## Features in Detail

### Network Monitoring
- Continuous connection monitoring
- Ping time measurements
- Connection status tracking

### Notifications
- Disconnect alerts
- Reconnection notifications
- Poor connection warnings
- Customizable thresholds

### System Tray Integration
- Status indicator icons
- Quick access menu
- Minimized operation

### Logging
- CSV format logging
- Timestamp recording
- Connection statistics
- Log rotation support

## Project Structure

```
src/
├── core/
│   ├── monitor.py      # Main monitoring logic
│   └── network.py      # Network checking functionality
├── ui/
│   ├── main_window.py  # Main application window
│   ├── system_tray.py  # System tray integration
│   └── splash_screen.py # Application splash screen
├── utils/
│   ├── config.py       # Configuration management
│   └── logger.py       # Logging functionality
└── main.py             # Application entry point
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt6 for the GUI framework
- ping3 for network connectivity checking
