import csv
import os
from datetime import datetime

class Logger:
    def __init__(self):
        self.log_file = "network_log.csv"
        self.initialize_log()
    
    def initialize_log(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Server", "Ping (ms)", "Status"])

    def log_result(self, result):
        """Log a ping result to the CSV file"""
        try:
            with open(self.log_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    result.server,
                    result.ping_time if result.is_connected else "N/A",
                    result.status
                ])
        except Exception as e:
            self.log_error(f"Error logging result: {e}")

    def rotate_logs(self, settings):
        """Rotate log file if it gets too large"""
        try:
            log_settings = settings.get("log_rotation", {
                "enabled": False,
                "max_size_mb": 10,
                "backup_count": 3
            })
            
            if not log_settings["enabled"]:
                return
            
            if not os.path.exists(self.log_file):
                return
            
            current_size = os.path.getsize(self.log_file) / (1024 * 1024)
            
            if current_size > log_settings["max_size_mb"]:
                self._perform_rotation(log_settings["backup_count"])
            
        except Exception as e:
            self.log_error(f"Error rotating logs: {e}")

    def _perform_rotation(self, backup_count):
        """Helper method to perform the actual log rotation"""
        for i in range(backup_count - 1, 0, -1):
            old_file = f"{self.log_file}.{i}"
            new_file = f"{self.log_file}.{i + 1}"
            if os.path.exists(old_file):
                os.rename(old_file, new_file)
        
        if os.path.exists(self.log_file):
            os.rename(self.log_file, f"{self.log_file}.1")
        
        self.initialize_log()

    def log_error(self, message):
        """Log error messages"""
        error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{error_time}] Error: {message}")  # Could be expanded to file logging
