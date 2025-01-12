from gi.repository import Gtk, Adw

from gi.repository import Gtk, Adw

class SettingsDialog(Gtk.Dialog):
    """Dialog for application settings"""
    
    def __init__(self, parent, settings):
        super().__init__(
            title="Settings",
            transient_for=parent,
            modal=True,
            destroy_with_parent=True
        )

        self.settings = settings
        # Set a more appropriate default size
        self.set_default_size(460, 400)
        self.set_size_request(400, -1)  # Minimum width but natural height
        
        # Header Bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        self.set_titlebar(header_bar)
        
        # Close button
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self._on_response, Gtk.ResponseType.OK)
        header_bar.pack_end(close_button)
        
        # Main Content Area
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(content_box)
        
        # Scrolled Window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)  # Allow vertical expansion
        content_box.append(scrolled)
        
        # Main box for settings
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        scrolled.set_child(main_box)
        
        # Behavior Section
        behavior_section = self.create_section("Behavior")
        main_box.append(behavior_section)
        
        # Auto-sort setting
        auto_sort_row = self.create_setting_row(
            "Auto-sort Items",
            "Automatically move completed items to the bottom of the list",
            'auto_sort_items'
        )
        behavior_section.append(auto_sort_row)
        
        # Appearance section
        appearance_section = self.create_section("Appearance")
        main_box.append(appearance_section)
        
        # Theme selector
        theme_box = self.create_theme_selector()
        appearance_section.append(theme_box)

        # Show all content immediately
        self.show()

    def create_section(self, title):
        """Create a settings section with title"""
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        section.add_css_class('settings-section')
        
        title_label = Gtk.Label(label=title)
        title_label.add_css_class('settings-section-title')
        title_label.set_halign(Gtk.Align.START)
        section.append(title_label)
        
        return section

    def create_setting_row(self, title, description, setting_key):
        """Create a row for a boolean setting"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.add_css_class('setting-row')
        
        # Left side with checkbox and title
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        left_box.set_hexpand(True)
        row.append(left_box)
        
        # Checkbox
        check = Gtk.CheckButton()
        check.set_active(self.settings.get(setting_key))
        check.connect('toggled', self._on_setting_toggled, setting_key)
        left_box.append(check)
        
        # Labels box
        labels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        left_box.append(labels_box)
        
        # Title
        title_label = Gtk.Label(label=title)
        title_label.add_css_class('setting-title')
        title_label.set_halign(Gtk.Align.START)
        labels_box.append(title_label)
        
        # Description
        description_label = Gtk.Label(label=description)
        description_label.add_css_class('setting-description')
        description_label.set_wrap(True)
        description_label.set_xalign(0)
        labels_box.append(description_label)
        
        # Reset button (only shown if setting is modified)
        if self.settings.is_modified(setting_key):
            reset_button = Gtk.Button()
            reset_button.set_icon_name('edit-undo-symbolic')
            reset_button.add_css_class('flat')
            reset_button.connect('clicked', self.on_reset_setting, setting_key, check)
            row.append(reset_button)
        
        # Make the entire row clickable
        gesture = Gtk.GestureClick()
        gesture.connect('released', self._on_row_clicked, check)
        row.add_controller(gesture)
        
        return row

    def create_theme_selector(self):
        """Create the theme selection row"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.add_css_class('setting-row')
        
        # Labels box
        labels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        labels_box.set_hexpand(True)
        row.append(labels_box)
        
        # Title
        title_label = Gtk.Label(label="Theme")
        title_label.add_css_class('setting-title')
        title_label.set_halign(Gtk.Align.START)
        labels_box.append(title_label)
        
        # Description
        description_label = Gtk.Label(label="Choose between light and dark theme")
        description_label.add_css_class('setting-description')
        description_label.set_wrap(True)
        description_label.set_xalign(0)
        labels_box.append(description_label)
        
        # Theme combo box
        combo = Gtk.ComboBoxText()
        combo.append('light', "Light")
        combo.append('dark', "Dark")
        combo.set_active_id(self.settings.get('theme'))
        combo.connect('changed', self._on_theme_changed)
        row.append(combo)
        
        # Reset button (only shown if setting is modified)
        if self.settings.is_modified('theme'):
            reset_button = Gtk.Button()
            reset_button.set_icon_name('edit-undo-symbolic')
            reset_button.add_css_class('flat')
            reset_button.connect('clicked', self.on_reset_setting, 'theme', combo)
            row.append(reset_button)
        
        return row

    def _on_setting_toggled(self, button, setting_key):
        """Handle boolean setting toggle"""
        self.settings.set(setting_key, button.get_active())
    
    def _on_theme_changed(self, combo):
        """Handle theme selection change"""
        self.settings.set('theme', combo.get_active_id())
        
        # Update the application theme
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(
            Adw.ColorScheme.FORCE_DARK if combo.get_active_id() == 'dark'
            else Adw.ColorScheme.FORCE_LIGHT
        )
    
    def _on_row_clicked(self, gesture, n_press, x, y, check):
        """Handle clickable row"""
        if isinstance(check, Gtk.CheckButton):
            check.set_active(not check.get_active())
    
    def on_reset_setting(self, button, setting_key, widget):
        """Reset a single setting to its default value"""
        default_value = self.settings.default_settings[setting_key]
        self.settings.reset_setting(setting_key)
        
        if isinstance(widget, Gtk.CheckButton):
            widget.set_active(default_value)
        elif isinstance(widget, Gtk.ComboBoxText):
            widget.set_active_id(default_value)
            
        # Remove the reset button
        button.get_parent().remove(button)
        
        if response == Gtk.ResponseType.YES:
            self.settings.reset()
            self._on_response(None, Gtk.ResponseType.OK)  # Close settings dialog
    
    def _on_response(self, button, response):
        """Handle dialog response"""
        self.emit("response", response)