import os
import json
import random
from gi.repository import GLib

class ListManager:
    """Service for managing goal lists"""
    
    def __init__(self):
        self.data_dir = os.path.join(GLib.get_user_data_dir(), 'goaltracker')
        os.makedirs(self.data_dir, exist_ok=True)
        self.lists_file = os.path.join(self.data_dir, 'lists.json')
        self.lists = {}
        
    def generate_id(self):
        """Generate a unique ID for a new list"""
        while True:
            new_id = str(random.randint(10000, 99999))
            if new_id not in self.lists:
                return new_id
        
    def load_lists(self):
        """Load lists from file"""
        try:
            with open(self.lists_file, 'r') as f:
                self.lists = json.load(f)
        except FileNotFoundError:
            self.lists = {}
            self.save_lists()
        except json.JSONDecodeError:
            print("Lists file corrupted, creating new file")
            self.lists = {}
            self.save_lists()
            
    def save_lists(self):
        """Save lists to file"""
        try:
            with open(self.lists_file, 'w') as f:
                json.dump(self.lists, f, indent=2)
        except Exception as e:
            print(f"Error saving lists: {e}")
            
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
    
    def get_list(self, list_id):
        """Get a specific list by ID"""
        return self.lists.get(list_id)
    
    def get_all_lists(self):
        """Get all lists"""
        return self.lists
    
    def add_goal_to_list(self, list_id, goal_data):
        """Add a goal to a specific list"""
        if list_id in self.lists:
            self.lists[list_id]['goals'].append(goal_data)
            self.save_lists()
            
    def update_goal_in_list(self, list_id, goal_index, goal_data):
        """Update a goal in a specific list"""
        if list_id in self.lists and 0 <= goal_index < len(self.lists[list_id]['goals']):
            self.lists[list_id]['goals'][goal_index] = goal_data
            self.save_lists()
            
    def remove_goal_from_list(self, list_id, goal_index):
        """Remove a goal from a specific list"""
        if list_id in self.lists and 0 <= goal_index < len(self.lists[list_id]['goals']):
            self.lists[list_id]['goals'].pop(goal_index)
            self.save_lists()
    
    def move_goal(self, list_id, old_index, new_index):
        """Move a goal to a new position in the list"""
        if list_id in self.lists:
            goals = self.lists[list_id]['goals']
            if 0 <= old_index < len(goals) and 0 <= new_index < len(goals):
                goal = goals.pop(old_index)
                goals.insert(new_index, goal)
                self.save_lists()
    
    def backup_lists(self):
        """Create a backup of the lists file"""
        backup_dir = os.path.join(self.data_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'lists_backup_{timestamp}.json')
        
        try:
            with open(self.lists_file, 'r') as source, open(backup_file, 'w') as target:
                target.write(source.read())
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def restore_from_backup(self, backup_file):
        """Restore lists from a backup file"""
        try:
            with open(backup_file, 'r') as f:
                self.lists = json.load(f)
            self.save_lists()
            return True
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False