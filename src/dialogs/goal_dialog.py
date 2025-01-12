from gi.repository import Gtk, GLib

class GoalDialog(Gtk.Dialog):
    """Dialog for adding or editing goals and steps"""
    
    def __init__(self, parent, title, current_text="", is_step=False, 
                 current_position=None, max_position=None, current_deadline=None):
        super().__init__(
            title=title,
            transient_for=parent,
            modal=True,
            destroy_with_parent=True
        )

        self.set_deletable(False)
        self.set_default_size(400, -1)
        
        # Header Bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        self.set_titlebar(header_bar)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_response, Gtk.ResponseType.CANCEL)
        header_bar.pack_start(cancel_button)
        
        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.add_css_class('suggested-action')
        save_button.connect("clicked", self._on_response, Gtk.ResponseType.OK)
        header_bar.pack_end(save_button)
        
        # Content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        self.set_child(box)
        
        # Text entry
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.append(text_box)
        
        text_label = Gtk.Label(label=f"{'Step' if is_step else 'Goal'} name:")
        text_label.set_halign(Gtk.Align.START)
        text_box.append(text_label)
        
        self.entry = Gtk.Entry()
        self.entry.set_text(current_text)
        self.entry.set_hexpand(True)
        self.entry.connect('activate', lambda w: self._on_response(None, Gtk.ResponseType.OK))
        text_box.append(self.entry)
        
        # Deadline section
        deadline_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.append(deadline_box)
        
        deadline_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        deadline_box.append(deadline_header)
        
        self.deadline_switch = Gtk.Switch()
        self.deadline_switch.set_active(current_deadline is not None)
        self.deadline_switch.connect('notify::active', self._on_deadline_switch_toggled)
        deadline_header.append(self.deadline_switch)
        
        deadline_label = Gtk.Label(label="Set deadline")
        deadline_label.set_halign(Gtk.Align.START)
        deadline_header.append(deadline_label)
        
        # Calendar for deadline selection
        self.calendar = Gtk.Calendar()
        self.calendar.set_sensitive(current_deadline is not None)
        deadline_box.append(self.calendar)
        
        if current_deadline:
            date = datetime.strptime(current_deadline, "%Y-%m-%d").date()
            self.calendar.select_day(GLib.DateTime.new_local(date.year, date.month, date.day, 0, 0, 0))
        
        # Position control
        if current_position is not None and max_position is not None:
            position_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            box.append(position_box)
            
            position_label = Gtk.Label(label="Position:")
            position_label.set_halign(Gtk.Align.START)
            position_box.append(position_label)
            
            adjustment = Gtk.Adjustment(
                value=current_position,
                lower=1,
                upper=max_position,
                step_increment=1,
                page_increment=5,
                page_size=0
            )
            
            self.position_spin = Gtk.SpinButton()
            self.position_spin.set_adjustment(adjustment)
            self.position_spin.set_numeric(True)
            self.position_spin.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
            position_box.append(self.position_spin)
        else:
            self.position_spin = None

    def _on_deadline_switch_toggled(self, switch, param):
        """Handle deadline switch toggle"""
        self.calendar.set_sensitive(switch.get_active())

    def get_deadline(self):
        """Get the selected deadline date"""
        if not self.deadline_switch.get_active():
            return None
            
        date = self.calendar.get_date()
        return date.format("%Y-%m-%d")
    
    def get_position(self):
        """Get the selected position"""
        if self.position_spin:
            return self.position_spin.get_value_as_int()
        return None

    def _on_response(self, button, response):
        """Handle dialog response"""
        self.emit("response", response)