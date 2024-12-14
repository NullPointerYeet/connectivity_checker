from src.core.monitor import NetworkMonitor
from PyQt6.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    monitor = NetworkMonitor()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
