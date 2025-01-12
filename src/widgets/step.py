from datetime import datetime
from gi.repository import Gtk, Pango

from ..dialogs.goal_dialog import GoalDialog
from ..dialogs.confirm_dialog import ConfirmDialog

class StepWidget(Gtk.Box):
    """Widget representing a step within a goal"""
    
    def __init__(self, step_data, parent_goal):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.step_data = step_data
        self.parent_goal = parent_goal
        self.add_css_class('step-row')

        self.build_ui()

    def build_ui(self):
        """Build the main UI components of the step widget"""
        # Left side box (number, checkbox, text)
        left_box = self.create_left_box()
        self.append(left_box)

        # Deadline label (if exists)
        if 'deadline' in self.step_data and self.step_data['deadline']:
            deadline_box = self.create_deadline_label(
                self.step_data['deadline'],
                self.step_data['completed']
            )
            self.append(deadline_box)

        # Buttons
        button_box = self.create_button_box()
        self.append(button_box)

    def create_left_box(self):
        """Create the left side of the step row with number, checkbox, and text"""
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        left_box.set_hexpand(True)

        # Number label
        self.number_label = Gtk.Label()
        self.number_label.add_css_class('step-number')
        left_box.append(self.number_label)

        # Checkbox
        self.check = Gtk.CheckButton()
        self.check.set_active(self.step_data['completed'])
        self.check.connect('toggled', self.on_step_toggled)
        left_box.append(self.check)

        # Step text
        label_box = self.create_label_box()
        left_box.append(label_box)

        return left_box

    def create_label_box(self):
        """Create the box containing the step text label"""
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_box.set_hexpand(True)
        label_box.set_size_request(400, -1)

        self.label = Gtk.Label(label=self.step_data['text'])
        self.label.add_css_class('step-label')
        self.label.set_hexpand(True)
        self.label.set_xalign(0)
        self.label.set_wrap(True)
        self.label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label.set_size_request(400, -1)
        self.update_label_style()
        label_box.append(self.label)

        return label_box

    def create_button_box(self):
        """Create the box containing action buttons"""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.add_css_class('button-box')

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

        return button_box

    def create_deadline_label(self, deadline_date_str, is_completed=False):
        """Create a deadline label with appropriate styling"""
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

    def update_label_style(self):
        """Update the label style based on completion status"""
        if self.step_data['completed']:
            self.label.add_css_class('completed')
        else:
            self.label.remove_css_class('completed')

    def update_number(self, number):
        """Update the displayed number"""
        self.number_label.set_text(f"{number}.")

    def update_deadline_display(self):
        """Update the deadline display in the UI"""
        # Find and remove old deadline box
        child = self.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            if isinstance(child, Gtk.Box) and 'deadline-box' in child.get_css_classes():
                self.remove(child)
                break
            child = next_child
        
        # Add new deadline box if deadline exists
        if 'deadline' in self.step_data and self.step_data['deadline']:
            deadline_box = self.create_deadline_label(
                self.step_data['deadline'],
                self.step_data['completed']
            )
            button_box = self.get_last_child()
            self.insert_child_after(deadline_box, button_box.get_prev_sibling())

    # Event Handlers
    def on_step_toggled(self, button):
        """Handle step completion toggle"""
        self.step_data['completed'] = button.get_active()
        self.update_label_style()
        self.update_deadline_display()
        
        self.parent_goal.parent_window.handle_completion(self, is_goal=False)
        self.parent_goal.parent_window.list_manager.save_lists()

    def on_edit_clicked(self, button):
        """Handle edit button click"""
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
        """Handle response from edit dialog"""
        if response == Gtk.ResponseType.OK:
            new_text = dialog.entry.get_text()
            new_position = dialog.get_position()
            new_deadline = dialog.get_deadline()
            
            if new_text:
                self.step_data['text'] = new_text
                self.step_data['deadline'] = new_deadline
                
                parent = self.get_parent()
                if parent:
                    parent.remove(self)
                    new_widget = StepWidget(self.step_data, self.parent_goal)
                    parent.append(new_widget)
                    
                    if new_position:
                        current_position = self.parent_goal.goal_data['steps'].index(self.step_data)
                        target_position = new_position - 1
                        
                        if current_position != target_position:
                            self.handle_position_change(current_position, target_position, new_widget)
                    
                    # Update numbers for all steps
                    self.parent_goal.update_step_numbers()
                    
                self.parent_goal.parent_window.list_manager.save_lists()
        dialog.destroy()

    def handle_position_change(self, current_position, target_position, widget):
        """Handle changing the position of the step in the list"""
        steps = self.parent_goal.goal_data['steps']
        parent = widget.get_parent()
        
        # Update data
        steps.pop(current_position)
        steps.insert(target_position, self.step_data)
        
        # Update UI
        parent.remove(widget)
        
        if target_position == 0:
            parent.prepend(widget)
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
                parent.insert_child_after(widget, prev_widget)
            else:
                parent.append(widget)

    def on_delete_clicked(self, button):
        """Handle delete button click"""
        dialog = ConfirmDialog(
            self.parent_goal.parent_window,
            "Delete Step",
            "Are you sure you want to delete this step?"
        )
        dialog.connect('response', self.on_delete_confirmed)
        dialog.present()

    def on_delete_confirmed(self, dialog, response):
        """Handle confirmation of step deletion"""
        if response == Gtk.ResponseType.OK:
            self.parent_goal.goal_data['steps'].remove(self.step_data)
            self.parent_goal.steps_box.remove(self)
            self.parent_goal.parent_window.list_manager.save_lists()
            self.parent_goal.update_step_numbers()
        dialog.destroy()