from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from src.ui.icons import create_status_icon

class SystemTray(QSystemTrayIcon):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.setup_ui()
        self.setup_context_menu()
        
        # Enable notifications
        self.setVisible(True)
        if not self.isSystemTrayAvailable():
            print("System tray is not available")
        
        # Make sure notifications are enabled
        if not self.supportsMessages():
            print("System tray notifications are not supported")

    def setup_ui(self):
        self.connected_icon = create_status_icon("connected")
        self.disconnected_icon = create_status_icon("disconnected")
        self.paused_icon = create_status_icon("paused")
        
        self.setIcon(self.connected_icon)
        self.setToolTip("Network Monitor\nClick to open")
        
        # Connect clicked signal to show main window
        self.activated.connect(self.on_tray_activated)
        self.show()

    def setup_context_menu(self):
        # Create context menu
        self.menu = QMenu()

        # Show Config action
        show_config_action = QAction("Show Configuration", self.menu)
        show_config_action.triggered.connect(self.show_config)
        self.menu.addAction(show_config_action)

        # Add separator
        self.menu.addSeparator()

        # Pause/Resume action
        self.toggle_monitoring_action = QAction("Pause Monitoring", self.menu)
        self.toggle_monitoring_action.triggered.connect(self.toggle_monitoring)
        self.menu.addAction(self.toggle_monitoring_action)

        # Add separator
        self.menu.addSeparator()

        # Exit action
        exit_action = QAction("Exit", self.menu)
        exit_action.triggered.connect(self.exit_application)
        self.menu.addAction(exit_action)

        # Set the context menu
        self.setContextMenu(self.menu)

    def show_config(self):
        """Show the main configuration window"""
        self.monitor.main_window.show()
        self.monitor.main_window.raise_()
        self.monitor.main_window.activateWindow()

    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        self.monitor.toggle_monitoring()
        # Update action text based on monitoring state
        if self.monitor.is_monitoring:
            self.toggle_monitoring_action.setText("Pause Monitoring")
            self.setIcon(self.connected_icon)  # Reset to last known state
            self.showMessage(
                "Network Monitor",
                "Monitoring resumed",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.toggle_monitoring_action.setText("Resume Monitoring")
            self.setIcon(self.paused_icon)  # Set yellow paused icon
            self.showMessage(
                "Network Monitor",
                "Monitoring paused",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def exit_application(self):
        """Cleanly exit the application"""
        # You might want to add cleanup code here
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left click
            self.show_config()

    def update_status(self, result):
        # Only update icon if monitoring is active
        if self.monitor.is_monitoring:
            icon = self.connected_icon if result.is_connected else self.disconnected_icon
            self.setIcon(icon)
        self.setToolTip(f"Network Monitor\nStatus: {result.status}\nPing: {result.ping_time}ms")

    def showMessage(self, title, message, icon, duration=3000):
        """Override to ensure notifications are shown properly"""
        if self.isSystemTrayAvailable() and self.supportsMessages():
            super().showMessage(title, message, icon, duration)