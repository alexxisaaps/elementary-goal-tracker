import os
import json
from gi.repository import GLib

class Settings:
    """Service for managing application settings"""
    
    def __init__(self):
        self.data_dir = os.path.join(GLib.get_user_data_dir(), 'goaltracker')
        os.makedirs(self.data_dir, exist_ok=True)
        self.settings_file = os.path.join(self.data_dir, 'settings.json')
        
        # Define default settings
        self.default_settings = {
            'auto_sort_items': False,
            'theme': 'light',
            'enable_notifications': True,
            'default_deadline_reminder': 1  # days before deadline
        }
        
        # Load current settings
        self.current_settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # If settings file doesn't exist, create it with defaults
            settings = self.default_settings.copy()
            self.save_settings_to_file(settings)
            return settings
        except json.JSONDecodeError:
            # If settings file is corrupted, recreate with defaults
            print("Settings file corrupted, recreating with defaults")
            settings = self.default_settings.copy()
            self.save_settings_to_file(settings)
            return settings
    
    def save_settings_to_file(self, settings):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key):
        """Get a setting value"""
        return self.current_settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        """Set a setting value"""
        self.current_settings[key] = value
        self.save_settings_to_file(self.current_settings)
    
    def reset(self):
        """Reset all settings to defaults"""
        self.current_settings = self.default_settings.copy()
        self.save_settings_to_file(self.current_settings)
    
    def reset_setting(self, key):
        """Reset a specific setting to its default value"""
        if key in self.default_settings:
            self.current_settings[key] = self.default_settings[key]
            self.save_settings_to_file(self.current_settings)
            
    def get_all(self):
        """Get all current settings"""
        return self.current_settings.copy()
        
    def is_modified(self, key):
        """Check if a setting has been modified from its default"""
        return self.get(key) != self.default_settings.get(key)