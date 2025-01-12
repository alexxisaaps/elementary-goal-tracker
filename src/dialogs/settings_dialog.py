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
        self.set_default_size(500, -1)
        
        # Header Bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        self.set_titlebar(header_bar)
        
        # Reset button
        reset_button = Gtk.Button(label="Reset All")
        reset_button.add_css_class('destructive-action')
        reset_button.connect('clicked', self.on_reset_clicked)
        header_bar.pack_start(reset_button)
        
        # Close button
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self._on_response, Gtk.ResponseType.OK)
        header_bar.pack_end(close_button)
        
        # Content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_child(scrolled)
        
        # Main box
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
        
        # Notifications section
        notifications_section = self.create_section("Notifications")
        main_box.append(notifications_section)
        
        # Enable notifications setting
        notifications_row = self.create_setting_row(
            "Enable Notifications",
            "Show notifications for upcoming deadlines",
            'enable_notifications'
        )
        notifications_section.append(notifications_row)
        
        # Deadline reminder setting
        deadline_box = self.create_spinbutton_row(
            "Default Reminder",
            "Days before deadline to show notification",
            'default_deadline_reminder',
            1,  # min value
            7,  # max value
            1   # step
        )
        deadline_box.set_sensitive(self.settings.get('enable_notifications'))
        notifications_section.append(deadline_box)
        
        # Connect notification toggle to deadline spinner sensitivity
        self.deadline_box = deadline_box
        notifications_row.get_first_child().connect('notify::active', self.on_notifications_toggled)
        
        # Appearance section
        appearance_section = self.create_section("Appearance")
        main_box.append(appearance_section)
        
        # Theme selector
        theme_box = self.create_theme_selector()
        appearance_section.append(theme_box)

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

    def create_spinbutton_row(self, title, description, setting_key, min_value, max_value, step):
        """Create a row for a numeric setting"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.add_css_class('setting-row')
        
        # Labels box
        labels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        labels_box.set_hexpand(True)
        row.append(labels_box)
        
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
        
        # Spin button
        adjustment = Gtk.Adjustment(
            value=self.settings.get(setting_key),
            lower=min_value,
            upper=max_value,
            step_increment=step
        )
        
        spin = Gtk.SpinButton()
        spin.set_adjustment(adjustment)
        spin.set_numeric(True)
        spin.connect('value-changed', self._on_spin_changed, setting_key)
        row.append(spin)
        
        # Reset button (only shown if setting is modified)
        if self.settings.is_modified(setting_key):
            reset_button = Gtk.Button()
            reset_button.set_icon_name('edit-undo-symbolic')
            reset_button.add_css_class('flat')
            reset_button.connect('clicked', self.on_reset_setting, setting_key, spin)
            row.append(reset_button)
        
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
    
    def _on_spin_changed(self, spin, setting_key):
        """Handle numeric setting change"""
        self.settings.set(setting_key, spin.get_value_as_int())
    
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
        
    def on_notifications_toggled(self, check, param):
            """Handle notifications toggle"""
            self.deadline_box.set_sensitive(check.get_active())
        
    def on_reset_setting(self, button, setting_key, widget):
            """Reset a single setting to its default value"""
            default_value = self.settings.default_settings[setting_key]
            self.settings.reset_setting(setting_key)
            
            if isinstance(widget, Gtk.CheckButton):
                widget.set_active(default_value)
            elif isinstance(widget, Gtk.SpinButton):
                widget.set_value(default_value)
            elif isinstance(widget, Gtk.ComboBoxText):
                widget.set_active_id(default_value)
                
            # Remove the reset button
            button.get_parent().remove(button)
        
    def on_reset_clicked(self, button):
            """Reset all settings to defaults"""
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Reset All Settings?"
            )
            dialog.format_secondary_text(
                "This will reset all settings to their default values. This action cannot be undone."
            )
            
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                self.settings.reset()
                self._on_response(None, Gtk.ResponseType.OK)  # Close settings dialog
        
    def _on_response(self, button, response):
            """Handle dialog response"""
            self.emit("response", response)