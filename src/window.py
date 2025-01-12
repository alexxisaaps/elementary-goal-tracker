from gi.repository import Gtk, GLib, Adw

from .services.settings import Settings
from .services.list_manager import ListManager
from .services.daily_quote import DailyQuote
from .widgets.goal import GoalWidget
from .dialogs.about_dialog import AboutDialog
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.goal_dialog import GoalDialog
from .dialogs import ConfirmDialog
from .widgets import GoalWidget, StepWidget

class GoalWindow(Adw.ApplicationWindow):
    """The main window of the application"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize services
        self.settings = Settings()
        self.daily_quote = DailyQuote()
        self.list_manager = ListManager()

        # Set up window properties
        self.setup_window()
        
        # Create UI components
        self.create_layout()
        
        # Load initial data
        self.load_initial_data()
        
    def setup_window(self):
        """Set up basic window properties"""
        self.set_title("Goal Tracker")
        self.set_default_size(1100, 600)
        self.set_size_request(800, 400)
        
    def create_layout(self):
        """Create the main layout of the window"""
        # Main layout box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_size_request(800, -1)
        self.set_content(main_box)
        
        # HeaderBar
        header_bar = self.create_header_bar()
        main_box.append(header_bar)
        
        # Main paned container
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_resize_start_child(True)
        paned.set_shrink_start_child(False)
        paned.set_shrink_end_child(False)
        paned.set_wide_handle(True)
        main_box.append(paned)

        # Sidebar
        sidebar = self.create_sidebar()
        sidebar.set_size_request(200, -1)
        paned.set_start_child(sidebar)
                
        # Content area
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.content_box.set_hexpand(True)
        self.content_box.set_size_request(400, -1)
        paned.set_end_child(self.content_box)
        
        # Set initial position
        paned.set_position(250)
        
        # Quote section
        self.quote_box = self.create_quote_section()
        self.content_box.append(self.quote_box)
        
        # Goals section
        self.create_goals_section()
        
    def create_header_bar(self):
        """Create the header bar with its buttons"""
        header_bar = Adw.HeaderBar()
        
        # About button
        about_button = Gtk.Button(label="About")
        about_button.add_css_class('help-button')
        about_button.connect('clicked', self.on_about_clicked)
        header_bar.pack_start(about_button)
        
        # Settings button
        settings_button = Gtk.Button(label="⚙️")
        settings_button.add_css_class('help-button')
        settings_button.connect('clicked', self.on_settings_clicked)
        header_bar.pack_start(settings_button)
        
        # Add goal button
        self.add_goal_button = Gtk.Button(label="Add Goal")
        self.add_goal_button.add_css_class('suggested-action')
        self.add_goal_button.connect('clicked', self.on_add_goal_clicked)
        self.add_goal_button.set_sensitive(False)  # Initially disabled
        header_bar.pack_end(self.add_goal_button)
        
        return header_bar
    
    def create_sidebar(self):
            """Create the sidebar for list management"""
            sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            sidebar_box.add_css_class('sidebar')
            sidebar_box.set_size_request(200, -1)
            sidebar_box.set_vexpand(True)
            
            # Lists header
            header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            header_box.add_css_class('sidebar-header')
            
            lists_title = Gtk.Label(label="Your Goals")
            lists_title.add_css_class('sidebar-title')
            lists_title.set_halign(Gtk.Align.START)
            lists_title.set_hexpand(True)
            header_box.append(lists_title)
            
            add_list_button = Gtk.Button()
            add_list_button.set_icon_name('list-add-symbolic')
            add_list_button.add_css_class('flat')
            add_list_button.connect('clicked', self.on_add_list_clicked)
            header_box.append(add_list_button)
            
            sidebar_box.append(header_box)
            
            # Lists container
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_vexpand(True)
            scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            
            self.lists_box = Gtk.ListBox()
            self.lists_box.add_css_class('lists-box')
            self.lists_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
            self.lists_box.connect('row-selected', self.on_list_selected)
            
            scrolled.set_child(self.lists_box)
            sidebar_box.append(scrolled)
            
            return sidebar_box
    
    def on_add_list_clicked(self, button):
        """Handle adding a new list"""
        dialog = ListDialog(self, "Add New List", "")
        dialog.connect('response', self.on_add_list_response)
        dialog.present()

    def on_add_list_response(self, dialog, response):
        """Handle response from add list dialog"""
        if response == Gtk.ResponseType.OK:
            list_name = dialog.entry.get_text()
            if list_name:
                list_id = self.list_manager.add_list(list_name)
                self.update_lists_sidebar()
                # Select the new list
                self.select_list(list_id)
        dialog.destroy()

    def create_list_row(self, list_data):
        """Create a row for a list in the sidebar"""
        row = Gtk.ListBoxRow()
        row.list_id = list_data['id']
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.add_css_class('list-row')
        
        label = Gtk.Label(label=list_data['name'])
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        box.append(label)
        
        # Edit and delete buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        button_box.set_halign(Gtk.Align.END)
        
        edit_button = Gtk.Button()
        edit_button.set_icon_name('document-edit-symbolic')
        edit_button.add_css_class('flat')
        edit_button.connect('clicked', self.on_edit_list_clicked, list_data)
        button_box.append(edit_button)
        
        delete_button = Gtk.Button()
        delete_button.set_icon_name('user-trash-symbolic')
        delete_button.add_css_class('trash-icon')
        delete_button.add_css_class('flat')
        delete_button.connect('clicked', self.on_delete_list_clicked, list_data)
        button_box.append(delete_button)
        
        box.append(button_box)
        row.set_child(box)
        
        return row
        
    def on_list_selected(self, list_box, row):
        """Handle list selection in sidebar"""
        if row is None:
            return
        
        list_id = row.list_id
        self.select_list(list_id)

    def on_edit_list_clicked(self, button, list_data):
        """Handle editing a list"""
        dialog = ListDialog(self, "Edit List", list_data['name'])
        dialog.connect('response', lambda d, r: self.on_edit_list_response(d, r, list_data['id']))
        dialog.present()

    def on_edit_list_response(self, dialog, response, list_id):
        """Handle response from edit list dialog"""
        if response == Gtk.ResponseType.OK:
            new_name = dialog.entry.get_text()
            if new_name:
                self.list_manager.edit_list(list_id, new_name)
                self.update_lists_sidebar()
                if hasattr(self, 'current_list') and self.current_list['id'] == list_id:
                    self.goals_title.set_text(f"{new_name} goals:")
        dialog.destroy()

    def on_delete_list_clicked(self, button, list_data):
        """Handle deleting a list"""
        dialog = ConfirmDialog(
            self,
            "Delete List",
            f"Are you sure you want to delete the list '{list_data['name']}' and all its goals?"
        )
        dialog.connect('response', lambda d, r: self.on_delete_list_confirmed(d, r, list_data['id']))
        dialog.present()

    def on_delete_list_confirmed(self, dialog, response, list_id):
        """Handle confirmation of list deletion"""
        if response == Gtk.ResponseType.OK:
            self.list_manager.delete_list(list_id)
            self.update_lists_sidebar()
            
            # Select first available list or clear goals
            if self.list_manager.lists:
                first_list = next(iter(self.list_manager.lists.values()))
                self.select_list(first_list['id'])
            else:
                self.current_list = None
                self.goals = []
                self.clear_goals()
                self.update_empty_state()
                self.add_goal_button.set_sensitive(False)
        
        dialog.destroy()
    
    def create_quote_section(self):
        """Create the daily quote section"""
        quote_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        quote_box.add_css_class('quote-section')
        
        quote_data = self.daily_quote.get_daily_quote()
        
        quote_text = Gtk.Label()
        quote_text.set_markup(f'<span font_size="large">\"{quote_data["text"]}\"</span>')
        quote_text.add_css_class('quote-text')
        quote_text.set_wrap(True)
        quote_text.set_max_width_chars(60)
        
        quote_author = Gtk.Label()
        quote_author.set_markup(f'<span font_size="small">— {quote_data["author"]}</span>')
        quote_author.add_css_class('quote-author')
        
        quote_box.append(quote_text)
        quote_box.append(quote_author)
        
        return quote_box
    
    def create_goals_section(self):
        """Create the goals section with its container and empty state"""
        # Scrolled Window for goals
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.content_box.append(scrolled)
        
        # Goals container
        self.goals_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled.set_child(self.goals_container)
        
        # Goals section header
        self.goals_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.goals_header.set_margin_start(16)
        self.goals_header.set_margin_end(16)
        self.goals_header.set_margin_top(16)
        self.goals_header.set_margin_bottom(8)
        self.goals_header.set_visible(False)
        
        self.goals_title = Gtk.Label(label="Your goals:")
        self.goals_title.add_css_class('goals-header-title')
        self.goals_title.set_halign(Gtk.Align.START)
        self.goals_header.append(self.goals_title)
        
        self.goals_container.append(self.goals_header)
        
        # Goals box for actual goals
        self.goals_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.goals_container.append(self.goals_box)
        
        # Empty state message
        self.empty_state_box = self.create_empty_state()
        self.goals_container.append(self.empty_state_box)

    def load_goals(self):
            """Load goals for the current list"""
            if not hasattr(self, 'current_list'):
                return
                
            for goal_data in self.goals:
                self.goals_box.append(GoalWidget(goal_data, self, self.current_list['id']))
            self.update_goal_numbers()
    
    def add_goal(self, goal_data):
        """Add a new goal to the current list"""
        if not hasattr(self, 'current_list'):
            return
        
        # Add original_position field if not present
        if 'original_position' not in goal_data:
            goal_data['original_position'] = len(self.goals)
            
        # Find insertion position - before completed items if auto-sort is enabled
        if self.settings.get('auto_sort_items'):
            # Find first completed item
            insertion_index = 0
            for i, goal in enumerate(self.goals):
                if goal['completed']:
                    insertion_index = i
                    break
                insertion_index = len(self.goals)
            self.goals.insert(insertion_index, goal_data)
        else:
            self.goals.append(goal_data)
        
        self.list_manager.save_lists()
        goal_widget = GoalWidget(goal_data, self, self.current_list['id'])
        
        # Insert widget at correct position
        if self.settings.get('auto_sort_items'):
            # Find first completed goal widget
            completed_found = False
            for child in self.goals_box:
                if isinstance(child, GoalWidget) and child.goal_data['completed']:
                    # Use insert_after for the previous widget instead of insert_before
                    prev_widget = child.get_prev_sibling()
                    if prev_widget:
                        self.goals_box.insert_child_after(goal_widget, prev_widget)
                    else:
                        self.goals_box.prepend(goal_widget)
                    completed_found = True
                    break
            if not completed_found:
                self.goals_box.append(goal_widget)
        else:
            self.goals_box.append(goal_widget)
        
        self.update_empty_state()
        self.update_goal_numbers()

    def on_add_goal_response(self, dialog, response):
        """Handle response from add goal dialog"""
        if response == Gtk.ResponseType.OK:
            goal_text = dialog.entry.get_text()
            if goal_text:
                self.add_goal({'title': goal_text, 'completed': False, 'steps': []})
        dialog.destroy()

    def remove_goal(self, goal_widget):
        """Remove a goal from the current list"""
        self.goals.remove(goal_widget.goal_data)
        self.list_manager.save_lists()
        self.goals_box.remove(goal_widget)
        self.update_empty_state()
        self.update_goal_numbers()

    def handle_completion(self, completed_widget, is_goal=True):
        """Handle sorting of completed items"""
        if not self.settings.get('auto_sort_items'):
            return
            
        container = self.goals_box if is_goal else completed_widget.parent_goal.steps_box
        items = self.goals if is_goal else completed_widget.parent_goal.goal_data['steps']
        
        # Get current position and completion status
        current_item = completed_widget.goal_data if is_goal else completed_widget.step_data
        current_position = items.index(current_item)
        is_completed = current_item['completed']
        
        # Store original position when completing if not already stored
        if is_completed and 'original_position' not in current_item:
            current_item['original_position'] = current_position
        
        # Remove item from current position
        items.pop(current_position)
        
        if is_completed:
            # When completing, move to end of list
            target_position = len(items)
            items.insert(target_position, current_item)
        else:
            # When uncompleting, restore to original position
            target_position = current_item.get('original_position', 0)
            # Ensure we don't insert beyond list bounds
            target_position = min(target_position, len(items))
            items.insert(target_position, current_item)
            # Clear the original position as it's no longer needed
            current_item.pop('original_position', None)
        
        # Update GUI
        container.remove(completed_widget)
        
        # Reinsert widget at the correct position
        if target_position == 0:
            container.prepend(completed_widget)
        else:
            # Find the widget that should be before our target position
            prev_widget = None
            widget_count = 0
            for child in container:
                if isinstance(child, GoalWidget if is_goal else StepWidget):
                    if widget_count == target_position - 1:
                        prev_widget = child
                        break
                    widget_count += 1
            
            if prev_widget:
                container.insert_child_after(completed_widget, prev_widget)
            else:
                container.append(completed_widget)
        
        # Save changes
        self.list_manager.save_lists()
        
        # Update numbers
        if is_goal:
            self.update_goal_numbers()
        else:
            completed_widget.parent_goal.update_step_numbers()
    
    def update_goal_numbers(self):
        """Update the display numbers for all goals"""
        for i, child in enumerate(self.goals_box):
            if isinstance(child, GoalWidget):
                child.update_number(i + 1)
    
    def load_initial_data(self):
        """Load initial data for the window"""
        # Load lists and select first list if exists
        self.list_manager.load_lists()
        self.update_lists_sidebar()
        
        # Select first list if exists and load its goals
        if self.list_manager.lists:
            first_list = next(iter(self.list_manager.lists.values()))
            self.select_list(first_list['id'])
        else:
            # No lists exist yet, update empty state
            self.update_empty_state()
    
    # Event handlers
    def on_about_clicked(self, button):
        """Handle about button click"""
        dialog = AboutDialog(self)
        dialog.connect('response', lambda d, r: d.destroy())
        dialog.present()

    def on_settings_clicked(self, button):
        """Handle settings button click"""
        dialog = SettingsDialog(self, self.settings)
        dialog.connect('response', lambda d, r: d.destroy())
        dialog.present()

    def on_add_goal_clicked(self, button):
        """Handle add goal button click"""
        dialog = GoalDialog(self, "Add New Goal", "")
        dialog.connect('response', self.on_add_goal_response)
        dialog.present()

    # Helper methods
    def create_empty_state(self):
            """Create the empty state message box"""
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            empty_box.set_valign(Gtk.Align.CENTER)
            empty_box.set_vexpand(True)
            empty_box.add_css_class('empty-state-box')
            
            empty_label = Gtk.Label()
            empty_label.set_markup("<span size='larger'>No goals yet!</span>")
            empty_label.add_css_class('empty-state-title')
            
            empty_description = Gtk.Label()
            empty_description.set_markup(
                "Click the 'Add Goal' button above to start tracking your goals"
            )
            empty_description.add_css_class('empty-state-description')
            
            empty_box.append(empty_label)
            empty_box.append(empty_description)
            
            return empty_box

    def create_initial_empty_state(self):
        """Create initial empty state when no lists exist"""
        empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        empty_box.set_valign(Gtk.Align.CENTER)
        empty_box.set_vexpand(True)
        empty_box.add_css_class('empty-state-box')
        
        empty_label = Gtk.Label()
        empty_label.set_markup("<span size='larger'>Welcome to Goal Tracker!</span>")
        empty_label.add_css_class('empty-state-title')
        
        empty_description = Gtk.Label()
        empty_description.set_markup(
            "Start by creating a new list using the '+' button in the sidebar"
        )
        empty_description.add_css_class('empty-state-description')
        
        empty_box.append(empty_label)
        empty_box.append(empty_description)
        
        return empty_box

    def update_empty_state(self):
            """Show or hide the empty state message based on goals count"""
            if not hasattr(self, 'current_list') or self.current_list is None:
                self.empty_state_box.set_visible(True)
                self.goals_header.set_visible(False)
                # Switch to initial empty state
                if hasattr(self, 'empty_state_box'):
                    parent = self.empty_state_box.get_parent()
                    if parent:
                        parent.remove(self.empty_state_box)
                    self.empty_state_box = self.create_initial_empty_state()
                    self.goals_container.append(self.empty_state_box)
            else:
                has_goals = len(self.goals) > 0
                self.empty_state_box.set_visible(not has_goals)
                self.goals_header.set_visible(has_goals)
                # Switch to regular empty state if needed
                if not has_goals and not any(widget for widget in self.empty_state_box if isinstance(widget, Gtk.Label) and widget.get_text() == "No goals yet!"):
                    parent = self.empty_state_box.get_parent()
                    if parent:
                        parent.remove(self.empty_state_box)
                    self.empty_state_box = self.create_empty_state()
                    self.goals_container.append(self.empty_state_box)

    def update_lists_sidebar(self):
        """Update the sidebar with current lists"""
        # Clear existing list items
        while True:
            row = self.lists_box.get_first_child()
            if row is None:
                break
            self.lists_box.remove(row)
        
        # Add list items
        for list_data in self.list_manager.lists.values():
            row = self.create_list_row(list_data)
            self.lists_box.append(row)
        
    def select_list(self, list_id):
        """Load and display the selected list's goals"""
        if list_id not in self.list_manager.lists:
            return
        
        self.current_list = self.list_manager.lists[list_id]
        self.goals = self.current_list['goals']
        
        # Update UI
        self.goals_title.set_text(f"{self.current_list['name']} goals:")
        self.clear_goals()
        self.load_goals()
        self.update_empty_state()
        self.add_goal_button.set_sensitive(True)

    def clear_goals(self):
        """Clear all goals from the display"""
        while True:
            child = self.goals_box.get_first_child()
            if child is None:
                break
            self.goals_box.remove(child)