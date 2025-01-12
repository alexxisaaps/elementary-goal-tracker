"""
Goal Tracker - A GTK4 application for tracking goals and tasks
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Granite', '7.0')

from .config import APP_NAME, APP_VERSION, APP_ID
from .application import GoalApplication

def main():
    """Start the application"""
    try:
        app = GoalApplication()
        return app.run()
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Fatal error: {error_msg}", file=sys.stderr)
        return 1