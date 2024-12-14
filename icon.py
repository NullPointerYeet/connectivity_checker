from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

def create_app_icon():
    # Create a 64x64 pixel pixmap for app icon
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Draw outer circle
    painter.setBrush(QColor("#34495e"))  # Dark blue-grey
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 60, 60)
    
    # Draw inner circle
    painter.setBrush(QColor("#2ecc71"))  # Green
    painter.drawEllipse(12, 12, 40, 40)
    
    painter.end()
    return pixmap 