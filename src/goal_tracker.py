#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Granite', '7.0')
from gi.repository import Gtk, GLib, GObject, Gdk, Pango, Adw, Gio, Granite
import json
import os
import sys
import shutil
import random
from datetime import datetime

APP_NAME = "Goal Tracker"
APP_VERSION = "1.1.0"

class GoalWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.settings = Settings()
        self.daily_quote = DailyQuote()
        self.list_manager = ListManager()

        # Set up window properties
        self.set_title(f"{APP_NAME} - {APP_VERSION}")
        self.set_default_size(1100, 600)
        self.set_size_request(800, 400)
        
        # Create main layout box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_size_request(800, -1)
        self.set_content(main_box)
        
        # HeaderBar
        header_bar = Adw.HeaderBar()
        main_box.append(header_bar)
        
        # Buttons setup
        about_button = Gtk.Button(label="About")
        about_button.add_css_class('help-button')
        about_button.connect('clicked', self.on_about_clicked)
        header_bar.pack_start(about_button)
        
        # Settings button
        settings_button = Gtk.Button(label="⚙️")
        settings_button.add_css_class('help-button')
        settings_button.connect('clicked', self.on_settings_clicked)
        header_bar.pack_start(settings_button)
        
        # Add goal button - Make it a class attribute
        self.add_goal_button = Gtk.Button(label="Add Goal")
        self.add_goal_button.add_css_class('suggested-action')
        self.add_goal_button.connect('clicked', self.on_add_goal_clicked)
        self.add_goal_button.set_sensitive(False)  # Initially disabled
        header_bar.pack_end(self.add_goal_button)
        
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
        
        self.goals_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.goals_container.append(self.goals_box)
        
        # Empty state message
        self.empty_state_box = self.create_empty_state()
        self.goals_container.append(self.empty_state_box)
        
        # Initialize goals list
        self.goals = []
        
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
        
    def create_empty_state(self):
        """Create the empty state message box"""
        empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        empty_box.set_valign(Gtk.Align.CENTER)
        empty_box.set_vexpand(True)
        
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
                if self.current_list['id'] == list_id:
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
    
    def update_empty_state(self):
        """Show or hide the empty state message and goals header based on goals count"""
        has_goals = len(self.goals) > 0
        self.empty_state_box.set_visible(not has_goals)
        self.goals_header.set_visible(has_goals)
    
    def on_about_clicked(self, button):
        dialog = AboutDialog(self)
        dialog.connect('response', lambda d, r: d.destroy())
        dialog.present()

    def on_settings_clicked(self, button):
        dialog = SettingsDialog(self, self.settings)
        dialog.connect('response', lambda d, r: d.destroy())
        dialog.present()

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

    def on_add_goal_clicked(self, button):
        dialog = GoalDialog(self, "Add New Goal", "")
        dialog.connect('response', self.on_add_goal_response)
        dialog.present()

    def on_add_goal_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            goal_text = dialog.entry.get_text()
            if goal_text:
                self.add_goal({'title': goal_text, 'completed': False, 'steps': []})
        dialog.destroy()

    def update_empty_state(self):
        """Show or hide the empty state message based on goals count"""
        if len(self.goals) == 0:
            self.empty_state_box.set_visible(True)
        else:
            self.empty_state_box.set_visible(False)
    
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

    def remove_goal(self, goal_widget):
        """Remove a goal from the current list"""
        self.goals.remove(goal_widget.goal_data)
        self.list_manager.save_lists()
        self.goals_box.remove(goal_widget)
        self.update_empty_state()
        self.update_goal_numbers()

    def save_goals(self):
        with open('goals.json', 'w') as f:
            json.dump(self.goals, f)

    def load_goals(self):
        """Load goals for the current list"""
        if not hasattr(self, 'current_list'):
            return
            
        for goal_data in self.goals:
            self.goals_box.append(GoalWidget(goal_data, self, self.current_list['id']))
        self.update_goal_numbers()
    
    def update_goal_numbers(self):
        """Update the display numbers for all goals"""
        for i, child in enumerate(self.goals_box):
            if isinstance(child, GoalWidget):
                child.update_number(i + 1)

class ListManager:
    def __init__(self):
        self.data_dir = os.path.join(GLib.get_user_data_dir(), 'goaltracker')
        os.makedirs(self.data_dir, exist_ok=True)
        self.lists_file = os.path.join(self.data_dir, 'lists.json')
        self.lists = {}
        
    def generate_id(self):
        """Generate a unique ID for a new list"""
        return str(random.randint(10000, 99999))
        
    def load_lists(self):
        """Load lists from file"""
        try:
            with open(self.lists_file, 'r') as f:
                self.lists = json.load(f)
        except FileNotFoundError:
            self.lists = {}
            
    def save_lists(self):
        """Save lists to file"""
        with open(self.lists_file, 'w') as f:
            json.dump(self.lists, f)
            
    def add_list(self, name):
        """Add a new list"""
        list_id = self.generate_id()
        self.lists[list_id] = {
            'id': list_id,
            'name': name,
            'goals': []
        }
        self.save_lists()
        return list_id
        
    def edit_list(self, list_id, new_name):
        """Edit an existing list"""
        if list_id in self.lists:
            self.lists[list_id]['name'] = new_name
            self.save_lists()
            
    def delete_list(self, list_id):
        """Delete a list"""
        if list_id in self.lists:
            del self.lists[list_id]
            self.save_lists()

    def save_goals_for_list(self, list_id):
        """Save goals for a specific list"""
        if list_id in self.lists:
            self.save_lists()

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
        
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_response, Gtk.ResponseType.CANCEL)
        header_bar.pack_start(cancel_button)
        
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
        self.emit("response", response)

class GoalWidget(Gtk.Box):
    def __init__(self, goal_data, parent_window, list_id):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.goal_data = goal_data
        self.parent_window = parent_window
        self.list_id = list_id

        # Goal row
        goal_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        goal_row.add_css_class('goal-row')
        self.append(goal_row)
        
        # Left side box (number, checkbox, title)
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        left_box.set_hexpand(True)
        goal_row.append(left_box)

        # Number label
        self.number_label = Gtk.Label()
        self.number_label.add_css_class('goal-number')
        left_box.append(self.number_label)

        # Checkbox
        self.check = Gtk.CheckButton()
        self.check.set_active(goal_data['completed'])
        self.check.connect('toggled', self.on_goal_toggled)
        left_box.append(self.check)

        # Goal title
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_box.set_hexpand(True)
        label_box.set_size_request(400, -1)

        self.label = Gtk.Label(label=goal_data['title'])
        self.label.add_css_class('goal-label')
        self.label.set_hexpand(True)
        self.label.set_xalign(0)
        self.label.set_wrap(True)
        self.label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label.set_size_request(400, -1)
        self.update_label_style()
        label_box.append(self.label)

        left_box.append(label_box)
        
        # Deadline label (if exists)
        if 'deadline' in goal_data and goal_data['deadline']:
            deadline_box = self.create_deadline_label(
                goal_data['deadline'],
                goal_data['completed']
            )
            goal_row.append(deadline_box)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.add_css_class('button-box')
        goal_row.append(button_box)

        add_step_button = Gtk.Button(label="Add Step")
        add_step_button.add_css_class('action-button')
        add_step_button.add_css_class('edit-button')
        add_step_button.connect('clicked', self.on_add_step_clicked)
        button_box.append(add_step_button)

        edit_button = Gtk.Button(label="Edit")
        edit_button.add_css_class('action-button')
        edit_button.add_css_class('edit-button')
        edit_button.connect('clicked', self.on_edit_clicked)
        button_box.append(edit_button)

        delete_button = Gtk.Button(label="Delete")
        delete_button.add_css_class('action-button')
        delete_button.add_css_class('delete-button')
        delete_button.connect('clicked', self.on_delete_clicked)
        button_box.append(delete_button)

        # Steps container
        self.steps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append(self.steps_box)

        # Load existing steps
        for step in goal_data.get('steps', []):
            self.add_step_widget(step)

    def add_step_widget(self, step_data):
        step_widget = StepWidget(step_data, self)
        self.steps_box.append(step_widget)
        self.update_step_numbers()
        self.parent_window.list_manager.save_lists()

    def update_label_style(self):
        if self.goal_data['completed']:
            self.label.add_css_class('completed')
        else:
            self.label.remove_css_class('completed')

    def create_deadline_label(self, deadline_date_str, is_completed=False):
        deadline_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        deadline_box.add_css_class('deadline-box')
        
        if is_completed:
            deadline_label = Gtk.Label(label="✓ Completed")
            deadline_label.add_css_class('deadline-label')
            deadline_label.add_css_class('deadline-completed')
        else:
            deadline_date = datetime.strptime(deadline_date_str, "%Y-%m-%d").date()
            days_left = (deadline_date - datetime.now().date()).days
            
            if days_left < 0:
                css_class = 'deadline-overdue'
                deadline_text = f"🕒 {abs(days_left)}d overdue"
            elif days_left == 0:
                css_class = 'deadline-today'
                deadline_text = "Due today"
            else:
                css_class = 'deadline-upcoming'
                deadline_text = f"🕒 {days_left}d left"
                
            deadline_label = Gtk.Label(label=deadline_text)
            deadline_label.add_css_class('deadline-label')
            deadline_label.add_css_class(css_class)
        
        deadline_box.append(deadline_label)
        return deadline_box

    def on_goal_toggled(self, button):
        self.goal_data['completed'] = button.get_active()
        self.update_label_style()
        
        # Update deadline display if it exists
        if 'deadline' in self.goal_data and self.goal_data['deadline']:
            goal_row = self.get_first_child()  # This is the horizontal box containing everything
            
            # Find and remove old deadline box
            child = goal_row.get_first_child()
            while child is not None:
                next_child = child.get_next_sibling()
                if isinstance(child, Gtk.Box) and 'deadline-box' in child.get_css_classes():
                    goal_row.remove(child)
                    break
                child = next_child
            
            # Add new deadline box
            deadline_box = self.create_deadline_label(
                self.goal_data['deadline'], 
                self.goal_data['completed']
            )
            # Insert before the button box (which is the last child)
            button_box = goal_row.get_last_child()
            goal_row.insert_child_after(deadline_box, button_box.get_prev_sibling())
        
        self.parent_window.handle_completion(self, is_goal=True)
        self.parent_window.list_manager.save_lists()

    def on_add_step_clicked(self, button):
        dialog = GoalDialog(self.parent_window, "Add Step", "")
        dialog.connect('response', self.on_add_step_response)
        dialog.present()

    def on_add_step_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            step_text = dialog.entry.get_text()
            step_deadline = dialog.get_deadline()
            if step_text:
                step_data = {
                    'text': step_text, 
                    'completed': False,
                    'deadline': step_deadline
                }
                if 'steps' not in self.goal_data:
                    self.goal_data['steps'] = []
                self.goal_data['steps'].append(step_data)
                self.add_step_widget(step_data)
                self.parent_window.list_manager.save_lists()
        dialog.destroy()

    def on_edit_clicked(self, button):
        # Get current position (1-based index)
        current_position = self.parent_window.goals.index(self.goal_data) + 1
        max_position = len(self.parent_window.goals)
        
        dialog = GoalDialog(
            self.parent_window,
            "Edit Goal",
            self.goal_data['title'],
            is_step=False,
            current_position=current_position,
            max_position=max_position
        )
        dialog.connect('response', self.on_edit_response)
        dialog.present()

    def on_edit_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            new_text = dialog.entry.get_text()
            new_position = dialog.get_position()
            new_deadline = dialog.get_deadline()
            
            if new_text:
                # Store current position before any changes
                current_position = self.parent_window.goals.index(self.goal_data)
                
                # Update the goal data
                self.goal_data['title'] = new_text
                self.goal_data['deadline'] = new_deadline
                
                # Only handle position change if it's different from current
                if new_position and (new_position - 1) != current_position:
                    target_position = new_position - 1  # Convert to 0-based index
                    
                    # Remove from current position in data
                    self.parent_window.goals.pop(current_position)
                    # Insert at new position in data
                    self.parent_window.goals.insert(target_position, self.goal_data)
                    
                    # Handle widget reordering
                    parent = self.get_parent()
                    if parent:
                        parent.remove(self)  # Remove widget from current position
                        
                        # Reinsert at correct position
                        if target_position == 0:
                            parent.prepend(self)
                        else:
                            # Find the widget that should be before our target position
                            widget_count = 0
                            prev_widget = None
                            for child in parent:
                                if isinstance(child, GoalWidget):
                                    if widget_count == target_position - 1:
                                        prev_widget = child
                                        break
                                    widget_count += 1
                            
                            if prev_widget:
                                parent.insert_child_after(self, prev_widget)
                            else:
                                parent.append(self)
                
                # Update the label text
                self.label.set_text(new_text)
                
                # Update deadline display
                if 'deadline' in self.goal_data and self.goal_data['deadline']:
                    goal_row = self.get_first_child()
                    
                    # Remove old deadline box if exists
                    child = goal_row.get_first_child()
                    while child:
                        next_child = child.get_next_sibling()
                        if isinstance(child, Gtk.Box) and 'deadline-box' in child.get_css_classes():
                            goal_row.remove(child)
                            break
                        child = next_child
                    
                    # Add new deadline box
                    deadline_box = self.create_deadline_label(
                        self.goal_data['deadline'],
                        self.goal_data['completed']
                    )
                    button_box = goal_row.get_last_child()
                    goal_row.insert_child_after(deadline_box, button_box.get_prev_sibling())
                
                # Update all goal numbers
                self.parent_window.update_goal_numbers()
                
                # Save changes
                self.parent_window.list_manager.save_lists()
                
        dialog.destroy()

    def on_delete_clicked(self, button):
        dialog = ConfirmDialog(
            self.parent_window,
            "Delete Goal",
            f"Are you sure you want to delete the goal '{self.goal_data['title']}' and all its steps?"
        )
        dialog.connect('response', self.on_delete_confirmed)
        dialog.present()

    def on_delete_confirmed(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.parent_window.remove_goal(self)
        dialog.destroy()
        
    def update_number(self, number):
        """Update the displayed number"""
        self.number_label.set_text(f"{number}.")

    def update_step_numbers(self):
        """Update the numbers for all steps"""
        for i, child in enumerate(self.steps_box):
            if isinstance(child, StepWidget):
                child.update_number(i + 1)

class StepWidget(Gtk.Box):
    def __init__(self, step_data, parent_goal):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.step_data = step_data
        self.parent_goal = parent_goal
        self.add_css_class('step-row')

        # Left side box (number, checkbox, text)
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        left_box.set_hexpand(True)
        self.append(left_box)

        # Number label
        self.number_label = Gtk.Label()
        self.number_label.add_css_class('step-number')
        left_box.append(self.number_label)

        # Checkbox
        self.check = Gtk.CheckButton()
        self.check.set_active(step_data['completed'])
        self.check.connect('toggled', self.on_step_toggled)
        left_box.append(self.check)

        # Step text
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_box.set_hexpand(True)
        label_box.set_size_request(400, -1)

        self.label = Gtk.Label(label=step_data['text'])
        self.label.add_css_class('step-label')
        self.label.set_hexpand(True)
        self.label.set_xalign(0)
        self.label.set_wrap(True)
        self.label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label.set_size_request(400, -1)
        self.update_label_style()
        label_box.append(self.label)

        left_box.append(label_box)

        # Deadline label (if exists)
        if 'deadline' in step_data and step_data['deadline']:
            deadline_box = self.create_deadline_label(
                step_data['deadline'],
                step_data['completed']
            )
            self.append(deadline_box)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.add_css_class('button-box')
        self.append(button_box)

        edit_button = Gtk.Button(label="Edit")
        edit_button.add_css_class('action-button')
        edit_button.add_css_class('edit-button')
        edit_button.connect('clicked', self.on_edit_clicked)
        button_box.append(edit_button)

        delete_button = Gtk.Button(label="Delete")
        delete_button.add_css_class('action-button')
        delete_button.add_css_class('delete-button')
        delete_button.connect('clicked', self.on_delete_clicked)
        button_box.append(delete_button)

    def update_number(self, number):
        """Update the displayed number"""
        self.number_label.set_text(f"{number}.")

    def update_label_style(self):
        if self.step_data['completed']:
            self.label.add_css_class('completed')
        else:
            self.label.remove_css_class('completed')

    def create_deadline_label(self, deadline_date_str, is_completed=False):
        deadline_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        deadline_box.add_css_class('deadline-box')
        
        if is_completed:
            deadline_label = Gtk.Label(label="✓ Completed")
            deadline_label.add_css_class('deadline-label')
            deadline_label.add_css_class('deadline-completed')
        else:
            deadline_date = datetime.strptime(deadline_date_str, "%Y-%m-%d").date()
            days_left = (deadline_date - datetime.now().date()).days
            
            if days_left < 0:
                css_class = 'deadline-overdue'
                deadline_text = f"🕒 {abs(days_left)}d overdue"
            elif days_left == 0:
                css_class = 'deadline-today'
                deadline_text = "Due today"
            else:
                css_class = 'deadline-upcoming'
                deadline_text = f"🕒 {days_left}d left"
                
            deadline_label = Gtk.Label(label=deadline_text)
            deadline_label.add_css_class('deadline-label')
            deadline_label.add_css_class(css_class)
        
        deadline_box.append(deadline_label)
        return deadline_box

    def on_step_toggled(self, button):
        self.step_data['completed'] = button.get_active()
        self.update_label_style()
        
        # Update deadline display if it exists
        if 'deadline' in self.step_data and self.step_data['deadline']:
            # Find and remove old deadline box
            child = self.get_first_child()
            while child is not None:
                next_child = child.get_next_sibling()
                if isinstance(child, Gtk.Box) and 'deadline-box' in child.get_css_classes():
                    self.remove(child)
                    break
                child = next_child
            
            # Add new deadline box
            deadline_box = self.create_deadline_label(
                self.step_data['deadline'], 
                self.step_data['completed']
            )
            
            # Insert before the button box
            button_box = self.get_last_child()
            self.insert_child_after(deadline_box, button_box.get_prev_sibling())
        
        self.parent_goal.parent_window.handle_completion(self, is_goal=False)
        self.parent_goal.parent_window.list_manager.save_lists()

    def on_edit_clicked(self, button):
        current_position = self.parent_goal.goal_data['steps'].index(self.step_data) + 1
        max_position = len(self.parent_goal.goal_data['steps'])
        
        dialog = GoalDialog(
            self.parent_goal.parent_window,
            "Edit Step",
            self.step_data['text'],
            is_step=True,
            current_position=current_position,
            max_position=max_position,
            current_deadline=self.step_data.get('deadline')
        )
        dialog.connect('response', self.on_edit_response)
        dialog.present()

    def on_edit_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            new_text = dialog.entry.get_text()
            new_position = dialog.get_position()
            new_deadline = dialog.get_deadline()
            
            if new_text:
                self.step_data['text'] = new_text
                self.step_data['deadline'] = new_deadline
                self.label.set_text(new_text)
                
                parent = self.get_parent()
                if parent:
                    parent.remove(self)
                    new_widget = StepWidget(self.step_data, self.parent_goal)
                    parent.append(new_widget)
                    
                    if new_position:
                        current_position = self.parent_goal.goal_data['steps'].index(self.step_data)
                        target_position = new_position - 1
                        
                        if current_position != target_position:
                            self.parent_goal.goal_data['steps'].pop(current_position)
                            self.parent_goal.goal_data['steps'].insert(target_position, self.step_data)
                            
                            parent.remove(new_widget)
                            
                            if target_position == 0:
                                parent.prepend(new_widget)
                            else:
                                prev_widget = None
                                widget_count = 0
                                for child in parent:
                                    if isinstance(child, StepWidget):
                                        if widget_count == target_position - 1:
                                            prev_widget = child
                                            break
                                        widget_count += 1
                                        
                                if prev_widget:
                                    parent.insert_child_after(new_widget, prev_widget)
                                else:
                                    parent.append(new_widget)
                    
                    # Update numbers for all steps
                    self.parent_goal.update_step_numbers()
                    
                self.parent_goal.parent_window.list_manager.save_lists()
        dialog.destroy()

    def on_delete_clicked(self, button):
        dialog = ConfirmDialog(
            self.parent_goal.parent_window,
            "Delete Step",
            f"Are you sure you want to delete this step?"
        )
        dialog.connect('response', self.on_delete_confirmed)
        dialog.present()

    def on_delete_confirmed(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.parent_goal.goal_data['steps'].remove(self.step_data)
            self.parent_goal.steps_box.remove(self)
            self.parent_goal.parent_window.list_manager.save_lists()
            self.parent_goal.update_step_numbers()
        dialog.destroy()

class GoalDialog(Gtk.Dialog):
    def __init__(self, parent, title, current_text="", is_step=False, current_position=None, max_position=None, current_deadline=None):
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
        
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_response, Gtk.ResponseType.CANCEL)
        header_bar.pack_start(cancel_button)
        
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
            
        self.entry.connect('activate', self._on_entry_activate)

    def _on_deadline_switch_toggled(self, switch, param):
        self.calendar.set_sensitive(switch.get_active())

    def get_deadline(self):
        if not self.deadline_switch.get_active():
            return None
            
        date = self.calendar.get_date()
        return date.format("%Y-%m-%d")

    def _on_entry_activate(self, entry):
        self.emit('response', Gtk.ResponseType.OK)

    def _on_response(self, button, response):
        self.emit("response", response)
        
    def get_position(self):
        if self.position_spin:
            return self.position_spin.get_value_as_int()
        return None
        
class DailyQuote:
    def __init__(self):
        self.data_dir = os.path.join(GLib.get_user_data_dir(), 'goaltracker')
        os.makedirs(self.data_dir, exist_ok=True)
        self.quotes_file = os.path.join(self.data_dir, 'quotes.json')
        self.current_quote = None
        self.last_date = None
        
    def load_quotes(self):
        """Load quotes from the system or user directory."""
        # Try user directory first
        user_quotes = os.path.join(GLib.get_user_data_dir(), 'goaltracker', 'quotes.json')
        # System directory as fallback
        system_quotes = os.path.join(GLib.get_system_data_dirs()[0], 'goaltracker', 'quotes.json')
        
        # Default quote in case everything fails
        default_quotes = {
            "quotes": [
                {
                    "text": "Set your goals high and don't stop till you get there.",
                    "author": "Bo Jackson"
                }
            ]
        }

        try:
            # Try user directory first
            if os.path.exists(user_quotes):
                with open(user_quotes, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data['quotes']
            # Try system directory next
            elif os.path.exists(system_quotes):
                with open(system_quotes, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data['quotes']
            else:
                print("No quotes file found, using default quote")
                return default_quotes['quotes']
        except Exception as e:
            print(f"Error loading quotes: {e}")
            return default_quotes['quotes']
    
    def get_daily_quote(self):
        today = datetime.now().date()
        
        if self.last_date != today or self.current_quote is None:
            quotes_list = self.load_quotes()
            if not quotes_list:  # If quotes list is empty
                quotes_list = [{
                    "text": "Set your goals high and don't stop till you get there.",
                    "author": "Bo Jackson"
                }]
            
            # Use the date as a seed to get the same quote throughout the day
            random.seed(today.strftime("%Y%m%d"))
            self.current_quote = random.choice(quotes_list)
            self.last_date = today
            
        return self.current_quote

class ConfirmDialog(Gtk.Dialog):
    def __init__(self, parent, title, message):
        super().__init__(
            title=title,
            transient_for=parent,
            modal=True,
            destroy_with_parent=True
        )
        
        self.set_deletable(False)

        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        self.set_titlebar(header_bar)
        
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_response, Gtk.ResponseType.CANCEL)
        header_bar.pack_start(cancel_button)
        
        delete_button = Gtk.Button(label="Delete")
        delete_button.add_css_class('delete-button')
        delete_button.connect("clicked", self._on_response, Gtk.ResponseType.OK)
        header_bar.pack_end(delete_button)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        self.set_child(box)
        
        label = Gtk.Label(label=message)
        label.set_wrap(True)
        label.set_max_width_chars(40)
        box.append(label)

    def _on_response(self, button, response):
        self.emit("response", response)

class Settings:
    def __init__(self):
        self.data_dir = os.path.join(GLib.get_user_data_dir(), 'goaltracker')
        os.makedirs(self.data_dir, exist_ok=True)
        self.settings_file = os.path.join(self.data_dir, 'settings.json')
        self.default_settings = {
            'auto_sort_items': False
        }
        self.current_settings = self.load_settings()
    
    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.default_settings.copy()
    
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.current_settings, f)
    
    def get(self, key):
        return self.current_settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        self.current_settings[key] = value
        self.save_settings()

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent, settings):
        super().__init__(
            title="Settings",
            transient_for=parent,
            modal=True,
            destroy_with_parent=True
        )

        self.settings = settings
        self.set_default_size(400, -1)
        
        # Header Bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(False)
        self.set_titlebar(header_bar)
        
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self._on_response, Gtk.ResponseType.OK)
        header_bar.pack_end(close_button)
        
        # Content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        self.set_child(box)
        
        # Auto-sort setting
        auto_sort_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        auto_sort_box.add_css_class('setting-row')
        box.append(auto_sort_box)
        
        # Left side with checkbox and title
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        left_box.set_hexpand(True)
        auto_sort_box.append(left_box)
        
        self.auto_sort_check = Gtk.CheckButton()
        self.auto_sort_check.set_active(self.settings.get('auto_sort_items'))
        self.auto_sort_check.connect('toggled', self._on_auto_sort_toggled)
        left_box.append(self.auto_sort_check)
        
        labels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        left_box.append(labels_box)
        
        title_label = Gtk.Label(label="Auto-sort Items")
        title_label.add_css_class('setting-title')
        title_label.set_halign(Gtk.Align.START)
        labels_box.append(title_label)
        
        description_label = Gtk.Label(
            label="When a goal or step is marked as completed, it will move to " +
                  "the bottom of the list. New items will be added before completed ones."
        )
        description_label.add_css_class('setting-description')
        description_label.set_wrap(True)
        description_label.set_xalign(0)
        labels_box.append(description_label)
        
        # Make the entire row clickable
        gesture = Gtk.GestureClick()
        gesture.connect('released', self._on_row_clicked)
        auto_sort_box.add_controller(gesture)
    
    def _on_auto_sort_toggled(self, button):
        self.settings.set('auto_sort_items', button.get_active())
    
    def _on_row_clicked(self, gesture, n_press, x, y):
        self.auto_sort_check.set_active(not self.auto_sort_check.get_active())
    
    def _on_response(self, button, response):
        self.emit("response", response)

class AboutDialog(Gtk.Dialog):
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
        launcher = Gtk.UriLauncher.new(url)
        launcher.launch(self, None, self._on_launch_finished)

    def _on_launch_finished(self, source, result):
        try:
            source.launch_finish(result)
        except GLib.Error as e:
            print(f"Error opening URL: {e.message}")
    
    def on_donate_clicked(self, button):
        url = "#"
        self.open_url(url)

    def _on_response(self, button, response):
        self.emit("response", response)

    def create_section(self, title, items):
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
        
class GoalApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='io.github.alexxisaapps.elementary_goal_tracker',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
        GLib.set_application_name("Goal Tracker")
        
    def do_startup(self):
        # Initialize Granite
        Granite.init()
        
        # Initialize parent
        Adw.Application.do_startup(self)
        
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
        win = self.get_active_window()
        if not win:
            win = GoalWindow(application=self)
        win.present()

def main():
    try:
        # Set up user data directory using GLib
        app_name = "goaltracker"
        user_data_dir = os.path.join(GLib.get_user_data_dir(), app_name)
        user_cache_dir = os.path.join(GLib.get_user_cache_dir(), app_name)
        user_config_dir = os.path.join(GLib.get_user_config_dir(), app_name)
        
        # Create necessary directories
        os.makedirs(user_data_dir, exist_ok=True)
        os.makedirs(user_cache_dir, exist_ok=True)
        os.makedirs(user_config_dir, exist_ok=True)
        
        # Change to user data directory for file operations
        os.chdir(user_data_dir)
        
        # System installed quotes file (using first system data dir)
        system_data_dir = GLib.get_system_data_dirs()[0]
        system_quotes = os.path.join(system_data_dir, 'goaltracker', 'quotes.json')
        user_quotes = os.path.join(user_data_dir, 'quotes.json')
        
        # Create initial files if they don't exist
        default_files = {
            'lists.json': '{}',
            'settings.json': '{"auto_sort_items": false}'
        }
        
        for filename, default_content in default_files.items():
            filepath = os.path.join(user_data_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(default_content)
                os.chmod(filepath, 0o644)
        
        # Copy system quotes to user directory if it doesn't exist
        if not os.path.exists(user_quotes) and os.path.exists(system_quotes):
            shutil.copy2(system_quotes, user_quotes)
            os.chmod(user_quotes, 0o644)
        
        # Initialize app
        app = GoalApplication()
        return app.run(sys.argv)
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Fatal error: {error_msg}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    main()