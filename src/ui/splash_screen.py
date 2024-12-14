from PyQt6.QtWidgets import QSplashScreen, QProgressBar
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPixmap, QLinearGradient, QFont
from src.ui.icons import create_app_icon

class SplashScreen(QSplashScreen):
    def __init__(self):
        # Create a modern-looking splash screen
        size = QSize(400, 300)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        self.setWindowIcon(create_app_icon())
        
        # Create gradient background
        self.gradient = QLinearGradient(0, 0, size.width(), size.height())
        self.gradient.setColorAt(0, QColor("#2c3e50"))  # Dark blue-gray
        self.gradient.setColorAt(1, QColor("#34495e"))  # Lighter blue-gray
        
        # Configure progress bar with modern style
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, size.height() - 70, size.width() - 100, 4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: #2ecc71;
                border-radius: 2px;
            }
        """)
        
        self.version = "1.0.0"
        
    def drawContents(self, painter: QPainter):
        # Draw background
        painter.fillRect(self.rect(), self.gradient)
        
        # Configure text rendering
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw app name
        title_font = QFont("Segoe UI", 24, QFont.Weight.Light)
        painter.setFont(title_font)
        painter.setPen(QColor("white"))
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignCenter,
            "Network Monitor"
        )
        
        # Draw version
        version_font = QFont("Segoe UI", 10)
        painter.setFont(version_font)
        painter.setPen(QColor(255, 255, 255, 180))  # Semi-transparent white
        version_rect = self.rect()
        version_rect.setBottom(self.progress_bar.y() - 10)
        painter.drawText(
            version_rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            f"Version {self.version}"
        )
        
        # Draw loading text
        loading_font = QFont("Segoe UI", 9)
        painter.setFont(loading_font)
        painter.setPen(QColor(255, 255, 255, 150))  # More transparent white
        loading_rect = self.rect()
        loading_rect.setTop(self.progress_bar.y() + 15)
        painter.drawText(
            loading_rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            "Loading..."
        )