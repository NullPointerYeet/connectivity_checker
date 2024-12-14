from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget, 
                            QInputDialog, QMessageBox, QDialog, QVBoxLayout, 
                            QLabel, QComboBox, QPushButton, QHBoxLayout, 
                            QCheckBox, QSpinBox, QDialogButtonBox)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QDesktopServices
from PyQt6.QtCore import QTimer, Qt, QUrl
import sys
import ping3
import datetime
import csv
import os
import json
from icon import create_app_icon
from config_dialog import NotificationSettingsDialog, SplashScreen, MainWindow

class PresetServersDialog(QDialog):
    def __init__(self, current_server, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Server")
        self.setModal(True)
        layout = QVBoxLayout()

        # Predefined servers with descriptions
        self.servers = {
            "Google DNS (8.8.8.8)": "8.8.8.8",
            "Cloudflare DNS (1.1.1.1)": "1.1.1.1",
            "OpenDNS (208.67.222.222)": "208.67.222.222",
            "Quad9 DNS (9.9.9.9)": "9.9.9.9",
            "Custom...": "custom"
        }

        self.combo = QComboBox()
        for server in self.servers.keys():
            self.combo.addItem(server)
        
        # Set current selection
        for i, (name, ip) in enumerate(self.servers.items()):
            if ip == current_server:
                self.combo.setCurrentIndex(i)
                break

        layout.addWidget(QLabel("Select a server to monitor:"))
        layout.addWidget(self.combo)
        
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)
        
        self.setLayout(layout)

class NetworkMonitor(QWidget):
    VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__()
        
        # Show splash screen
        self.splash = SplashScreen(self.VERSION)
        self.splash.show()
        
        # Delay the initialization
        QTimer.singleShot(100, self.delayed_init)

    def delayed_init(self):
        # Initialize everything else
        self.target_server = "8.8.8.8"
        self.log_file = "network_log.csv"
        self.check_interval = 1000  # 1 second
        self.stats = {
            "total_checks": 0,
            "failures": 0,
            "current_streak": 0
        }
        self.ping_timeout = 1.0  # Add timeout setting
        self.is_monitoring = True  # Add monitoring state
        self.last_status = "Unknown"
        self.notification_settings = {
            "notify_on_disconnect": True,
            "notify_on_reconnect": True,
            "notify_on_poor_connection": True,
            "poor_connection_threshold": 200  # ms
        }
        
        # Initialize notification settings with defaults
        self.notification_settings = {
            "notify_on_disconnect": True,
            "notify_on_reconnect": True,
            "notify_on_poor_connection": True,
            "poor_connection_threshold": 200  # ms
        }
        
        # Add log rotation settings
        self.notification_settings.update({
            "log_rotation": {
                "enabled": False,
                "max_size_mb": 10,
                "backup_count": 3
            }
        })
        
        # Load settings if they exist
        self.load_settings()
        
        # Create icons
        self.connected_icon = self.create_circle_icon("#2ecc71")
        self.disconnected_icon = self.create_circle_icon("#e74c3c")
        
        self.setWindowIcon(QIcon(create_app_icon()))
        
        # Create and show main window
        self.main_window = MainWindow(self.notification_settings)
        self.main_window.show()
        
        self.init_ui()
        self.init_logging()
        self.start_monitoring()

    def create_circle_icon(self, color):
        pixmap = QPixmap(22, 22)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(1, 1, 20, 20)
        painter.end()
        
        return QIcon(pixmap)

    def init_ui(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.connected_icon)
        
        # Connect double-click to settings
        self.tray.activated.connect(self.tray_activated)
        
        menu = QMenu()
        
        # Status submenu
        status_menu = menu.addMenu("Status")
        self.status_text = status_menu.addAction("Connected")
        self.status_text.setEnabled(False)
        status_menu.addSeparator()
        self.stats_text = status_menu.addAction("Checks: 0 | Failures: 0")
        self.stats_text.setEnabled(False)

        menu.addSeparator()
        
        # Server options
        change_server = menu.addAction("Change Server")
        change_server.triggered.connect(self.change_target_server)
        
        # Logs and settings
        menu.addSeparator()
        view_logs = menu.addAction("Open Logs")
        view_logs.triggered.connect(self.open_logs)
        clear_logs = menu.addAction("Clear Logs")
        clear_logs.triggered.connect(self.clear_logs)
        
        # Help menu
        menu.addSeparator()
        help_menu = menu.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
        help_action = help_menu.addAction("Online Help")
        help_action.triggered.connect(self.open_online_help)
        
        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.cleanup_and_exit)
        
        settings_menu = menu.addMenu("Settings")
        notification_settings = settings_menu.addAction("Notification Settings")
        notification_settings.triggered.connect(self.show_notification_settings)
        
        self.tray.setContextMenu(menu)
        self.tray.show()

    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.target_server = settings.get('server', self.target_server)
                    self.stats = settings.get('stats', self.stats)
                    self.notification_settings = settings.get('notifications', 
                                                            self.notification_settings)
        except:
            pass

    def save_settings(self):
        settings = {
            'server': self.target_server,
            'stats': self.stats,
            'notifications': self.notification_settings
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def change_target_server(self):
        dialog = PresetServersDialog(self.target_server, self)
        if dialog.exec():
            selected = dialog.servers[dialog.combo.currentText()]
            if selected == "custom":
                server, ok = QInputDialog.getText(self, 'Custom Server', 
                                                'Enter server IP or hostname:',
                                                text=self.target_server)
                if ok and server:
                    self.target_server = server
            else:
                self.target_server = selected
            self.save_settings()

    def check_connection(self):
        if not self.is_monitoring:
            return
        
        try:
            ping_time = ping3.ping(self.target_server, timeout=self.ping_timeout)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.stats["total_checks"] += 1
            
            # Consider both None response and socket errors as connection losses
            if ping_time is None:
                status = "Connection Lost"
                self.tray.setIcon(self.disconnected_icon)
                self.stats["failures"] += 1
                self.stats["current_streak"] = 0
                ping_time = "N/A"  # Set a value for logging when connection is lost
            else:
                status = "Connected"
                self.tray.setIcon(self.connected_icon)
                self.stats["current_streak"] += 1
                ping_time = round(ping_time * 1000, 2)
            
            # Update status in menu
            self.status_text.setText(f"Status: {status}")
            self.stats_text.setText(
                f"Checks: {self.stats['total_checks']} | "
                f"Failures: {self.stats['failures']} | "
                f"Streak: {self.stats['current_streak']}"
            )
            
            # Add tooltip with current status
            self.tray.setToolTip(f"Status: {status}\nPing: {ping_time}ms")
            
            # Notify on connection loss with enhanced notification
            if status == "Connection Lost" and self.notification_settings["notify_on_disconnect"]:
                self.show_enhanced_notification(
                    title="Network Connection Lost",
                    message=f"Connection to {self.target_server} has been lost.\nTime: {timestamp}",
                    icon=QSystemTrayIcon.MessageIcon.Warning,
                    duration=5000  # 5 seconds
                )
            elif (status == "Connected" and 
                  self.last_status == "Connection Lost" and 
                  self.notification_settings["notify_on_reconnect"]):
                self.show_enhanced_notification(
                    title="Network Connection Restored",
                    message=f"Connection to {self.target_server} is back online.\nPing: {ping_time}ms",
                    icon=QSystemTrayIcon.MessageIcon.Information,
                    duration=3000  # 3 seconds
                )
            
            # Store last status for reconnection detection
            self.last_status = status
            
            with open(self.log_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, self.target_server, ping_time, status])
            
            self.rotate_logs()
            self.save_settings()
            
            # Update main window status
            if hasattr(self, 'main_window'):
                self.main_window.update_connection_status(
                    status,
                    ping_time if isinstance(ping_time, (int, float)) else "N/A"
                )
            
        except Exception as e:
            # Treat any exception as a connection loss
            status = "Connection Lost"
            self.tray.setIcon(self.disconnected_icon)
            self.stats["failures"] += 1
            self.stats["current_streak"] = 0
            
            if self.notification_settings["notify_on_disconnect"]:
                self.show_enhanced_notification(
                    title="Network Error",
                    message=f"Unable to reach {self.target_server}\nError: Network unreachable",
                    icon=QSystemTrayIcon.MessageIcon.Critical,
                    duration=5000
                )
            
            self.last_status = status
            self.log_error(f"Error during connection check: {e}")

    def clear_logs(self):
        reply = QMessageBox.question(
            self, 'Clear Logs',
            'Are you sure you want to clear the logs?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Close any open file handles
            try:
                # Clear the file contents
                with open(self.log_file, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Timestamp", "Server", "Ping (ms)", "Status"])
                QMessageBox.information(self, "Success", "Logs have been cleared.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear logs: {str(e)}")

    def show_about(self):
        about_text = f"""
        Network Monitor v{self.VERSION}
        
        A simple tool to monitor network connectivity
        and track connection drops.
        
        Created by: Matija Mandic
        License: MIT
        
        """
        QMessageBox.about(self, "About Network Monitor", about_text)

    def open_online_help(self):
        # Replace with your actual help documentation URL
        QDesktopServices.openUrl(QUrl("https://github.com/yourusername/network-monitor"))

    def cleanup_and_exit(self):
        """Proper cleanup before exit"""
        self.timer.stop()
        self.save_settings()
        app.quit()

    def init_logging(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Server", "Ping (ms)", "Status"])

    def start_monitoring(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(self.check_interval)

    def open_logs(self):
        os.startfile(self.log_file) if sys.platform == 'win32' else os.system(f'open {self.log_file}')

    def validate_server(self, server):
        """Validate server address"""
        # Add proper IP/hostname validation
        if not server or len(server) > 255:
            return False
        return True

    def rotate_logs(self):
        """Rotate log file if it gets too large"""
        try:
            log_settings = self.notification_settings.get("log_rotation", {
                "enabled": False,
                "max_size_mb": 10,
                "backup_count": 3
            })
            
            if not log_settings["enabled"]:
                return
            
            if not os.path.exists(self.log_file):
                return
            
            current_size = os.path.getsize(self.log_file) / (1024 * 1024)  # Size in MB
            
            if current_size > log_settings["max_size_mb"]:
                # Close any open file handles
                for i in range(log_settings["backup_count"] - 1, 0, -1):
                    src = f"{self.log_file}.{i}"
                    dst = f"{self.log_file}.{i+1}"
                    if os.path.exists(src):
                        if os.path.exists(dst):
                            os.remove(dst)
                        os.rename(src, dst)
                
                # Backup current log file
                if os.path.exists(self.log_file):
                    backup = f"{self.log_file}.1"
                    if os.path.exists(backup):
                        os.remove(backup)
                    os.rename(self.log_file, backup)
                
                # Create new log file with headers
                self.init_logging()
            
        except Exception as e:
            self.log_error(f"Error rotating logs: {e}")

    def log_error(self, message):
        """Central error logging"""
        print(f"Error: {message}")  # Could be expanded to file logging
        
    def toggle_monitoring(self):
        """Pause/Resume monitoring"""
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.timer.start(self.check_interval)
        else:
            self.timer.stop()

    def show_notification_settings(self):
        try:
            dialog = NotificationSettingsDialog(self.notification_settings, self)
            if dialog.exec():
                self.notification_settings = dialog.get_settings()
                self.save_settings()
        except Exception as e:
            print(f"Error showing settings dialog: {str(e)}")
            QMessageBox.critical(self, "Error", 
                               f"Failed to open settings: {str(e)}")

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_notification_settings()

    def show_enhanced_notification(self, title, message, icon, duration=3000):
        """
        Show a customized system tray notification
        
        Args:
            title (str): Notification title
            message (str): Notification message
            icon (QSystemTrayIcon.MessageIcon): Icon to display
            duration (int): How long to show notification in milliseconds
        """
        # Set custom timeout for notification
        QTimer.singleShot(duration, self.tray.hide)
        
        # Show the notification with enhanced formatting
        self.tray.showMessage(
            title,
            message,
            icon,
            duration
        )

    def update_log_rotation_settings(self, enabled, max_size_mb, backup_count):
        """Update log rotation settings"""
        self.notification_settings["log_rotation"] = {
            "enabled": enabled,
            "max_size_mb": max_size_mb,
            "backup_count": backup_count
        }
        self.save_settings()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    monitor = NetworkMonitor()
    sys.exit(app.exec())