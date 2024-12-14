from PyQt6.QtCore import QTimer
from src.core.network import NetworkChecker
from src.ui.main_window import MainWindow
from src.ui.system_tray import SystemTray
from src.utils.config import Config
from src.utils.logger import Logger
from PyQt6.QtWidgets import QSystemTrayIcon

class NetworkMonitor:
    VERSION = "1.0.0"
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.network_checker = NetworkChecker()
        self.stats = {
            "total_checks": 0,
            "failures": 0,
            "current_streak": 0
        }
        self.is_monitoring = True
        self.last_status = "Unknown"
        
        # Initialize UI components - create main window first
        self.main_window = MainWindow(self, self.config.settings)
        self.system_tray = SystemTray(self)
        
        self.initialize()

    def initialize(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(self.config.settings['check_interval'])

    def check_connection(self):
        if not self.is_monitoring:
            return
            
        result = self.network_checker.check(self.config.settings['server'])
        self.update_stats(result)
        self.system_tray.update_status(result)
        self.main_window.update_status(result)
        self.logger.log_result(result)
        
        # Handle connection state changes
        if self.last_status != result.status:
            if not result.is_connected and self.config.settings['notifications']['notify_on_disconnect']:
                self.system_tray.showMessage(
                    "Network Monitor",
                    f"Connection Lost to {result.server}",
                    QSystemTrayIcon.MessageIcon.Critical,
                    3000
                )
            elif result.is_connected and self.last_status != "Unknown" and self.config.settings['notifications']['notify_on_reconnect']:
                self.system_tray.showMessage(
                    "Network Monitor",
                    f"Connection Restored (Ping: {result.ping_time}ms)",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
            elif result.is_connected and self.config.settings['notifications']['notify_on_poor_connection']:
                threshold = self.config.settings['notifications']['poor_connection_threshold']
                if result.ping_time > threshold:
                    self.system_tray.showMessage(
                        "Network Monitor",
                        f"Poor Connection Detected (Ping: {result.ping_time}ms)",
                        QSystemTrayIcon.MessageIcon.Warning,
                        3000
                    )
        
        self.last_status = result.status

    def update_stats(self, result):
        self.stats["total_checks"] += 1
        if not result.is_connected:
            self.stats["failures"] += 1
            self.stats["current_streak"] = 0
        else:
            self.stats["current_streak"] += 1

    def toggle_monitoring(self):
        """Pause/Resume monitoring"""
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.timer.start(self.config.settings['check_interval'])
        else:
            self.timer.stop()

    def save_settings(self, new_settings):
        """Save new settings and update the configuration"""
        self.config.settings = new_settings
        self.config.save_settings()
        
        # Update the check interval if it has changed
        if self.timer.interval() != new_settings['check_interval']:
            self.timer.setInterval(new_settings['check_interval'])
