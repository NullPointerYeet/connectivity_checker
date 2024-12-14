from src.core.monitor import NetworkMonitor
from src.ui.splash_screen import SplashScreen
from src.ui.icons import create_app_icon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QSystemTrayIcon
import sys

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide properties
    app.setApplicationName("Network Monitor")
    app.setApplicationDisplayName("Network Monitor")
    app.setApplicationVersion(NetworkMonitor.VERSION)
    app.setWindowIcon(create_app_icon())
    app.setQuitOnLastWindowClosed(False)
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Ensure splash is shown
    app.processEvents()
    
    # Create monitor instance
    monitor = NetworkMonitor()
    
    # Simulate loading process
    for i in range(100):
        splash.progress_bar.setValue(i)
        app.processEvents()
        QTimer.singleShot(20, lambda: None)
    
    # Close splash and show main window after a short delay
    QTimer.singleShot(2000, lambda: {
        splash.close(),
        monitor.main_window.show(),
        monitor.system_tray.showMessage(
            "Network Monitor",
            "Application is running and monitoring network connectivity",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    })
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
