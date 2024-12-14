# src/ui/icons.py
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

def create_app_icon():
    """Create the main application icon"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw outer circle
    painter.setBrush(QColor("#34495e"))  # Dark blue-grey
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 60, 60)
    
    # Draw inner circle
    painter.setBrush(QColor("#2ecc71"))  # Green
    painter.drawEllipse(12, 12, 40, 40)
    
    painter.end()
    return QIcon(pixmap)

def create_status_icon(status):
    """Create status-specific icons for the system tray"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw outer circle
    painter.setBrush(QColor("#34495e"))  # Dark blue-grey
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 60, 60)
    
    # Draw inner circle with status-specific color
    if status == "connected":
        color = QColor("#2ecc71")  # Green
    elif status == "disconnected":
        color = QColor("#e74c3c")  # Red
    elif status == "paused":
        color = QColor("#f1c40f")  # Yellow
    else:
        color = QColor("#95a5a6")  # Gray (fallback)
        
    painter.setBrush(color)
    painter.drawEllipse(12, 12, 40, 40)
    
    painter.end()
    return QIcon(pixmap)