from PyQt6.QtCore import QTimer
from src.core.network import NetworkChecker
from src.ui.main_window import MainWindow
from src.ui.system_tray import SystemTray
from src.utils.config import Config
from src.utils.logger import Logger

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
        
        # Initialize UI components
        self.system_tray = SystemTray(self)
        self.main_window = MainWindow(self, self.config.settings)
        
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
