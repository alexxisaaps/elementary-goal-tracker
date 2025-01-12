from datetime import datetime
from gi.repository import Gtk, Pango

from ..dialogs.goal_dialog import GoalDialog
from ..dialogs.confirm_dialog import ConfirmDialog
from .step import StepWidget

class GoalWidget(Gtk.Box):
    """Widget representing a goal with its steps"""
    
    def __init__(self, goal_data, parent_window, list_id):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.goal_data = goal_data
        self.parent_window = parent_window
        self.list_id = list_id

        self.build_ui()
        self.load_steps()

    def build_ui(self):
        """Build the main UI components of the goal widget"""
        # Goal row
        goal_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        goal_row.add_css_class('goal-row')
        self.append(goal_row)
        
        # Left side box (number, checkbox, title)
        left_box = self.create_left_box()
        goal_row.append(left_box)
        
        # Deadline label (if exists)
        if 'deadline' in self.goal_data and self.goal_data['deadline']:
            deadline_box = self.create_deadline_label(
                self.goal_data['deadline'],
                self.goal_data['completed']
            )
            goal_row.append(deadline_box)

        # Buttons
        button_box = self.create_button_box()
        goal_row.append(button_box)

        # Steps container
        self.steps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append(self.steps_box)

    def create_left_box(self):
        """Create the left side of the goal row with number, checkbox, and title"""
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        left_box.set_hexpand(True)

        # Number label
        self.number_label = Gtk.Label()
        self.number_label.add_css_class('goal-number')
        left_box.append(self.number_label)

        # Checkbox
        self.check = Gtk.CheckButton()
        self.check.set_active(self.goal_data['completed'])
        self.check.connect('toggled', self.on_goal_toggled)
        left_box.append(self.check)

        # Goal title
        label_box = self.create_label_box()
        left_box.append(label_box)

        return left_box

    def create_label_box(self):
        """Create the box containing the goal title label"""
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_box.set_hexpand(True)
        label_box.set_size_request(400, -1)

        self.label = Gtk.Label(label=self.goal_data['title'])
        self.label.add_css_class('goal-label')
        self.label.set_hexpand(True)
        self.label.set_xalign(0)
        self.label.set_wrap(True)
        self.label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label.set_size_request(400, -1)
        self.label.set_selectable(True)
        self.label.set_can_focus(True)
        self.update_label_style()
        label_box.append(self.label)

        return label_box

    def create_button_box(self):
        """Create the box containing action buttons"""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.add_css_class('button-box')

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

    def load_steps(self):
        """Load existing steps for this goal"""
        for step in self.goal_data.get('steps', []):
            self.add_step_widget(step)

    def add_step_widget(self, step_data):
        """Add a new step widget to the goal"""
        step_widget = StepWidget(step_data, self)
        self.steps_box.append(step_widget)
        self.update_step_numbers()
        self.parent_window.list_manager.save_lists()

    def update_label_style(self):
        """Update the label style based on completion status"""
        if self.goal_data['completed']:
            self.label.add_css_class('completed')
        else:
            self.label.remove_css_class('completed')

    def update_number(self, number):
        """Update the displayed number"""
        self.number_label.set_text(f"{number}.")

    def update_step_numbers(self):
        """Update the numbers for all steps"""
        for i, child in enumerate(self.steps_box):
            if isinstance(child, StepWidget):
                child.update_number(i + 1)

    # Event Handlers
    def on_goal_toggled(self, button):
        """Handle goal completion toggle"""
        self.goal_data['completed'] = button.get_active()
        self.update_label_style()
        
        # Update deadline display if it exists
        if 'deadline' in self.goal_data and self.goal_data['deadline']:
            goal_row = self.get_first_child()
            
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
            # Insert before the button box
            button_box = goal_row.get_last_child()
            goal_row.insert_child_after(deadline_box, button_box.get_prev_sibling())
        
        self.parent_window.handle_completion(self, is_goal=True)
        self.parent_window.list_manager.save_lists()

    def on_add_step_clicked(self, button):
        """Handle add step button click"""
        dialog = GoalDialog(self.parent_window, "Add Step", "")
        dialog.connect('response', self.on_add_step_response)
        dialog.present()

    def on_add_step_response(self, dialog, response):
        """Handle response from add step dialog"""
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
        """Handle edit button click"""
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
        """Handle response from edit dialog"""
        if response == Gtk.ResponseType.OK:
            new_text = dialog.entry.get_text()
            new_position = dialog.get_position()
            new_deadline = dialog.get_deadline()
            
            if new_text:
                # Update the goal data
                self.goal_data['title'] = new_text
                self.goal_data['deadline'] = new_deadline
                
                # Handle position change if needed
                if new_position is not None:
                    current_position = self.parent_window.goals.index(self.goal_data)
                    target_position = new_position - 1
                    
                    if target_position != current_position:
                        self.handle_position_change(current_position, target_position)
                
                # Update UI
                self.label.set_text(new_text)
                self.update_deadline_display()
                
                # Save changes
                self.parent_window.list_manager.save_lists()
                
        dialog.destroy()

    def handle_position_change(self, current_position, target_position):
        """Handle changing the position of the goal in the list"""
        # Remove from current position
        self.parent_window.goals.pop(current_position)
        
        # Insert at new position
        self.parent_window.goals.insert(target_position, self.goal_data)
        
        # Update widget position
        parent = self.get_parent()
        if parent:
            parent.remove(self)
            
            if target_position == 0:
                parent.prepend(self)
            else:
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

    def update_deadline_display(self):
        """Update the deadline display in the UI"""
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

    def on_delete_clicked(self, button):
        """Handle delete button click"""
        dialog = ConfirmDialog(
            self.parent_window,
            "Delete Goal",
            f"Are you sure you want to delete the goal '{self.goal_data['title']}' and all its steps?"
        )
        dialog.connect('response', self.on_delete_confirmed)
        dialog.present()

    def on_delete_confirmed(self, dialog, response):
        """Handle confirmation of goal deletion"""
        if response == Gtk.ResponseType.OK:
            self.parent_window.remove_goal(self)
        dialog.destroy()