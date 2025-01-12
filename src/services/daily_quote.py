import os
import json
import random
from datetime import datetime
from gi.repository import GLib

class DailyQuote:
    """Service for managing daily motivational quotes"""
    
    def __init__(self):
        self.data_dir = os.path.join(GLib.get_user_data_dir(), 'goaltracker')
        os.makedirs(self.data_dir, exist_ok=True)
        self.quotes_file = os.path.join(self.data_dir, 'quotes.json')
        
        # For caching the daily quote
        self.current_quote = None
        self.last_date = None
        
        # Default quote in case everything fails
        self.default_quote = {
            "text": "Set your goals high and don't stop till you get there.",
            "author": "Bo Jackson"
        }
    
    def load_quotes(self):
        """Load quotes from the system or user directory"""
        # Try user directory first
        user_quotes = os.path.join(GLib.get_user_data_dir(), 'goaltracker', 'quotes.json')
        # System directory as fallback
        system_quotes = os.path.join(GLib.get_system_data_dirs()[0], 'goaltracker', 'quotes.json')
        
        # Default quotes collection
        default_quotes = {
            "quotes": [
                self.default_quote,
                {
                    "text": "The future depends on what you do today.",
                    "author": "Mahatma Gandhi"
                },
                {
                    "text": "Don't watch the clock; do what it does. Keep going.",
                    "author": "Sam Levenson"
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
                print("No quotes file found, using default quotes")
                return default_quotes['quotes']
        except Exception as e:
            print(f"Error loading quotes: {e}")
            return default_quotes['quotes']
    
    def get_daily_quote(self):
        """Get the quote for today"""
        today = datetime.now().date()
        
        if self.last_date != today or self.current_quote is None:
            quotes_list = self.load_quotes()
            if not quotes_list:  # If quotes list is empty
                quotes_list = [self.default_quote]
            
            # Use the date as a seed to get the same quote throughout the day
            random.seed(today.strftime("%Y%m%d"))
            self.current_quote = random.choice(quotes_list)
            self.last_date = today
            
        return self.current_quote
    
    def add_quote(self, text, author):
        """Add a new quote to the user's collection"""
        try:
            # Load existing quotes
            quotes = {"quotes": self.load_quotes()}
            
            # Add new quote
            quotes["quotes"].append({
                "text": text,
                "author": author
            })
            
            # Save to user directory
            user_quotes = os.path.join(self.data_dir, 'quotes.json')
            with open(user_quotes, 'w', encoding='utf-8') as f:
                json.dump(quotes, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"Error adding quote: {e}")
            return False
    
    def remove_quote(self, text, author):
        """Remove a quote from the user's collection"""
        try:
            # Load existing quotes
            quotes = {"quotes": self.load_quotes()}
            
            # Remove matching quote
            quotes["quotes"] = [
                q for q in quotes["quotes"]
                if not (q["text"] == text and q["author"] == author)
            ]
            
            # Save to user directory
            user_quotes = os.path.join(self.data_dir, 'quotes.json')
            with open(user_quotes, 'w', encoding='utf-8') as f:
                json.dump(quotes, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"Error removing quote: {e}")
            return False
    
    def get_random_quote(self):
        """Get a random quote (different from daily quote)"""
        quotes_list = self.load_quotes()
        if not quotes_list:
            return self.default_quote
            
        # If we have the daily quote, try to get a different one
        if self.current_quote and len(quotes_list) > 1:
            other_quotes = [q for q in quotes_list if q != self.current_quote]
            return random.choice(other_quotes)
            
        return random.choice(quotes_list)