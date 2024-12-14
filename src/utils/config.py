import json
import os

class Config:
    def __init__(self):
        self.config_file = 'settings.json'
        self.default_settings = {
            'server': '8.8.8.8',
            'check_interval': 1000,
            'notifications': {
                'notify_on_disconnect': True,
                'notify_on_reconnect': True,
                'notify_on_poor_connection': True,
                'poor_connection_threshold': 200
            },
            'log_rotation': {
                'enabled': False,
                'max_size_mb': 10,
                'backup_count': 3
            }
        }
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    merged_settings = self.default_settings.copy()
                    merged_settings.update(loaded_settings)
                    return merged_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        return self.default_settings.copy()

    def save_settings(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
