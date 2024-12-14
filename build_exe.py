import os
from PyQt6.QtWidgets import QApplication
import sys
from icon import create_app_icon
from PyQt6.QtGui import QIcon

# Initialize QApplication first
app = QApplication(sys.argv)

# Create and save the icon
pixmap = create_app_icon()
pixmap.save("app_icon.png")

# Convert PNG to ICO (requires pillow)
from PIL import Image
img = Image.open("app_icon.png")
img.save("app_icon.ico")

# Clean up PNG
os.remove("app_icon.png")

# Run PyInstaller
os.system("pyinstaller build.spec")