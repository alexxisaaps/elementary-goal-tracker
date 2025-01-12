import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Granite', '7.0')

from gi.repository import Gtk, GLib, Gio, Adw, Gdk, Granite
from .window import GoalWindow
from .dialogs import AboutDialog, SettingsDialog, ListDialog, GoalDialog
from .config import APP_ID, APP_NAME

class GoalApplication(Adw.Application):
    """The main application class"""
    
    def __init__(self):
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
        GLib.set_application_name(APP_NAME)
        
    def do_startup(self):
        """Initialize the application on startup"""
        # Initialize Granite
        Granite.init()
        
        # Initialize parent
        Adw.Application.do_startup(self)

        # Set up actions
        self.setup_actions()
        
        try:
            # Load GResource file
            resource_path = '/usr/share/goaltracker/resources.gresource'
            
            if os.path.exists(resource_path):
                resource = Gio.Resource.load(resource_path)
                resource._register()
                
                # Load CSS provider manually
                css_provider = Gtk.CssProvider()
                css_path = "/io/github/alexxisaapps/elementary_goal_tracker/style.css"
                
                bytes = Gio.resources_lookup_data(css_path, 0)
                css_provider.load_from_data(bytes.get_data())
                
                Gtk.StyleContext.add_provider_for_display(
                    Gdk.Display.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
        except Exception as e:
            print(f"Error loading resources: {e}")
            import traceback
            traceback.print_exc()
            
        # Set up style manager
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
        
        # Set up application icon
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_theme.add_search_path('/usr/share/icons')

    def do_activate(self):
        """Create and show the main window when the application is activated"""
        win = self.get_active_window()
        if not win:
            win = GoalWindow(application=self)
        win.present()

    def setup_actions(self):
            """Set up application-wide actions"""
            # Quit action
            quit_action = Gio.SimpleAction.new("quit", None)
            quit_action.connect("activate", lambda *_: self.quit())
            self.add_action(quit_action)
            self.set_accels_for_action("app.quit", ["<Control>q", "<Control>w"])
            
            # About action
            about_action = Gio.SimpleAction.new("about", None)
            about_action.connect("activate", self.on_about_action)
            self.add_action(about_action)
            
            # Settings action
            settings_action = Gio.SimpleAction.new("settings", None)
            settings_action.connect("activate", self.on_settings_action)
            self.add_action(settings_action)
            self.set_accels_for_action("app.settings", ["<Control>comma"])
            
            # New list action
            new_list_action = Gio.SimpleAction.new("new-list", None)
            new_list_action.connect("activate", self.on_new_list_action)
            self.add_action(new_list_action)
            self.set_accels_for_action("app.new-list", ["<Control>n"])
            
            # New goal action
            new_goal_action = Gio.SimpleAction.new("new-goal", None)
            new_goal_action.connect("activate", self.on_new_goal_action)
            self.add_action(new_goal_action)
            self.set_accels_for_action("app.new-goal", ["<Control>g"])
            
            # Backup action
            backup_action = Gio.SimpleAction.new("backup", None)
            backup_action.connect("activate", self.on_backup_action)
            self.add_action(backup_action)

    def on_about_action(self, action, param):
            """Handle about action"""
            window = self.get_active_window()
            if window:
                dialog = AboutDialog(window)
                dialog.connect('response', lambda d, r: d.destroy())
                dialog.present()

    def on_settings_action(self, action, param):
            """Handle settings action"""
            window = self.get_active_window()
            if window:
                dialog = SettingsDialog(window, window.settings)
                dialog.connect('response', lambda d, r: d.destroy())
                dialog.present()

    def on_new_list_action(self, action, param):
            """Handle new list action"""
            window = self.get_active_window()
            if window:
                dialog = ListDialog(window, "Add New List", "")
                dialog.connect('response', window.on_add_list_response)
                dialog.present()

    def on_new_goal_action(self, action, param):
            """Handle new goal action"""
            window = self.get_active_window()
            if window and window.add_goal_button.get_sensitive():
                dialog = GoalDialog(window, "Add New Goal", "")
                dialog.connect('response', window.on_add_goal_response)
                dialog.present()

    def on_backup_action(self, action, param):
            """Handle backup action"""
            window = self.get_active_window()
            if window:
                window.list_manager.backup_lists()
                # Show success message
                toast = Adw.Toast.new("Backup created successfully")
                toast.set_timeout(3)
                window.add_toast(toast)

    def setup_data_directories(self):
        """Set up necessary data directories for the application"""
        app_name = "goaltracker"
        user_data_dir = os.path.join(GLib.get_user_data_dir(), app_name)
        user_cache_dir = os.path.join(GLib.get_user_cache_dir(), app_name)
        user_config_dir = os.path.join(GLib.get_user_config_dir(), app_name)
        
        # Create necessary directories
        os.makedirs(user_data_dir, exist_ok=True)
        os.makedirs(user_cache_dir, exist_ok=True)
        os.makedirs(user_config_dir, exist_ok=True)
        
        return user_data_dir, user_cache_dir, user_config_dir