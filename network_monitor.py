from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget, 
                            QInputDialog, QMessageBox, QDialog, QVBoxLayout, 
                            QLabel, QComboBox, QPushButton)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QDesktopServices
from PyQt6.QtCore import QTimer, Qt, QUrl
import sys
import ping3
import datetime
import csv
import os
import json
from icon import create_app_icon

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
        self.target_server = "8.8.8.8"
        self.log_file = "network_log.csv"
        self.check_interval = 1000  # 1 second
        self.stats = {
            "total_checks": 0,
            "failures": 0,
            "current_streak": 0
        }
        
        # Load settings if they exist
        self.load_settings()
        
        # Create icons
        self.connected_icon = self.create_circle_icon("#2ecc71")
        self.disconnected_icon = self.create_circle_icon("#e74c3c")
        
        self.setWindowIcon(QIcon(create_app_icon()))
        
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
        
        self.tray.setContextMenu(menu)
        self.tray.show()

    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.target_server = settings.get('server', self.target_server)
                    self.stats = settings.get('stats', self.stats)
        except:
            pass

    def save_settings(self):
        settings = {
            'server': self.target_server,
            'stats': self.stats
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def change_target_server(self):
        dialog = PresetServersDialog(self.target_server, self)
        if dialog.exec_():
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
        try:
            ping_time = ping3.ping(self.target_server)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.stats["total_checks"] += 1
            
            if ping_time is None:
                status = "Connection Lost"
                self.tray.setIcon(self.disconnected_icon)
                self.stats["failures"] += 1
                self.stats["current_streak"] = 0
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
            
            with open(self.log_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, self.target_server, ping_time, status])
            
            self.save_settings()
                
        except Exception as e:
            print(f"Error: {e}")

    def clear_logs(self):
        reply = QMessageBox.question(
            self, 'Clear Logs',
            'Are you sure you want to clear the logs?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.init_logging()

    def show_about(self):
        about_text = f"""
        Network Monitor v{self.VERSION}
        
        A simple tool to monitor network connectivity
        and track connection drops.
        
        Created by: Your Name
        License: MIT
        
        © 2024 All rights reserved
        """
        QMessageBox.about(self, "About Network Monitor", about_text)

    def open_online_help(self):
        # Replace with your actual help documentation URL
        QDesktopServices.openUrl(QUrl("https://github.com/yourusername/network-monitor"))

    def cleanup_and_exit(self):
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    monitor = NetworkMonitor()
    sys.exit(app.exec())