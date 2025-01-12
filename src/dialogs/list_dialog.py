from gi.repository import Gtk

class ListDialog(Gtk.Dialog):
    """Dialog for adding/editing lists"""
    
    def __init__(self, parent, title, current_text=""):
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
        
        text_label = Gtk.Label(label="List name:")
        text_label.set_halign(Gtk.Align.START)
        text_box.append(text_label)
        
        self.entry = Gtk.Entry()
        self.entry.set_text(current_text)
        self.entry.set_hexpand(True)
        self.entry.connect('activate', lambda w: self._on_response(None, Gtk.ResponseType.OK))
        text_box.append(self.entry)

    def _on_response(self, button, response):
        """Handle dialog response"""
        self.emit("response", response)