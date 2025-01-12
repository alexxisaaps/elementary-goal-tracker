from gi.repository import Gtk, GLib, Pango
from ..config import APP_NAME, APP_VERSION

class AboutDialog(Gtk.Dialog):
    """Dialog showing application information and credits"""
    
    def __init__(self, parent):
        super().__init__(
            title=f"About {APP_NAME}",
            transient_for=parent,
            modal=True,
            destroy_with_parent=True
        )

        self.set_deletable(False)
        self.set_default_size(400, -1)
        self.set_size_request(350, -1)
        
        # Header Bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        self.set_titlebar(header_bar)
        
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self._on_response, Gtk.ResponseType.OK)
        header_bar.pack_end(close_button)
        
        # Scrolled Window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_propagate_natural_height(True)
        self.set_child(scrolled)
        
        # Main Content Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.add_css_class('about-dialog-box')
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        scrolled.set_child(main_box)
        
        # App Info Section
        app_info = self.create_section(
            APP_NAME,
            [
                "A simple and elegant goal tracking app",
                f"Version {APP_VERSION}"
            ]
        )
        app_info.add_css_class('app-info-section')
        main_box.append(app_info)
        
        # Credits Section
        credits_section = self.create_section(
            "Credits",
            [
                "Icon Design by Genesis Diaz",
                "Built with Python and GTK4"
            ]
        )
        main_box.append(credits_section)
        
        # Links Box
        links_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        links_box.set_halign(Gtk.Align.CENTER)
        main_box.append(links_box)
        
        # Designer Link Button
        designer_button = Gtk.Button(label="View Designer Profile")
        designer_button.add_css_class('link-button')
        designer_button.connect('clicked', lambda _: self.open_url("https://www.behance.net/artbygened"))
        links_box.append(designer_button)
        
        # Separator for visual spacing
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.add_css_class('about-separator')
        main_box.append(separator)
        
        # Donate Button
        donate_button = Gtk.Button(label="💜 Support Goal Tracker")
        donate_button.add_css_class('donate-button')
        donate_button.connect('clicked', self.on_donate_clicked)
        main_box.append(donate_button)

    def open_url(self, url):
        """Open a URL in the default web browser"""
        launcher = Gtk.UriLauncher.new(url)
        launcher.launch(self, None, self._on_launch_finished)

    def _on_launch_finished(self, source, result):
        """Handle URL launch completion"""
        try:
            source.launch_finish(result)
        except GLib.Error as e:
            print(f"Error opening URL: {e.message}")
    
    def on_donate_clicked(self, button):
        """Handle donate button click"""
        url = "#"  # Replace with actual donation URL
        self.open_url(url)

    def create_section(self, title, items):
        """Create a section in the about dialog"""
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section.add_css_class('about-section')
        
        # Section Title
        section_title = Gtk.Label(label=title)
        section_title.add_css_class('about-section-title')
        section_title.set_halign(Gtk.Align.CENTER)
        section.append(section_title)
        
        # Section Content
        for item in items:
            item_label = Gtk.Label(label=item)
            item_label.add_css_class('about-section-content')
            item_label.set_halign(Gtk.Align.CENTER)
            item_label.set_wrap(True)
            item_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            section.append(item_label)
        
        return section

    def _on_response(self, button, response):
        """Handle dialog response"""
        self.emit("response", response)