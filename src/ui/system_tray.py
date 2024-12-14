from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from src.ui.icons import create_status_icon

class SystemTray(QSystemTrayIcon):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.setup_ui()
        
    def setup_ui(self):
        self.connected_icon = create_status_icon("connected")
        self.disconnected_icon = create_status_icon("disconnected")
        
        self.setIcon(self.connected_icon)
        self.menu = QMenu()
        self.setup_menu_items()
        self.setContextMenu(self.menu)
        self.show()

    def setup_menu_items(self):
        # Add your menu items here (status, server change, logs, etc.)
        pass

    def update_status(self, result):
        icon = self.connected_icon if result.is_connected else self.disconnected_icon
        self.setIcon(icon)
        self.setToolTip(f"Status: {result.status}\nPing: {result.ping_time}ms")
        
        # Handle notifications
        self.handle_notifications(result)

    def handle_notifications(self, result):
        # Implement notification logic here
        pass


    def show_enhanced_notification(self, title, message, icon, duration=3000):
        QTimer.singleShot(duration, self.hide)
        self.showMessage(title, message, icon, duration)