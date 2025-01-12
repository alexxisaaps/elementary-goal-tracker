from gi.repository import Gtk

class ConfirmDialog(Gtk.Dialog):
    """A dialog for confirming destructive actions"""
    
    def __init__(self, parent, title, message):
        super().__init__(
            title=title,
            transient_for=parent,
            modal=True,
            destroy_with_parent=True
        )
        
        self.set_deletable(False)

        # Header Bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        self.set_titlebar(header_bar)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_response, Gtk.ResponseType.CANCEL)
        header_bar.pack_start(cancel_button)
        
        # Delete button
        delete_button = Gtk.Button(label="Delete")
        delete_button.add_css_class('delete-button')
        delete_button.connect("clicked", self._on_response, Gtk.ResponseType.OK)
        header_bar.pack_end(delete_button)
        
        # Content box
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        self.set_child(box)
        
        # Message label
        label = Gtk.Label(label=message)
        label.set_wrap(True)
        label.set_max_width_chars(40)
        box.append(label)

    def _on_response(self, button, response):
        """Handle dialog response"""
        self.emit("response", response)